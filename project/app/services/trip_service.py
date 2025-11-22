from ..cruds.trip_crud import TripCrud
from ..cruds.delivery_crud import DeliveryCrud
from ..cruds.order_crud import OrderCrud
from ..cruds.address_crud import AddressCrud
from ..cruds.box_crud import BoxCrud
from ..cruds.truck_crud import TruckCrud
from ..cruds.depot_crud import DepotCrud
from ..models import Trip, Truck, Depot, Delivery
from ..services.depot_service import DepotService
from ..exception_errors import (
    RangeError,
    StatusError,
    CapacityError,
    BelongError,
    RemainingDeliveriesError,
    SimulateTripError,
)

import time
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import osmnx as ox
import heapq
import matplotlib.pyplot as plt


def pathing_route_dijkstra(G, start, target, weight="length"):
    dist = {node: float("inf") for node in G.nodes()}
    dist[start] = 0
    prev = {}
    pq = [(0, start)]

    while pq:
        current_dist, u = heapq.heappop(pq)

        if u == target:
            path = []
            while u is not None:
                path.append(u)
                u = prev.get(u)
            return current_dist, list(reversed(path))

        if current_dist > dist[u]:
            continue

        for v in G.neighbors(u):
            edge_data = G.get_edge_data(u, v)
            if edge_data is None:
                continue

            w = min(ed.get(weight, 1) for ed in edge_data.values())
            new_dist = current_dist + w

            if new_dist < dist[v]:
                dist[v] = new_dist
                prev[v] = u
                heapq.heappush(pq, (new_dist, v))

    return float("inf"), []


class TripService:
    @staticmethod
    def remaining_deliveries(trip_id):
        TripCrud.read_by_id(trip_id)

        deliveries_list = DeliveryCrud.delivery_by_trip(trip_id)
        remaining_deliveries_list = []
        for delivery in deliveries_list:
            if delivery.delivered_at == None:
                remaining_deliveries_list.append(delivery)

        return remaining_deliveries_list

    @staticmethod
    def define_route(origin_depot, selected_orders):
        if not all(
            (
                order.store.address.city == origin_depot.address.city
                and order.store.address.state == origin_depot.address.state
                and order.store.address.country == origin_depot.address.country
            )
            for order in selected_orders
        ):
            raise RangeError(
                "Addresses out of range — all addresses must be in the same city"
            )

        addresses = []
        addresses.append(AddressCrud.formatted_address(origin_depot.address.id))
        for selected_order in selected_orders:
            addresses.append(AddressCrud.formatted_address(selected_order.address.id))

        area = f"{origin_depot.address.city}, {origin_depot.address.state}, {origin_depot.address.country}"

        geolocator = Nominatim(user_agent="cheaptracker", timeout=20)

        locations = [geolocator.geocode(address) for address in addresses]

        for location, address in zip(locations, addresses):
            if location is None:
                raise ValueError(f"Address not found: {address}")

        G = ox.graph_from_place(area, network_type="drive")

        xs = [loc.longitude for loc in locations]
        ys = [loc.latitude for loc in locations]
        nodes = ox.distance.nearest_nodes(G, xs, ys)

        segment_paths = []
        total_distance = 0
        route_order = [0]
        remaining = list(range(1, len(nodes)))

        while remaining:
            last = route_order[-1]

            candidates = []
            for r in remaining:
                dist, path = pathing_route_dijkstra(G, nodes[last], nodes[r])
                candidates.append((dist, r, path))

            candidates.sort(key=lambda x: x[0])
            chosen_distance, chosen_index, chosen_path = candidates[0]

            route_order.append(chosen_index)
            remaining.remove(chosen_index)
            total_distance += chosen_distance

            segment_paths.append(chosen_path)

        chosen_distance, return_path = pathing_route_dijkstra(
            G, nodes[route_order[-1]], nodes[0]
        )
        segment_paths.append(return_path)
        route_order.append(0)
        total_distance += chosen_distance

        print("\nRoute stop order:")
        for i, idx in enumerate(route_order):
            if i == 0:
                print(f"Departure: {addresses[idx]}")
            else:
                print(f"{i}° stop: {addresses[idx]}")

        total_distance = round(total_distance / 1000, 1)
        print(f"Distance traveled on the trip: {total_distance} km")

        fig, ax = ox.plot_graph(G, node_size=0, show=False, close=False)

        for path in segment_paths:
            ox.plot_graph_route(
                G, path, ax=ax, node_size=0, route_linewidth=3, show=False, close=False
            )

        x = [G.nodes[n]["x"] for n in nodes]
        y = [G.nodes[n]["y"] for n in nodes]
        ax.scatter(x, y, s=120, c="red", zorder=5)

        for stop_number, node_index in enumerate(route_order):
            node = nodes[node_index]
            x = G.nodes[node]["x"]
            y = G.nodes[node]["y"]
            ax.text(
                x,
                y,
                str(stop_number),
                fontsize=11,
                color="yellow",
                weight="bold",
                zorder=10,
            )

        plt.show()

        return route_order, total_distance, fig

    @staticmethod
    def define_trip(depot_id, orders_id_list):
        origin_depot, selected_orders = DepotService.select_orders(
            depot_id, orders_id_list
        )

        cargo_weight_kg = 0
        cargo_volume_m3 = 0

        for order in selected_orders:
            cargo_weight_kg += order.total_weight_kg
            cargo_volume_m3 += order.total_volume_m3

        route_order, total_distance, fig = TripService.define_route(
            origin_depot, selected_orders
        )

        trip = TripCrud.create(
            depot_id=depot_id,
            total_loaded_weight_kg=cargo_weight_kg,
            total_loaded_volume_m3=cargo_volume_m3,
            total_distance_km=total_distance,
        )

        for order in selected_orders:
            order.status = "Sche"
            order.save()

        return trip, route_order, fig

    @staticmethod
    def start_trip(truck_plate, trip_id, depot_id):
        truck = TruckCrud.read_by_plate(truck_plate)
        trip = TripCrud.read_by_id(trip_id)
        depot = DepotCrud.read_by_id(depot_id)

        if truck.is_active == True:
            raise StatusError("Truck already being used")

        if not (trip.total_loaded_weight_kg <= truck.max_payload_kg) and (
            trip.total_loaded_volume_m3 <= truck.cargo_volume_m3
        ):
            raise CapacityError(
                "The selected orders exceed the chosen truck's capacity"
            )

        if trip.origin_depot != depot:
            raise BelongError("This trip does not correspond to this depot")

        if trip.status != "Plan":
            raise StatusError("The trip status must be planned to be started")

        match (truck.euro):
            case 5:
                carbon_kg_co2 = trip.total_distance_km * 0.83
            case 6:
                carbon_kg_co2 = trip.total_distance_km * 0.75

        orders = OrderCrud.read_orders_by_trip(trip_id)
        for order in orders:
            order.status = "Ship"
            order.save()
            DeliveryCrud.create(
                trip_id=trip.id, store_id=order.store.id, order_id=order.id
            )

        trip.truck = truck
        trip.carbon_kg_co2 = carbon_kg_co2
        trip.departure_date = datetime.now()
        trip.status = "InTr"
        trip.save()

        truck.is_active = True
        truck.total_trips += 1
        truck.save()

        return trip

    @staticmethod
    def end_trip(trip_id, depot_id):
        trip = TripCrud.read_by_id(trip_id)
        truck = TruckCrud.read_by_plate(trip.truck.plate)
        depot = DepotCrud.read_by_id(depot_id)

        if trip.origin_depot != depot:
            raise BelongError("This trip does not belong to this depot")

        if trip.status != "InTr":
            raise StatusError("The trip status must be in transit to be ended")

        remaining_deliveries = TripService.remaining_deliveries(trip_id)
        if remaining_deliveries:
            raise RemainingDeliveriesError(
                "The trip must have all deliveries completed to be ended"
            )

        orders = OrderCrud.read_orders_by_trip(trip_id)
        for order in orders:
            boxes = BoxCrud.read_boxes_by_order(order_id=order.id)
            for box in boxes:
                box.was_delivered = True
                box.save()
            order.status = "Deli"
            order.save()

        trip.arrival_date = datetime.now()
        trip.status = "Comp"
        trip.save()

        truck.is_active = False
        truck.save()

        return trip

    @staticmethod
    def cancel_trip(trip_id, depot_id):
        trip = TripCrud.read_by_id(trip_id)
        depot = DepotCrud.read_by_id(depot_id)

        if trip.origin_depot != depot:
            raise BelongError("This trip does not correspond to this depot")

        if trip.status != "Plan":
            raise StatusError("The trip status must be planned to be calceled")

        orders = OrderCrud.read_orders_by_trip(trip_id)
        for order in orders:
            order.status = "Pend"
            order.save()

        trip.status = "Canc"
        trip.save()

    @staticmethod
    def confirm_delivery(trip_id, truck_plate, delivery_id):
        trip = TripCrud.read_by_id(trip_id)
        truck = TruckCrud.read_by_plate(truck_plate)
        delivery = DeliveryCrud.read_by_id(delivery_id)

        if trip.status != "InTr":
            raise StatusError("Trip status must be in transit to confirm a delivery")

        if trip.truck != truck:
            raise BelongError("This truck does not belong on this trip")

        if delivery.trip != trip:
            raise BelongError("This delivery does not belong on this trip")

        delivery.delivered_at = datetime.now()
        delivery.save()

    @staticmethod
    def simulate_trip(trip_id, truck_plate, traffic_status):
        trip = TripCrud.read_by_id(trip_id)
        truck = TruckCrud.read_by_plate(truck_plate)

        if traffic_status not in ["light", "medium", "heavy"]:
            raise StatusError("Traffic Status must be: light, medium or heavy.")

        match (traffic_status):
            case "light":
                average_speed = 60
            case "medium":
                average_speed = 40
            case "heavy":
                average_speed = 20

        departure_date = datetime.now()
        full_time_route = trip.total_distance_km / average_speed

        days = full_time_route // 24
        hours = int(full_time_route - (days * 24))
        minutes = round((full_time_route % 1) * 60)

        arrival_date = departure_date + timedelta(
            days=days, hours=hours, minutes=minutes
        )

        match (truck.euro):
            case 5:
                carbon_kg_co2 = trip.total_distance_km * 0.83
            case 6:
                carbon_kg_co2 = trip.total_distance_km * 0.75

        print(f"Simulating Trip ID:{trip.id} with Truck Plate: {truck.plate}\n\n")
        print(f"Total distance traveled on the Trip:\n{trip.total_distance_km} kms\n\n")
        print(
            f"Departure:\n{departure_date.month} {departure_date.day} at {departure_date.hour}:{departure_date.minute}\n\n"
        )
        print(
            f"Arrival:\n{arrival_date.month} {arrival_date.day} at {arrival_date.hour}:{arrival_date.minute}\n\n"
        )
        print(
            f"Travel time:\n{days} day(s), {hours} hour(s) and {minutes} minute(s)\n\n"
        )
        print(f"Carbon emission:\n{carbon_kg_co2} kgCO2\n")

        simulation = {
            "trip_id": trip.id,
            "truck_plate": truck.plate,
            "trip_total_distance": trip.total_distance_km,
            "departure_date_month": departure_date.month,
            "departure_date_day": departure_date.day,
            "departure_date_hour": departure_date.hour,
            "departure_date_minute": departure_date.minute,
            "arrival_date_month": arrival_date.month,
            "arrival_date_day": arrival_date.day,
            "arrival_date_hour": arrival_date.hour,
            "arrival_date_minute": arrival_date.minute,
            "trip_days": days,
            "trip_hours": hours,
            "trip_minutes": minutes,
            "trip_carbon_emission": carbon_kg_co2,
        }

        return simulation

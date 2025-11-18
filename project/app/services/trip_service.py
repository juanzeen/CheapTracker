from ..cruds.trip_crud import TripCrud
from ..cruds.delivery_crud import DeliveryCrud
from ..cruds.order_crud import OrderCrud
from ..cruds.address_crud import AddressCrud
from ..cruds.box_crud import BoxCrud
from ..models import Trip, Truck, Depot, Delivery
from ..services.depot_service import DepotService

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
        try:
            Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            raise ValueError("Trip not found")

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
            raise ValueError(
                "Addresses out of range — all addresses must be in the same area"
            )

        addresses = []
        addresses.append(AddressCrud.formatted_address(origin_depot.address.id))
        for selected_order in selected_orders:
            addresses.append(AddressCrud.formatted_address(selected_order.address.id))

        area = f"{origin_depot.address.city}, {origin_depot.address.state}, {origin_depot.address.country}"

        geolocator = Nominatim(user_agent="cheaptracker")

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
    def define_trip(truck_plate, depot_id, orders_id_list, departure_date):
        try:
            truck = Truck.objects.get(plate=truck_plate)
        except Truck.DoesNotExist:
            raise ValueError("Incorrect Plate or Truck not found")

        if truck.is_active == True:
            raise ValueError("This Truck is already on a trip")

        origin_depot, selected_orders = DepotService.select_orders(
            depot_id, orders_id_list
        )

        cargo_weight_kg = 0
        cargo_volume_m3 = 0

        for order in selected_orders:
            cargo_weight_kg += order.total_weight_kg
            cargo_volume_m3 += order.total_volume_m3

        if not (cargo_weight_kg <= truck.max_payload_kg) and (
            cargo_volume_m3 <= truck.cargo_volume_m3
        ):
            raise ValueError("The selected orders exceed the chosen truck's capacity")

        route_order, total_distance, fig = TripService.define_route(
            origin_depot, selected_orders
        )

        match (truck.euro):
            case 5:
                carbon_kg_co2 = total_distance * 0.83
            case 6:
                carbon_kg_co2 = total_distance * 0.75

        trip = TripCrud.create(
            truck_id=truck.id,
            depot_id=depot_id,
            departure_date=departure_date,
            total_loaded_weight_kg=cargo_weight_kg,
            total_loaded_volume_m3=cargo_volume_m3,
            total_distance_km=total_distance,
            carbon_kg_co2=carbon_kg_co2,
        )

        for order in selected_orders:
            order.status = "Sche"
            order.save()
            DeliveryCrud.create(
                trip_id=trip.id, store_id=order.store.id, order_id=order.id
            )

        return trip, route_order, fig

    @staticmethod
    def start_trip(trip_id, depot_id):
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            raise ValueError("Trip not found")

        try:
            depot = Depot.objects.get(id=depot_id)
        except Depot.DoesNotExist:
            raise ValueError("Depot not found")

        if Trip.origin_depot != depot:
            raise ValueError("This trip does not correspond to this depot")

        if trip.status != "Plan":
            raise ValueError("The trip must be planned to be started")

        orders = OrderCrud.read_orders_by_trip(trip_id)
        for order in orders:
            order.status = "Ship"
            order.save()

        trip.departure_date = datetime.now()
        trip.status = "InTr"
        trip.save()

        return trip

    @staticmethod
    def end_trip(trip_id, depot_id):
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            raise ValueError("Trip not found")

        try:
            depot = Depot.objects.get(id=depot_id)
        except Depot.DoesNotExist:
            raise ValueError("Depot not found")

        if Trip.origin_depot != depot:
            raise ValueError("This trip does not correspond to this depot")

        if trip.status != "InTr":
            raise ValueError("The trip must be in transit to be ended")

        deliveries = DeliveryCrud.delivery_by_trip(trip_id=trip_id)
        if not all(delivery.delivered_at for delivery in deliveries):
            raise ValueError(
                "A trip must have all deliveries completed in order to be ended"
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

        return trip

    @staticmethod
    def cancel_trip(trip_id, depot_id):
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            raise ValueError("Trip not found")

        try:
            depot = Depot.objects.get(id=depot_id)
        except Depot.DoesNotExist:
            raise ValueError("Depot not found")

        if Trip.origin_depot != depot:
            raise ValueError("This trip does not correspond to this depot")

        if trip.status != "Plan":
            raise ValueError("The trip must be planned to be calceled")

        orders = OrderCrud.read_orders_by_trip(trip_id)
        for order in orders:
            order.status = "Pend"
            order.save()

        deliveries = DeliveryCrud.delivery_by_trip(trip_id=trip_id)
        for delivery in deliveries:
            DeliveryCrud.delete(delivery.id)

        trip.status = "Canc"
        trip.save()

    @staticmethod
    def confirm_delivery(trip_id, truck_plate, delivery_id):
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            raise ValueError("Trip not found")

        try:
            truck = Truck.objects.get(plate=truck_plate)
        except Truck.DoesNotExist:
            raise ValueError("Incorrect Plate or Truck not found")

        try:
            delivery = Delivery.objects.get(id=delivery_id)
        except Delivery.DoesNotExist:
            raise ValueError("Delivery not found")

        if trip.status != "InTr":
            raise ValueError("Trip must be in transit to confirm a delivery")

        if trip.truck != truck:
            raise ValueError("This truck is not making this trip")

        if delivery.trip != trip:
            raise ValueError("This delivery does not belong on this trip")

        delivery.delivered_at = datetime.now()
        delivery.save()

    """@staticmethod
    def simulate_trip(trip_id, traffic_status):
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            raise ValueError("Trip not found")

        if traffic_status not in ['light', 'medium', 'heavy']:
            raise ValueError('Traffic Status must be: light, medium or heavy.')

        match(traffic_status):
            case 'light':
                average_speed = 60
            case 'medium':
                average_speed = 40
            case 'heavy':
                average_speed = 20

        # simulation arrival time
        full_time_route = trip.total_distance_km/average_speed
        hours = int(full_time_route)
        minutes = round((full_time_route % 1) * 60)

        arrival_date = trip.departure_date + timedelta(hours=hours, minutes=minutes)

        trip.arrival_date = arrival_date
        trip.save()

        while True:
            now = datetime.now()
            if now >= arrival_date:
                break

            time.sleep(60)

        trip_deliveries = DeliveryCrud.delivery_by_trip(trip_id=trip_id)
        for delivery in trip_deliveries:
            delivery.delivered_at = now
            delivery.save()"""

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
)

from datetime import timedelta
from geopy.geocoders import Nominatim
from django.utils import timezone
from django.conf import settings
import osmnx as ox
import heapq
import matplotlib
import matplotlib.pyplot as plt
from django.forms.models import model_to_dict
import os
import folium


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
                remaining_deliveries_list.append(model_to_dict(delivery))

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

        address_objects = [origin_depot.address] + [
            order.store.address for order in selected_orders
        ]

        area = f"{origin_depot.address.city}, {origin_depot.address.state}, {origin_depot.address.country}"

        matplotlib.use("Agg")
        print(f"1. Geocoding addresses in {area}...")
        geolocator = Nominatim(user_agent="cheaptracker", timeout=20)

        locations = []
        addresses = []  # For display purposes

        for addr in address_objects:
            # List of queries from most specific to least specific
            queries = [
                f"{addr.street}, {addr.number}, {addr.neighborhood}, {addr.city}, {addr.state}, {addr.country}",
                f"{addr.street}, {addr.number}, {addr.city}, {addr.state}, {addr.country}",
                f"{addr.street}, {addr.city}, {addr.state}, {addr.country}",
                f"{addr.neighborhood}, {addr.city}, {addr.state}, {addr.country}",  # Fallback to neighborhood center
            ]

            loc = None
            matched_query = ""

            for q in queries:
                try:
                    loc = geolocator.geocode(q)
                    if loc:
                        matched_query = q
                        break
                except Exception as e:
                    print(f"   [WARN] Error geocoding '{q}': {e}")
                    continue

            if loc:
                locations.append(loc)
                # Reconstruct the full formatted address for display consistency
                full_display = f"{addr.street}, {addr.number}, {addr.neighborhood}, {addr.city}, {addr.state}, {addr.cep}, {addr.country}"
                addresses.append(full_display)
                print(
                    f"   [OK] Address found: {matched_query} (Original: {addr.street}, {addr.number})"
                )
            else:
                raise ValueError(
                    f"   [ERROR] Address not found after retries: {addr.street}, {addr.number}"
                )

        print("2. Downloading the city map (this may be slow the first time)...")
        G = ox.graph_from_place(area, network_type="drive")

        xs = [loc.longitude for loc in locations]
        ys = [loc.latitude for loc in locations]
        nodes = ox.distance.nearest_nodes(G, xs, ys)

        segment_paths = []
        total_distance = 0
        route_order = [0]
        remaining = list(range(1, len(nodes)))

        print("3. Calculating the best route (Nearest Neighbor - Dijkstra)...")
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

        print("   Calculating the return to the departure depot...")
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
            elif i == len(route_order) - 1:
                print(f"Arrival (Return): {addresses[idx]}")
            else:
                print(f"{i}° Stop: {addresses[idx]}")

        total_distance = round(total_distance / 1000, 1)
        print(f"Distance traveled on the trip: {total_distance} km")

        fig, ax = ox.plot_graph(G, node_size=0, show=False, close=False)

        colors = ["cyan", "orange", "lime", "magenta", "yellow", "white"]
        for i, path in enumerate(segment_paths):
            c = colors[i % len(colors)]
            ox.plot_graph_route(
                G,
                path,
                ax=ax,
                node_size=0,
                route_linewidth=3,
                route_color=c,
                show=False,
                close=False,
            )

        x = [G.nodes[n]["x"] for n in nodes]
        y = [G.nodes[n]["y"] for n in nodes]
        ax.scatter(x, y, s=120, c="red", zorder=5, edgecolors="white")

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

        node_lats = [G.nodes[n]["y"] for n in nodes]
        node_lons = [G.nodes[n]["x"] for n in nodes]
        center_lat = sum(node_lats) / len(node_lats)
        center_lon = sum(node_lons) / len(node_lons)

        graph_map = folium.Map(location=[center_lat, center_lon], zoom_start=13)

        folium_colors = [
            "#00FFFF",
            "#FFA500",
            "#00FF00",
            "#FF00FF",
            "#FFFF00",
            "#0000FF",
        ]

        for i, path in enumerate(segment_paths):
            c = folium_colors[i % len(folium_colors)]
            # Extract coordinates for the path
            route_coords = [(G.nodes[node]["y"], G.nodes[node]["x"]) for node in path]

            folium.PolyLine(
                route_coords, color=c, weight=5, opacity=0.7
            ).add_to(graph_map)

        for i, idx in enumerate(route_order):
            node = nodes[idx]
            lat = G.nodes[node]["y"]
            lon = G.nodes[node]["x"]

            if i == 0:
                folium.Marker(
                    [lat, lon],
                    popup=f"Origem/Fim: {addresses[idx]}",
                    icon=folium.Icon(color="red", icon="home"),
                ).add_to(graph_map)
            elif i == len(route_order) - 1:
                pass
            else:
                folium.Marker(
                    [lat, lon],
                    popup=f"Parada {i}: {addresses[idx]}",
                    icon=folium.Icon(color="blue", icon="info-sign"),
                ).add_to(graph_map)

        return route_order, total_distance, fig, graph_map

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

        route_order, total_distance, fig, graph_map = TripService.define_route(
            origin_depot, selected_orders
        )

        trip = TripCrud.create(
            depot_id=depot_id,
            total_loaded_weight_kg=cargo_weight_kg,
            total_loaded_volume_m3=cargo_volume_m3,
            total_distance_km=total_distance,
        )

        # Construct the full path to save the image in the static directory
        image_path = os.path.join(settings.BASE_DIR, "static", "routes")
        os.makedirs(image_path, exist_ok=True)  # Ensure the directory exists
        file_path = os.path.join(image_path, f"trip_{trip.id}.png")
        fig.savefig(file_path, dpi=300)

        # Save HTML map
        html_path = os.path.join(image_path, f"trip_{trip.id}.html")
        graph_map.save(html_path)

        for order in selected_orders:
            order.status = "Sche"
            order.trip = trip
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
                f"The selected orders exceed the chosen truck's capacity in {trip.total_loaded_weight_kg - truck.max_payload_kg}kg and {trip.total_loaded_volume_m3 - truck.cargo_volume_m3}m3"
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
        trip.departure_date = timezone.now()
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

        trip.arrival_date = timezone.now()
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
            raise StatusError("The trip status must be planned to be canceled")

        orders = OrderCrud.read_orders_by_trip(trip_id)
        for order in orders:
            order.status = "Pend"
            order.trip = None
            order.save()

        trip.status = "Canc"
        trip.save()

    @staticmethod
    def confirm_delivery(trip_id, truck_plate, delivery_id):
        trip = TripCrud.read_by_id(trip_id)
        truck = TruckCrud.read_by_plate(truck_plate)
        delivery = DeliveryCrud.read_by_id(delivery_id)
        order = OrderCrud.read_by_id(delivery.order.id)

        if trip.status != "InTr":
            raise StatusError("Trip status must be in transit to confirm a delivery")

        if trip.truck != truck:
            raise BelongError("This truck does not belong on this trip")

        if delivery.trip != trip:
            raise BelongError("This delivery does not belong on this trip")

        delivery.delivered_at = timezone.now()
        delivery.save()
        order.status = "Deli"
        order.save()

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

        departure_date = timezone.now()
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

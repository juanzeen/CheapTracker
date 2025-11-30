import random
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from app.models import (
    Usuario,
    UserRoles,
    Address,
    Store,
    Depot,
    Carrier,
    Truck,
    Trip,
    TripStatus,
    Order,
    OrderStatus,
    Box,
    BoxSize,
    Delivery,
)


class Command(BaseCommand):
    help = "Seeds the database with rich initial data for exploratory testing."

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write("Deleting old data...")
        models = [
            Delivery,
            Box,
            Order,
            Trip,
            Truck,
            Carrier,
            Depot,
            Store,
            Address,
            Usuario,
        ]
        for m in models:
            m.objects.all().delete()
        self.stdout.write(self.style.SUCCESS("Old data deleted."))

        self.stdout.write("Creating new data...")

        # --- Users ---
        # Admin
        admin, _ = Usuario.objects.get_or_create(
            email="admin@cheaper.com",
            defaults={
                "name": "Admin User",
                "age": 40,
                "role": UserRoles.ADM,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin.set_password("admin123")
        admin.save()

        # Manager
        manager_user, _ = Usuario.objects.get_or_create(
            email="manager@depot.com",
            defaults={"name": "John Depot", "age": 45, "role": UserRoles.MAN},
        )
        manager_user.set_password("manager123")
        manager_user.save()

        # Shopkeepers
        shopkeeper_user1, _ = Usuario.objects.get_or_create(
            email="shop1@store.com",
            defaults={"name": "Ana Store", "age": 33, "role": UserRoles.SHOP},
        )
        shopkeeper_user1.set_password("shop123")
        shopkeeper_user1.save()

        shopkeeper_user2, _ = Usuario.objects.get_or_create(
            email="shop2@store.com",
            defaults={"name": "Carlos Market", "age": 29, "role": UserRoles.SHOP},
        )
        shopkeeper_user2.set_password("shop123")
        shopkeeper_user2.save()

        # Carrier
        carrier_user, _ = Usuario.objects.get_or_create(
            email="carrier@trans.com",
            defaults={"name": "Peter Carrier", "age": 50, "role": UserRoles.CARR},
        )
        carrier_user.set_password("carrier123")
        carrier_user.save()

        self.stdout.write(self.style.SUCCESS(f"Created Users."))

        # --- Addresses ---
        addresses = []
        for i in range(10):
            address = Address.objects.create(
                street=f"Rua {i+1}",
                number=f"{i * 100 + 10}",
                complement=f"Apto {i}" if i % 3 == 0 else "",
                neighborhood="Centro" if i < 5 else "Zona Norte",
                city="Cidade Exemplo",
                state="EX",
                cep=f"12345-00{i}",
            )
            addresses.append(address)
        self.stdout.write(self.style.SUCCESS(f"Created Addresses."))

        # --- Entities (Store, Depot, Carrier) ---
        # Contacts must be 11 digits
        store1 = Store.objects.create(
            user=shopkeeper_user1,
            name="Loja Matriz",
            address=addresses[0],
            contact="11987654321",
            registration="11111111-1",
        )

        store2 = Store.objects.create(
            user=shopkeeper_user2,
            name="Supermercado B",
            address=addresses[1],
            contact="11912345678",
            registration="55555555-5",
        )

        depot = Depot.objects.create(
            user=manager_user,
            name="Depósito Central",
            address=addresses[2],
            contact="11888888888",
            registration="22222222-2",
        )

        carrier = Carrier.objects.create(
            user=carrier_user,
            name="Transportadora Rápida",
            address=addresses[3],
            contact="11777777777",
            registration="33333333-3",
        )
        self.stdout.write(self.style.SUCCESS(f"Created Stores, Depot, Carrier."))

        # --- Trucks ---
        trucks = []
        for i in range(5):
            truck = Truck.objects.create(
                carrier=carrier,
                plate=f"TRK0{i+1}A",
                axles_count=random.choice([2, 3, 4, 5]),
                cargo_length=10.5,
                cargo_width=2.5,
                cargo_height=3.0,
                max_payload_kg=15000,
                euro=random.randint(4, 6),
                is_active=True,
                release_year=2020 + i,
                total_trips=0,
                max_fuel_capacity=400,
            )
            trucks.append(truck)
        self.stdout.write(self.style.SUCCESS(f"Created Trucks."))

        # --- Helper to create order/boxes ---
        def create_order_with_boxes(
            store_obj, trip_obj, status_enum, scheduled_bool=True
        ):
            # If status is PEND, trip might be None
            order_obj = Order.objects.create(
                store=store_obj,
                trip=trip_obj,
                status=status_enum,
                total_weight_kg=0,
                total_volume_m3=0,
                total_boxes=0,
                scheduled=scheduled_bool,
            )

            num_boxes = random.randint(1, 4)
            current_weight = 0.0
            current_volume = 0.0

            is_delivered = status_enum == OrderStatus.DELI

            for _ in range(num_boxes):
                box_choice = random.choice(BoxSize.choices)
                size_code = box_choice[0]

                if size_code == BoxSize.SMA:
                    l, w, h, wgt = 0.4, 0.4, 0.4, 5.0
                elif size_code == BoxSize.MED:
                    l, w, h, wgt = 0.6, 0.6, 0.6, 15.0
                elif size_code == BoxSize.BIG:
                    l, w, h, wgt = 1.0, 0.8, 0.8, 30.0
                elif size_code == BoxSize.LAR:
                    l, w, h, wgt = 1.2, 1.0, 1.0, 50.0
                else:  # Custom
                    l, w, h, wgt = 1.5, 1.0, 1.0, 60.0

                box_obj = Box.objects.create(
                    order=order_obj,
                    size=size_code,
                    length=l,
                    width=w,
                    height=h,
                    payload_kg=wgt,
                    was_delivered=is_delivered,
                )
                current_weight += wgt
                current_volume += box_obj.volume_m3

            order_obj.total_weight_kg = round(current_weight, 2)
            order_obj.total_volume_m3 = round(current_volume, 3)
            order_obj.total_boxes = num_boxes
            order_obj.save()

            # Create Delivery Record
            if trip_obj:
                d_at = timezone.now() if is_delivered else None
                Delivery.objects.create(
                    trip=trip_obj, store=store_obj, order=order_obj, delivered_at=d_at
                )

            return order_obj

        # --- Trips & Orders ---

        # 1. Trip Planned (Standard case)
        trip_planned = Trip.objects.create(
            truck=trucks[0],
            origin_depot=depot,
            status=TripStatus.PLANN,
            total_loaded_weight_kg=0,
            total_loaded_volume_m3=0,
        )
        # Add orders to planned trip
        for _ in range(3):
            create_order_with_boxes(store1, trip_planned, OrderStatus.SCHE)
        for _ in range(2):
            create_order_with_boxes(store2, trip_planned, OrderStatus.SCHE)

        # 2. Trip In Transit
        trip_transit = Trip.objects.create(
            truck=trucks[1],
            origin_depot=depot,
            status=TripStatus.IN_TR,
            departure_date=timezone.now() - timedelta(hours=4),
            total_loaded_weight_kg=0,
            total_loaded_volume_m3=0,
        )
        # Add orders (Shipped)
        for _ in range(4):
            create_order_with_boxes(store1, trip_transit, OrderStatus.SHIP)

        # 3. Trip Completed
        trip_completed = Trip.objects.create(
            truck=trucks[2],
            origin_depot=depot,
            status=TripStatus.COMP,
            departure_date=timezone.now() - timedelta(days=1, hours=5),
            arrival_date=timezone.now() - timedelta(days=1),
            total_distance_km=350.5,
            carbon_kg_co2=150.2,
            total_loaded_weight_kg=0,
            total_loaded_volume_m3=0,
        )
        # Add orders (Delivered)
        for _ in range(3):
            create_order_with_boxes(store2, trip_completed, OrderStatus.DELI)
        # Maybe one order was cancelled/returned on this trip?
        # create_order_with_boxes(store1, trip_completed, OrderStatus.CANC) # Optional complexity

        # 4. Trip Cancelled
        trip_cancelled = Trip.objects.create(
            truck=trucks[3],
            origin_depot=depot,
            status=TripStatus.CANC,
            total_loaded_weight_kg=0,
            total_loaded_volume_m3=0,
        )
        # Orders here might be Cancelled or stuck in Scheduled? Let's say Cancelled.
        create_order_with_boxes(store1, trip_cancelled, OrderStatus.CANC)

        # 5. Pending Orders (No Trip assigned)
        # These represent orders just placed by the store
        for _ in range(5):
            # trip=None
            create_order_with_boxes(store1, None, OrderStatus.PEND)
            create_order_with_boxes(store2, None, OrderStatus.PEND)

        # --- Update Trip Totals ---
        all_trips = [trip_planned, trip_transit, trip_completed, trip_cancelled]
        for t in all_trips:
            t_orders = Order.objects.filter(trip=t)
            t.total_loaded_weight_kg = sum(o.total_weight_kg for o in t_orders)
            t.total_loaded_volume_m3 = sum(o.total_volume_m3 for o in t_orders)
            t.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Updated Trip {t.id} [{t.get_status_display()}]: {len(t_orders)} orders."
                )
            )

        self.stdout.write(
            self.style.SUCCESS("Database seeded successfully with comprehensive data!")
        )

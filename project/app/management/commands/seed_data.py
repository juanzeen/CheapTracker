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

        shopkeeper_user3, _ = Usuario.objects.get_or_create(
            email="shop3@store.com",
            defaults={"name": "Lurdes Modas", "age": 56, "role": UserRoles.SHOP},
        )
        shopkeeper_user3.set_password("shop123")
        shopkeeper_user3.save()

        shopkeeper_user4, _ = Usuario.objects.get_or_create(
            email="shop4@store.com",
            defaults={"name": "Juliana Presentes", "age": 22, "role": UserRoles.SHOP},
        )
        shopkeeper_user4.set_password("shop123")
        shopkeeper_user4.save()

        shopkeeper_user5, _ = Usuario.objects.get_or_create(
            email="shop5@store.com",
            defaults={"name": "Miguel Eletro", "age": 43, "role": UserRoles.SHOP},
        )
        shopkeeper_user5.set_password("shop123")
        shopkeeper_user5.save()

        # Carrier
        carrier_user, _ = Usuario.objects.get_or_create(
            email="carrier@trans.com",
            defaults={"name": "Peter Carrier", "age": 50, "role": UserRoles.CARR},
        )
        carrier_user.set_password("carrier123")
        carrier_user.save()

        self.stdout.write(self.style.SUCCESS(f"Created Users."))

        # --- Addresses (Real Addresses in Campos dos Goytacazes) ---
        real_addresses_data = [
            {
                "street": "Avenida Pelinca",
                "number": "100",
                "neighborhood": "Pelinca",
                "cep": "28035-053",
            },
            {
                "street": "Rua Tenente Coronel Cardoso",
                "number": "50",
                "neighborhood": "Centro",
                "cep": "28035-042",
            },
            {
                "street": "Avenida 28 de Março",
                "number": "450",
                "neighborhood": "Centro",
                "cep": "28020-740",
            },
            {
                "street": "Rua Barão da Lagoa Dourada",
                "number": "85",
                "neighborhood": "Pelinca",
                "cep": "28035-210",
            },
            {
                "street": "Rua Conselheiro Otaviano",
                "number": "20",
                "neighborhood": "Centro",
                "cep": "28010-140",
            },
            {
                "street": "Rua Treze de Maio",
                "number": "60",
                "neighborhood": "Centro",
                "cep": "28010-260",
            },
            {
                "street": "Avenida Alberto Torres",
                "number": "330",
                "neighborhood": "Centro",
                "cep": "28035-581",
            },
            {
                "street": "Rua Doutor Siqueira",
                "number": "115",
                "neighborhood": "Parque Tamandaré",
                "cep": "28035-150",
            },
            {
                "street": "Avenida Nilo Peçanha",
                "number": "200",
                "neighborhood": "Parque Santo Amaro",
                "cep": "28030-035",
            },
            {
                "street": "Rua Voluntários da Pátria",
                "number": "90",
                "neighborhood": "Pelinca",
                "cep": "28035-260",
            },
            {
                "street": "Rua Saldanha Marinho",
                "number": "45",
                "neighborhood": "Centro",
                "cep": "28010-220",
            },
            {
                "street": "Rua Santos Dumont",
                "number": "30",
                "neighborhood": "Centro",
                "cep": "28010-230",
            },
            {
                "street": "Rua Ipiranga",
                "number": "75",
                "neighborhood": "Centro",
                "cep": "28010-250",
            },
            {
                "street": "Rua Marechal Floriano",
                "number": "55",
                "neighborhood": "Centro",
                "cep": "28010-180",
            },
            {
                "street": "Avenida José Alves de Azevedo",
                "number": "500",
                "neighborhood": "Centro",
                "cep": "28010-300",
            },
            {
                "street": "Rua Ouvidor",
                "number": "40",
                "neighborhood": "Centro",
                "cep": "28010-160",
            },
            {
                "street": "Rua Governador Teotônio Ferreira",
                "number": "80",
                "neighborhood": "Centro",
                "cep": "28010-190",
            },
            {
                "street": "Rua Carlos de Lacerda",
                "number": "25",
                "neighborhood": "Centro",
                "cep": "28010-130",
            },
            {
                "street": "Avenida Arthur Bernardes",
                "number": "600",
                "neighborhood": "Parque Rosário",
                "cep": "28027-000",
            },
            {
                "street": "Rua Ricardo Quitete",
                "number": "150",
                "neighborhood": "Jockey Club",
                "cep": "28020-250",
            },
            {
                "street": "Avenida Presidente Kennedy",
                "number": "850",
                "neighborhood": "Jockey Club",
                "cep": "28020-010",
            },
            {
                "street": "Rua Doutor Beda",
                "number": "120",
                "neighborhood": "Parque Rosário",
                "cep": "28027-110",
            },
            {
                "street": "Rua dos Goitacazes",
                "number": "300",
                "neighborhood": "Centro",
                "cep": "28010-500",
            },
            {
                "street": "Avenida XV de Novembro",
                "number": "750",
                "neighborhood": "Centro",
                "cep": "28035-100",
            },
            {
                "street": "Rua Barão de Miracema",
                "number": "180",
                "neighborhood": "Centro",
                "cep": "28035-300",
            },
            {
                "street": "Rua Salvador Corrêa",
                "number": "95",
                "neighborhood": "Centro",
                "cep": "28035-310",
            },
            {
                "street": "Rua Alvarenga Filho",
                "number": "65",
                "neighborhood": "Centro",
                "cep": "28010-120",
            },
        ]

        addresses = []
        for i, addr_data in enumerate(real_addresses_data):
            address = Address.objects.create(
                street=addr_data["street"],
                number=addr_data["number"],
                complement=f"Loja {i+1}" if i % 2 == 0 else "",
                neighborhood=addr_data["neighborhood"],
                city="Campos dos Goytacazes",
                state="RJ",
                cep=addr_data["cep"],
            )
            addresses.append(address)
        self.stdout.write(
            self.style.SUCCESS(f"Created {len(addresses)} Real Addresses.")
        )

        # --- Entities (Store, Depot, Carrier) ---
        # Assigning real addresses to entities
        store1 = Store.objects.create(
            user=shopkeeper_user1,
            name="Loja Pelinca",
            address=addresses[0],  # Av Pelinca
            contact="11987654321",
            registration="11111111-1",
        )

        store2 = Store.objects.create(
            user=shopkeeper_user2,
            name="Supermercado Centro",
            address=addresses[2],  # Av 28 de Marco
            contact="11912345678",
            registration="55555555-5",
        )

        store3 = Store.objects.create(
            user=shopkeeper_user3,
            name="Lurdes Modas",
            address=addresses[5],  # Rua Treze de Maio
            contact="11934567890",
            registration="66666666-6",
        )

        store4 = Store.objects.create(
            user=shopkeeper_user4,
            name="Juliana Presentes",
            address=addresses[3],  # Rua Barão da Lagoa Dourada
            contact="11945678901",
            registration="77777777-7",
        )

        store5 = Store.objects.create(
            user=shopkeeper_user5,
            name="Miguel Eletro",
            address=addresses[21],  # Rua Doutor Beda
            contact="11956789012",
            registration="88888888-8",
        )

        depot = Depot.objects.create(
            user=manager_user,
            name="Depósito Jockey",
            address=addresses[19],  # Ricardo Quitete (Jockey)
            contact="11888888888",
            registration="22222222-2",
        )

        carrier = Carrier.objects.create(
            user=carrier_user,
            name="Transportadora Goytacaz",
            address=addresses[8],  # Nilo Pecanha
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
        def create_order_with_boxes(store_obj, trip_obj, status_enum):
            # If status is PEND, trip might be None
            order_obj = Order.objects.create(
                store=store_obj,
                trip=trip_obj,
                status=status_enum,
                total_weight_kg=0,
                total_volume_m3=0,
                total_boxes=0,
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

        # --- Trips & Orders --- Removed to prevent automatic trip generation.

        # 5. Pending Orders (No Trip assigned)
        # These represent orders just placed by the store
        for _ in range(2):
            # trip=None
            create_order_with_boxes(store1, None, OrderStatus.PEND)
            create_order_with_boxes(store2, None, OrderStatus.PEND)
            create_order_with_boxes(store3, None, OrderStatus.PEND)
            create_order_with_boxes(store4, None, OrderStatus.PEND)
            create_order_with_boxes(store5, None, OrderStatus.PEND)

        self.stdout.write(
            self.style.SUCCESS("Database seeded successfully with comprehensive data!")
        )


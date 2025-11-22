import json
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from app.cruds.user_crud import UserCrud
from app.cruds.address_crud import AddressCrud
from app.cruds.store_crud import StoreCrud
from app.cruds.depot_crud import DepotCrud
from app.cruds.carrier_crud import CarrierCrud
from app.cruds.truck_crud import TruckCrud
from app.cruds.order_crud import OrderCrud
from app.cruds.trip_crud import TripCrud
from app.cruds.box_crud import BoxCrud
from app.cruds.delivery_crud import DeliveryCrud
from app.exception_errors import UserRoleError, UpdateError, BelongError, DeleteError


class BasicUserCrudTest(TestCase):
    "Tests to check users CRUD"

    def setUp(self):
        UserCrud.create(
            role="Shop",
            name="User Test",
            age=20,
            email="emaildeexemplo@gmail.com",
            password="8charminpass",
        )
        return super().setUp()

    def test_create_user_and_get_by_email(self):
        """Testing if the users has been created correctly"""
        UserCrud.create(
            role="Shop",
            name="User Test",
            age=20,
            email="testedecriacao@gmail.com",
            password="8charminpass",
        )
        user = UserCrud.read_by_email("testedecriacao@gmail.com")
        self.assertEqual(user.name, "User Test")

    def test_retriver_users(self):
        """Testing if the user has been retrieved by user crud"""
        users = UserCrud.read()
        self.assertGreater(len(users), 0)

    def test_update_user(self):
        """Testing if the user has been updated by user crud"""
        user = UserCrud.read_by_email("emaildeexemplo@gmail.com")
        updatedUser = UserCrud.update(user.id, name="User Test With Changes", age=22)
        self.assertEqual(updatedUser.name, "User Test With Changes")
        self.assertEqual(updatedUser.age, 22)

    def test_delete_user(self):
        """Testing if the user has been deleted by user crud"""
        user = UserCrud.read_by_email("emaildeexemplo@gmail.com")
        UserCrud.delete(user.id)
        with self.assertRaises(ValueError):
            UserCrud.read_by_email("emaildeexemplo@gmail.com")


class AddressCrudTest(TestCase):
    "Tests to check address CRUD"

    def setUp(self):
        self.address = AddressCrud.create(
            street="Rua Exemplo",
            number="123",
            complement="Apto 101",
            neighborhood="Bairro Exemplo",
            city="Cidade Exemplo",
            state="Estado Exemplo",
            cep="12345-678",
            country="Brasil",
        )
        return super().setUp()

    def test_create_address(self):
        """Testing if the address has been created correctly"""
        address = AddressCrud.read_by_id(self.address.id)
        self.assertEqual(address.street, "Rua Exemplo")

    def test_read_addresses(self):
        """Testing if the addresses have been retrieved by address crud"""
        addresses = AddressCrud.read()
        self.assertGreater(len(addresses), 0)

    def test_update_address(self):
        """Testing if the address has been updated by address crud"""
        updated_address = AddressCrud.update(
            self.address.id, street="Rua Nova", city="Cidade Nova"
        )
        self.assertEqual(updated_address.street, "Rua Nova")
        self.assertEqual(updated_address.city, "Cidade Nova")

    def test_delete_address(self):
        """Testing if the address has been deleted by address crud"""
        address_id = self.address.id
        AddressCrud.delete(address_id)
        with self.assertRaises(ValueError):
            AddressCrud.read_by_id(address_id)

    def test_formatted_address(self):
        """Testing if the address is formatted correctly"""
        formatted = AddressCrud.formatted_address(self.address.id)
        expected = "Rua Exemplo, 123, Bairro Exemplo, Cidade Exemplo, Estado Exemplo, 12345-678, Brasil"
        self.assertEqual(formatted, expected)


class StoreCrudTest(TestCase):
    "Tests to check store CRUD"

    def setUp(self):
        UserCrud.create(
            role="Shop",
            name="Shop User",
            age=30,
            email="shopuser@test.com",
            password="password",
        )
        UserCrud.create(
            role="Man",
            name="Manager User",
            age=40,
            email="manageruser@test.com",
            password="password",
        )
        self.store = StoreCrud.create(
            user_email="shopuser@test.com",
            name="My Test Store",
            contact="123456789",
            registration="987654321",
            street="Main St",
            number="10",
            complement="",
            neighborhood="Downtown",
            city="Testville",
            state="Testland",
            cep="12345-000",
            country="Testland",
        )

    def test_create_store_with_shop_user(self):
        """Testing if a store is created with a shop user"""
        store = StoreCrud.read_by_id(self.store.id)
        self.assertEqual(store.name, "My Test Store")
        self.assertEqual(store.user.email, "shopuser@test.com")

    def test_create_store_with_wrong_role_fails(self):
        """Testing if creating a store with a non-shop user raises an error"""
        with self.assertRaises(UserRoleError):
            StoreCrud.create(
                user_email="manageruser@test.com",
                name="Manager's Store",
                contact="987654321",
                registration="123456789",
                street="Second St",
                number="20",
                complement="",
                neighborhood="Uptown",
                city="Testville",
                state="Testland",
                cep="54321-000",
                country="Testland",
            )

    def test_read_stores(self):
        """Testing if stores are retrieved by store crud"""
        stores = StoreCrud.read()
        self.assertGreater(len(stores), 0)

    def test_read_stores_by_email(self):
        """Testing retrieval of stores by user email"""
        stores = StoreCrud.read_stores_by_email("shopuser@test.com")
        self.assertEqual(len(stores), 1)
        self.assertEqual(stores[0].name, "My Test Store")

    def test_update_store(self):
        """Testing if the store and its address can be updated"""
        updated_store = StoreCrud.update(
            self.store.id,
            name="My Updated Store",
            contact="999888777",
            street="Updated St",
        )
        self.assertEqual(updated_store.name, "My Updated Store")
        self.assertEqual(updated_store.contact, "999888777")
        self.assertEqual(updated_store.address.street, "Updated St")

    def test_update_store_user_fails(self):
        """Testing that updating the user of a store raises an error"""
        another_user = UserCrud.create(
            role="Shop",
            name="Another Shop User",
            age=25,
            email="another@test.com",
            password="password",
        )
        with self.assertRaises(UpdateError):
            StoreCrud.update(self.store.id, user=another_user)

    def test_delete_store(self):
        """Testing if the store and its address are deleted"""
        store_id = self.store.id
        address_id = self.store.address.id
        StoreCrud.delete(store_id)
        with self.assertRaises(ValueError):
            StoreCrud.read_by_id(store_id)
        with self.assertRaises(ValueError):
            AddressCrud.read_by_id(address_id)


class DepotCrudTest(TestCase):
    "Tests to check depot CRUD"

    def setUp(self):
        self.user = UserCrud.create(
            role="Man",
            name="Manager User",
            age=40,
            email="manageruser@test.com",
            password="password",
        )
        UserCrud.create(
            role="Shop",
            name="Shop User",
            age=30,
            email="shopuser@test.com",
            password="password",
        )
        self.depot = DepotCrud.create(
            user_email="manageruser@test.com",
            name="Main Depot",
            contact="111222333",
            registration="1122334455",
            street="Depot St",
            number="100",
            complement="Warehouse 1",
            neighborhood="Industrial Park",
            city="Depotville",
            state="Depotland",
            cep="54321-123",
            country="Depotland",
        )

    def test_create_depot_with_manager_user(self):
        """Testing if a depot is created with a manager user"""
        depot = DepotCrud.read_by_id(self.depot.id)
        self.assertEqual(depot.name, "Main Depot")
        self.assertEqual(depot.user.email, "manageruser@test.com")

    def test_create_depot_with_wrong_role_fails(self):
        """Testing if creating a depot with a non-manager user raises an error"""
        with self.assertRaises(UserRoleError):
            DepotCrud.create(
                user_email="shopuser@test.com",
                name="Shop's Depot",
                contact="987654321",
                registration="123456789",
                street="Second St",
                number="20",
                complement="",
                neighborhood="Uptown",
                city="Testville",
                state="Testland",
                cep="54321-000",
                country="Testland",
            )

    def test_read_depots(self):
        """Testing if depots are retrieved by depot crud"""
        depots = DepotCrud.read()
        self.assertGreater(len(depots), 0)

    def test_read_depots_by_email(self):
        """Testing retrieval of depots by user email"""
        depots = DepotCrud.read_depots_by_email("manageruser@test.com")
        self.assertEqual(len(depots), 1)
        self.assertEqual(depots[0].name, "Main Depot")

    def test_update_depot(self):
        """Testing if the depot and its address can be updated"""
        updated_depot = DepotCrud.update(
            self.depot.id,
            name="Updated Main Depot",
            contact="444555666",
            city="Updated City",
        )
        self.assertEqual(updated_depot.name, "Updated Main Depot")
        self.assertEqual(updated_depot.contact, "444555666")
        self.assertEqual(updated_depot.address.city, "Updated City")

    def test_update_depot_user_fails(self):
        """Testing that updating the user of a depot raises an error"""
        another_user = UserCrud.create(
            role="Man",
            name="Another Manager",
            age=45,
            email="anothermanager@test.com",
            password="password",
        )
        with self.assertRaises(UpdateError):
            DepotCrud.update(self.depot.id, user=another_user)

    def test_delete_depot(self):
        """Testing if the depot and its address are deleted"""
        depot_id = self.depot.id
        address_id = self.depot.address.id
        DepotCrud.delete(depot_id)
        with self.assertRaises(ValueError):
            DepotCrud.read_by_id(depot_id)
        with self.assertRaises(ValueError):
            AddressCrud.read_by_id(address_id)


class CarrierCrudTest(TestCase):
    "Tests to check carrier CRUD"

    def setUp(self):
        self.user = UserCrud.create(
            role="Carr",
            name="Carrier User",
            age=35,
            email="carrieruser@test.com",
            password="password",
        )
        UserCrud.create(
            role="Shop",
            name="Shop User",
            age=30,
            email="shopuser@test.com",
            password="password",
        )
        self.carrier = CarrierCrud.create(
            user_email="carrieruser@test.com",
            name="Fast Carrier",
            contact="555666777",
            registration="5566778899",
            street="Carrier Ave",
            number="200",
            complement="",
            neighborhood="Transport Hub",
            city="Carrierville",
            state="Carrierland",
            cep="98765-432",
            country="Carrierland",
        )

    def test_create_carrier_with_carrier_user(self):
        """Testing if a carrier is created with a carrier user"""
        carrier = CarrierCrud.read_by_id(self.carrier.id)
        self.assertEqual(carrier.name, "Fast Carrier")
        self.assertEqual(carrier.user.email, "carrieruser@test.com")

    def test_create_carrier_with_wrong_role_fails(self):
        """Testing if creating a carrier with a non-carrier user raises an error"""
        with self.assertRaises(UserRoleError):
            CarrierCrud.create(
                user_email="shopuser@test.com",
                name="Shop's Carrier",
                contact="123123123",
                registration="456456456",
                street="Shop St",
                number="30",
                complement="",
                neighborhood="Shopping District",
                city="Shopville",
                state="Shopland",
                cep="11223-344",
                country="Shopland",
            )

    def test_read_carriers(self):
        """Testing if carriers are retrieved by carrier crud"""
        carriers = CarrierCrud.read()
        self.assertGreater(len(carriers), 0)

    def test_read_carriers_by_email(self):
        """Testing retrieval of carriers by user email"""
        carriers = CarrierCrud.read_carriers_by_email("carrieruser@test.com")
        self.assertEqual(len(carriers), 1)
        self.assertEqual(carriers[0].name, "Fast Carrier")

    def test_update_carrier(self):
        """Testing if the carrier and its address can be updated"""
        updated_carrier = CarrierCrud.update(
            self.carrier.id,
            name="Super Fast Carrier",
            contact="888999000",
            state="Updated State",
        )
        self.assertEqual(updated_carrier.name, "Super Fast Carrier")
        self.assertEqual(updated_carrier.contact, "888999000")
        self.assertEqual(updated_carrier.address.state, "Updated State")

    def test_update_carrier_user_fails(self):
        """Testing that updating the user of a carrier raises an error"""
        another_user = UserCrud.create(
            role="Carr",
            name="Another Carrier",
            age=38,
            email="anothercarrier@test.com",
            password="password",
        )
        with self.assertRaises(UpdateError):
            CarrierCrud.update(self.carrier.id, user=another_user)

    def test_delete_carrier(self):
        """Testing if the carrier and its address are deleted"""
        carrier_id = self.carrier.id
        address_id = self.carrier.address.id
        CarrierCrud.delete(carrier_id)
        with self.assertRaises(ValueError):
            CarrierCrud.read_by_id(carrier_id)
        with self.assertRaises(ValueError):
            AddressCrud.read_by_id(address_id)


class TruckCrudTest(TestCase):
    "Tests to check truck CRUD"

    def setUp(self):
        self.user = UserCrud.create(
            role="Carr",
            name="Carrier User",
            age=35,
            email="carrieruser@test.com",
            password="password",
        )
        self.carrier1 = CarrierCrud.create(
            user_email="carrieruser@test.com",
            name="Fast Carrier",
            contact="555666777",
            registration="5566778899",
            street="Carrier Ave",
            number="200",
            complement="",
            neighborhood="Transport Hub",
            city="Carrierville",
            state="Carrierland",
            cep="98765-432",
            country="Carrierland",
        )
        self.truck = TruckCrud.create(
            carrier_id=self.carrier1.id,
            plate="TRK1234",
            category="medium",
            release_year=2020,
        )

    def test_create_light_truck(self):
        """Testing creation of a light truck"""
        truck = TruckCrud.create(self.carrier1.id, "LGT1111", "light", 2021)
        self.assertEqual(truck.plate, "LGT1111")
        self.assertEqual(truck.axles_count, 2)

    def test_create_medium_truck(self):
        """Testing creation of a medium truck"""
        truck = TruckCrud.read_by_plate("TRK1234")
        self.assertEqual(truck.plate, "TRK1234")
        self.assertEqual(truck.axles_count, 3)

    def test_create_heavy_truck(self):
        """Testing creation of a heavy truck"""
        truck = TruckCrud.create(self.carrier1.id, "HVY2222", "heavy", 2022)
        self.assertEqual(truck.plate, "HVY2222")
        self.assertEqual(truck.axles_count, 5)

    def test_read_trucks(self):
        """Testing if trucks are retrieved"""
        trucks = TruckCrud.read()
        self.assertGreater(len(trucks), 0)

    def test_read_trucks_by_carrier(self):
        """Testing retrieval of trucks by carrier"""
        trucks = TruckCrud.read_trucks_by_carrier(self.carrier1.id)
        self.assertEqual(len(trucks), 1)
        self.assertEqual(trucks[0].plate, "TRK1234")

    def test_change_carrier_truck_success(self):
        """Testing successfully changing a truck's carrier"""
        carrier2 = CarrierCrud.create(
            user_email=self.user.email,
            name="Slower Carrier",
            contact="111222333",
            registration="11223344",
            street="Slow Lane",
            number="10",
            complement="",
            neighborhood="Suburb",
            city="Carrierville",
            state="Carrierland",
            cep="98765-111",
            country="Carrierland",
        )
        updated_truck = TruckCrud.change_carrier_truck(
            self.truck.plate, self.carrier1.id, carrier2.id
        )
        self.assertEqual(updated_truck.carrier.id, carrier2.id)

    def test_change_carrier_same_id_fails(self):
        """Testing failure when new and current carrier IDs are the same"""
        with self.assertRaisesMessage(
            ValueError, "The carrier IDs entered are the same"
        ):
            TruckCrud.change_carrier_truck(
                self.truck.plate, self.carrier1.id, self.carrier1.id
            )

    def test_change_carrier_wrong_belong_fails(self):
        """Testing failure when truck does not belong to the specified carrier"""
        wrong_carrier_id = 999
        with self.assertRaises(BelongError):
            TruckCrud.change_carrier_truck(
                self.truck.plate, wrong_carrier_id, self.carrier1.id
            )

    def test_change_carrier_different_user_fails(self):
        """Testing failure when carriers belong to different users"""
        other_user = UserCrud.create(
            role="Carr",
            name="Other Carrier User",
            age=40,
            email="other@test.com",
            password="password",
        )
        carrier3 = CarrierCrud.create(
            user_email=other_user.email,
            name="Third Carrier",
            contact="444555666",
            registration="44556677",
            street="Third St",
            number="30",
            complement="",
            neighborhood="Industrial",
            city="Carrierville",
            state="Carrierland",
            cep="98765-222",
            country="Carrierland",
        )
        with self.assertRaises(BelongError):
            TruckCrud.change_carrier_truck(
                self.truck.plate, self.carrier1.id, carrier3.id
            )

    def test_delete_truck(self):
        """Testing if a truck is deleted"""
        plate = self.truck.plate
        TruckCrud.delete(plate)
        with self.assertRaises(ValueError):
            TruckCrud.read_by_plate(plate)


class OrderCrudTest(TestCase):
    "Tests to check order CRUD"

    def setUp(self):
        user = UserCrud.create(
            role="Shop",
            name="Shop User",
            age=30,
            email="shopuser@test.com",
            password="password",
        )
        self.store = StoreCrud.create(
            user_email="shopuser@test.com",
            name="My Test Store",
            contact="123456789",
            registration="987654321",
            street="Main St",
            number="10",
            complement="",
            neighborhood="Downtown",
            city="Testville",
            state="Testland",
            cep="12345-000",
            country="Testland",
        )
        self.order = OrderCrud.create(self.store.id)

    def test_create_order(self):
        """Testing creation of an order"""
        order = OrderCrud.read_by_id(self.order.id)
        self.assertEqual(order.store.id, self.store.id)
        self.assertEqual(order.status, "Pend")
        self.assertEqual(order.total_boxes, 0)
        self.assertFalse(order.scheduled)

    def test_read_orders(self):
        """Testing if orders are retrieved"""
        orders = OrderCrud.read()
        self.assertGreater(len(orders), 0)

    def test_read_orders_by_store(self):
        """Testing retrieval of orders by store"""
        orders = OrderCrud.read_orders_by_store(self.store.id)
        self.assertEqual(len(orders), 1)
        self.assertEqual(orders[0].id, self.order.id)

    def test_read_pend_orders(self):
        """Testing retrieval of pending orders"""
        OrderCrud.create(self.store.id)
        pending_orders = OrderCrud.read_pend_orders()
        self.assertGreaterEqual(len(pending_orders), 1)
        for order in pending_orders:
            self.assertEqual(order.status, "Pend")

    def test_delete_pending_order(self):
        """Testing deletion of a pending order"""
        order_id = self.order.id
        OrderCrud.delete(order_id)
        with self.assertRaises(ValueError):
            OrderCrud.read_by_id(order_id)

    def test_delete_non_pending_order_fails(self):
        """Testing that deleting a non-pending order raises an error"""
        self.order.status = "Sche"
        self.order.save()
        with self.assertRaises(DeleteError):
            OrderCrud.delete(self.order.id)


class TripCrudTest(TestCase):
    "Tests to check trip CRUD"

    def setUp(self):
        user = UserCrud.create(
            role="Man",
            name="Manager User",
            age=40,
            email="manageruser@test.com",
            password="password",
        )
        self.depot = DepotCrud.create(
            user_email="manageruser@test.com",
            name="Main Depot",
            contact="111222333",
            registration="1122334455",
            street="Depot St",
            number="100",
            complement="Warehouse 1",
            neighborhood="Industrial Park",
            city="Depotville",
            state="Depotland",
            cep="54321-123",
            country="Depotland",
        )
        self.trip = TripCrud.create(
            depot_id=self.depot.id,
            total_loaded_weight_kg=1000.5,
            total_loaded_volume_m3=50.5,
            total_distance_km=250.0,
        )

    def test_create_trip(self):
        """Testing creation of a trip"""
        trip = TripCrud.read_by_id(self.trip.id)
        self.assertEqual(trip.origin_depot.id, self.depot.id)
        self.assertEqual(trip.status, "Plan")
        self.assertIsNone(trip.truck)

    def test_read_trips(self):
        """Testing if trips are retrieved"""
        trips = TripCrud.read()
        self.assertGreater(len(trips), 0)

    def test_read_by_status(self):
        """Testing retrieval of trips by status"""
        planned_trips = TripCrud.read_by_status("Plan")
        self.assertIn(self.trip, planned_trips)

        self.trip.status = "InTr"
        self.trip.save()
        in_transit_trips = TripCrud.read_by_status("InTr")
        self.assertIn(self.trip, in_transit_trips)

    def test_read_by_invalid_status_fails(self):
        """Testing failure when reading by an invalid status"""
        with self.assertRaises(ValueError):
            TripCrud.read_by_status("Invalid")

    def test_delete_planned_trip(self):
        """Testing deletion of a planned trip"""
        trip_id = self.trip.id
        TripCrud.delete(trip_id)
        with self.assertRaises(ValueError):
            TripCrud.read_by_id(trip_id)

    def test_delete_in_transit_trip_fails(self):
        """Testing that deleting an in-transit trip raises an error"""
        self.trip.status = "InTr"
        self.trip.save()
        with self.assertRaises(DeleteError):
            TripCrud.delete(self.trip.id)

    def test_delete_completed_trip_fails(self):
        """Testing that deleting a completed trip raises an error"""
        self.trip.status = "Comp"
        self.trip.save()
        with self.assertRaises(DeleteError):
            TripCrud.delete(self.trip.id)

    def test_delete_cancelled_trip(self):
        """Testing deletion of a cancelled trip"""
        self.trip.status = "Canc"
        self.trip.save()
        trip_id = self.trip.id
        TripCrud.delete(trip_id)
        with self.assertRaises(ValueError):
            TripCrud.read_by_id(trip_id)


class BoxCrudTest(TestCase):
    "Tests to check box CRUD"

    def setUp(self):
        user = UserCrud.create(
            role="Shop",
            name="Shop User",
            age=30,
            email="shopuser@test.com",
            password="password",
        )
        store = StoreCrud.create(
            user_email="shopuser@test.com",
            name="My Test Store",
            contact="123456789",
            registration="987654321",
            street="Main St",
            number="10",
            complement="",
            neighborhood="Downtown",
            city="Testville",
            state="Testland",
            cep="12345-000",
            country="Testland",
        )
        self.order = OrderCrud.create(store.id)

    def test_create_small_box(self):
        """Testing creation of a small box"""
        box = BoxCrud.create(self.order.id, "small", None, None, None, None)
        self.assertEqual(box.size, "Sma")
        self.assertEqual(box.payload_kg, 5.0)

    def test_create_custom_box(self):
        """Testing creation of a custom box"""
        box = BoxCrud.create(self.order.id, "custom", 0.1, 0.2, 0.3, 1.5)
        self.assertEqual(box.size, "Cus")
        self.assertEqual(box.length, 0.1)
        self.assertAlmostEqual(box.volume_m3, 0.006)

    def test_create_invalid_size_string_fails(self):
        """Testing failure when creating a box with an invalid size string"""
        with self.assertRaises(ValueError):
            BoxCrud.create(self.order.id, "tiny", None, None, None, None)

    def test_create_custom_box_missing_dims_fails(self):
        """Testing failure for custom box with missing dimensions"""
        with self.assertRaises(ValueError):
            BoxCrud.create(self.order.id, "custom", 0.1, 0.2, None, 1.5)

    def test_create_custom_box_invalid_dims_fails(self):
        """Testing failure for custom box with invalid (zero) dimensions"""
        with self.assertRaises(ValueError):
            BoxCrud.create(self.order.id, "custom", 0.1, 0.0, 0.3, 1.5)

    def test_read_boxes_by_order(self):
        """Testing retrieval of boxes by order"""
        BoxCrud.create(self.order.id, "small", None, None, None, None)
        BoxCrud.create(self.order.id, "medium", None, None, None, None)
        boxes = BoxCrud.read_boxes_by_order(self.order.id)
        self.assertEqual(len(boxes), 2)

    def test_delete_box_with_pending_order(self):
        """Testing deletion of a box when the order is pending"""
        box = BoxCrud.create(self.order.id, "small", None, None, None, None)
        box_id = box.id
        BoxCrud.delete(box_id)
        with self.assertRaises(ValueError):
            BoxCrud.read_by_id(box_id)

    def test_delete_box_with_shipped_order_fails(self):
        """Testing that deleting a box from a shipped order raises an error"""
        self.order.status = "Ship"
        self.order.save()
        box = BoxCrud.create(self.order.id, "small", None, None, None, None)
        with self.assertRaises(DeleteError):
            BoxCrud.delete(box.id)


class DeliveryCrudTest(TestCase):
    "Tests to check delivery CRUD"

    def setUp(self):
        shop_user = UserCrud.create(
            role="Shop",
            name="Shop User",
            age=30,
            email="shopuser@test.com",
            password="password",
        )
        manager_user = UserCrud.create(
            role="Man",
            name="Manager User",
            age=40,
            email="manageruser@test.com",
            password="password",
        )
        self.store = StoreCrud.create(
            user_email="shopuser@test.com",
            name="My Test Store",
            contact="123456789",
            registration="987654321",
            street="Main St",
            number="10",
            complement="",
            neighborhood="Downtown",
            city="Testville",
            state="Testland",
            cep="12345-000",
            country="Testland",
        )
        self.depot = DepotCrud.create(
            user_email="manageruser@test.com",
            name="Main Depot",
            contact="111222333",
            registration="1122334455",
            street="Depot St",
            number="100",
            complement="Warehouse 1",
            neighborhood="Industrial Park",
            city="Depotville",
            state="Depotland",
            cep="54321-123",
            country="Depotland",
        )
        self.order = OrderCrud.create(self.store.id)
        self.trip = TripCrud.create(
            depot_id=self.depot.id,
            total_loaded_weight_kg=100.0,
            total_loaded_volume_m3=10.0,
            total_distance_km=50.0,
        )
        self.delivery = DeliveryCrud.create(self.trip.id, self.store.id, self.order.id)

    def test_create_delivery(self):
        """Testing creation of a delivery record"""
        delivery = DeliveryCrud.read_by_id(self.delivery.id)
        self.assertEqual(delivery.trip.id, self.trip.id)
        self.assertEqual(delivery.store.id, self.store.id)
        self.assertEqual(delivery.order.id, self.order.id)
        self.assertIsNone(delivery.delivered_at)

    def test_read_deliveries_by_trip(self):
        """Testing retrieval of deliveries by trip"""
        deliveries = DeliveryCrud.delivery_by_trip(self.trip.id)
        self.assertEqual(len(deliveries), 1)
        self.assertEqual(deliveries[0].id, self.delivery.id)

    def test_is_delivered(self):
        """Testing the is_delivered check"""
        self.assertFalse(DeliveryCrud.is_delivered(self.delivery.id))
        self.delivery.delivered_at = timezone.now()
        self.delivery.save()
        self.assertTrue(DeliveryCrud.is_delivered(self.delivery.id))

    def test_delete_undelivered_delivery(self):
        """Testing deletion of a delivery that has not been completed"""
        delivery_id = self.delivery.id
        DeliveryCrud.delete(delivery_id)
        with self.assertRaises(ValueError):
            DeliveryCrud.read_by_id(delivery_id)

    def test_delete_delivered_delivery_fails(self):
        """Testing that deleting a completed delivery raises an error"""
        self.delivery.delivered_at = timezone.now()
        self.delivery.save()
        with self.assertRaises(DeleteError):
            DeliveryCrud.delete(self.delivery.id)


class UserAPITest(TestCase):
    "Tests to check all the user API views"

    def setUp(self):
        self.client = Client()
        self.user = UserCrud.create(
            role="Adm",
            name="Admin User",
            age=40,
            email="admin@test.com",
            password="adminpassword",
        )

    def test_login_success(self):
        """Testing successful user login"""
        response = self.client.post(
            reverse("Login Route"),
            data=json.dumps({"email": "admin@test.com", "password": "adminpassword"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("sessionid", response.cookies)
        response_data = response.json()
        self.assertEqual(response_data["message"], "User successfully logged in!")

    def test_login_fail(self):
        """Testing failed user login with wrong password"""
        response = self.client.post(
            reverse("Login Route"),
            data=json.dumps({"email": "admin@test.com", "password": "wrongpassword"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(response_data["error"], "Invalid credentials!")

    def test_list_users_unauthorized(self):
        """Testing that listing users is open (SECURITY ISSUE)"""
        response = self.client.get(reverse("Users Routes"))
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.json()["data"]), 0)

    def test_create_user_unauthorized(self):
        """Testing that creating users is open (SECURITY ISSUE)"""
        response = self.client.post(
            reverse("Users Routes"),
            data=json.dumps(
                {
                    "role": "Shop",
                    "name": "New User",
                    "age": 25,
                    "email": "newuser@test.com",
                    "password": "newpassword",
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(UserCrud.read_by_email("newuser@test.com"))

    def test_logout(self):
        """Testing user logout"""
        self.client.login(email="admin@test.com", password="adminpassword")
        response = self.client.post(reverse("Logout Route"))
        self.assertEqual(response.status_code, 200)
        # Verify user is logged out by trying to access an authenticated view
        response = self.client.get(
            reverse("User Route", kwargs={"email": "admin@test.com"})
        )
        self.assertEqual(response.status_code, 401)

    def test_get_user_details_authenticated(self):
        """Testing getting user details when authenticated"""
        self.client.login(email="admin@test.com", password="adminpassword")
        response = self.client.get(
            reverse("User Route", kwargs={"email": "admin@test.com"})
        )
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertEqual(response_data["data"]["email"], "admin@test.com")

    def test_get_user_details_unauthenticated(self):
        """Testing getting user details when not authenticated"""
        response = self.client.get(
            reverse("User Route", kwargs={"email": "admin@test.com"})
        )
        self.assertEqual(response.status_code, 401)

    def test_update_user_details(self):
        """Testing updating user details"""
        self.client.login(email="admin@test.com", password="adminpassword")
        update_data = {"name": "Admin User Updated", "age": 41}
        response = self.client.put(
            reverse("User Route", kwargs={"email": "admin@test.com"}),
            data=json.dumps(update_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        updated_user = UserCrud.read_by_email("admin@test.com")
        self.assertEqual(updated_user.name, "Admin User Updated")
        self.assertEqual(updated_user.age, 41)

    def test_delete_user(self):
        """Testing deleting a user"""
        user_to_delete = UserCrud.create(
            role="Shop",
            name="To Delete",
            age=30,
            email="todelete@test.com",
            password="password",
        )
        self.client.login(email="admin@test.com", password="adminpassword")
        response = self.client.delete(
            reverse("User Route", kwargs={"email": "todelete@test.com"})
        )
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(ValueError):
            UserCrud.read_by_email("todelete@test.com")

    def test_change_password_incorrect_old(self):
        """Testing change password with incorrect old password fails"""
        self.client.login(email="admin@test.com", password="adminpassword")
        response = self.client.put(
            reverse("Change Password Route", kwargs={"email": "admin@test.com"}),
            data=json.dumps(
                {"old_password": "wrongoldpassword", "new_password": "newpassword123"}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid old password", response.json()["error"])

    def test_change_password_success(self):
        """Testing successful password change"""
        first_login_response = self.client.post(
            reverse("Login Route"),
            data=json.dumps({"email": "admin@test.com", "password": "adminpassword"}),
            content_type="application/json",
        )
        self.assertEqual(first_login_response.status_code, 200)
        response = self.client.put(
            reverse("Change Password Route", kwargs={"email": "admin@test.com"}),
            data=json.dumps(
                {"old_password": "adminpassword", "new_password": "newpassword123"}
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        # Check if the new password works for login
        self.client.post(reverse("Logout Route"))
        login_response = self.client.post(
            reverse("Login Route"),
            data=json.dumps({"email": "admin@test.com", "password": "newpassword123"}),
            content_type="application/json",
        )
        self.assertEqual(login_response.status_code, 200)

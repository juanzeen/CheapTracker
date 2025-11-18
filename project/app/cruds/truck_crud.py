from ..models import Truck, Carrier


class TruckCrud:
    @staticmethod
    def create(carrier_id, plate, category, release_year):
        carrier = Carrier.objects.get(id=carrier_id)
        match category:
            case "light":
                return Truck.objects.create(
                    carrier=carrier,
                    plate=plate,
                    axles_count=2,
                    cargo_length=5.5,
                    cargo_width=2.2,
                    cargo_height=2.2,
                    max_payload_kg=3000.0,
                    euro=5,
                    is_active=False,
                    release_year=release_year,
                    total_trips=0,
                    max_fuel_capacity=150,
                )
            case "medium":
                return Truck.objects.create(
                    carrier=carrier,
                    plate=plate,
                    axles_count=3,
                    cargo_length=8.5,
                    cargo_width=2.5,
                    cargo_height=2.6,
                    max_payload_kg=14000.0,
                    euro=6,
                    is_active=False,
                    release_year=release_year,
                    total_trips=0,
                    max_fuel_capacity=550,
                )
            case "heavy":
                return Truck.objects.create(
                    carrier=carrier,
                    plate=plate,
                    axles_count=5,
                    cargo_length=14.0,
                    cargo_width=2.6,
                    cargo_height=2.8,
                    max_payload_kg=25000.0,
                    euro=6,
                    is_active=False,
                    release_year=release_year,
                    total_trips=0,
                    max_fuel_capacity=980,
                )

    @staticmethod
    def read():
        return Truck.objects.all()

    @staticmethod
    def read_trucks_by_carrier(carrier_id):
        carrier = Carrier.objects.get(id=carrier_id)
        return Truck.objects.filter(carrier=carrier)

    @staticmethod
    def change_carrier_truck(plate, current_carrier_id, new_carrier_id):
        if current_carrier_id == new_carrier_id:
            raise ValueError("The carrier IDs entered are the same")

        truck = Truck.objects.get(plate=plate)
        if truck.carrier.id != current_carrier_id:
            raise ValueError("This truck does not belong to this carrier")

        try:
            new_carrier = Carrier.objects.get(id=new_carrier_id)
        except Carrier.DoesNotExist:
            raise ValueError("New carrier ID not found")

        if new_carrier.user == truck.carrier.user:
            setattr(truck, "carrier", new_carrier)
            truck.save()
            return truck
        else:
            raise ValueError("The carriers entered are not from the same user")

    @staticmethod
    def delete(plate):
        Truck.objects.get(plate=plate).delete()

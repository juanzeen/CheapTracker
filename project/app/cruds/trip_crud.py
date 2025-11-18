from ..models import Trip, Truck, Depot


class TripCrud:
    @staticmethod
    def create(truck_id, depot_id,
               total_loaded_weight_kg, total_loaded_volume_m3,
               total_distance_km, carbon_kg_co2):
        try:
            truck = Truck.objects.get(id=truck_id)
        except Truck.DoesNotExist:
            raise ValueError("Truck not found")

        try:
            depot = Depot.objects.get(id=depot_id)
        except Depot.DoesNotExist:
            raise ValueError("Depot not found")

        return Trip.objects.create(truck=truck, origin_depot=depot,
                                   departure_date=None, arrival_date=None,
                                   total_loaded_weight_kg=total_loaded_weight_kg,
                                   total_loaded_volume_m3=total_loaded_volume_m3,
                                   total_distance_km = total_distance_km,
                                   carbon_kg_co2=carbon_kg_co2, status="Plan")

    @staticmethod
    def read():
        return Trip.objects.all()

    @staticmethod
    def read_by_id(trip_id):
        try:
            return Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            raise ValueError("Trip not found")

    @staticmethod
    def read_by_status(status_option):
        if status_option not in ["Plan", "InTr", "Comp", "Canc"]:
            raise ValueError("Status option must be: Plan, InTr, Comp or Canc")

        return Trip.objects.filter(status=status_option)

    @staticmethod
    def update(trip_id, **kwargs):
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            raise ValueError("Trip not found")

        for key, value in kwargs.items():
            if key == "truck_id":
                try:
                    Truck.objects.get(id=value)
                except Truck.DoesNotExist:
                    raise ValueError("Truck not found")

                setattr(trip, key, value)

            elif key == "depot_id":
                raise KeyError("Change depot trip denied. Create a new trip")

            elif key in ["departure_date", "arrival_date"]:
                setattr(trip, key, value)

            else:
                raise KeyError("Update denied")

        trip.save()
        return trip

    @staticmethod
    def delete(trip_id):
        try:
            trip = Trip.objects.get(id=trip_id)
        except Trip.DoesNotExist:
            raise ValueError("Trip not found")

        if trip.status in ["InTr", "Comp"]:
            raise ValueError(
                "Delete trip denied. This trip is in transit or has already "
                "been completed"
            )

        trip.delete()

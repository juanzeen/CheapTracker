from ..models import Trip
from .depot_crud import DepotCrud
from ..exception_errors import DeleteError


class TripCrud:
    @staticmethod
    def create(
        depot_id,
        total_loaded_weight_kg,
        total_loaded_volume_m3,
        total_distance_km,
    ):
        depot = DepotCrud.read_by_id(depot_id)

        return Trip.objects.create(
            truck=None,
            origin_depot=depot,
            departure_date=None,
            arrival_date=None,
            total_loaded_weight_kg=total_loaded_weight_kg,
            total_loaded_volume_m3=total_loaded_volume_m3,
            total_distance_km=total_distance_km,
            carbon_kg_co2=None,
            status="Plan",
        )

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
    def delete(trip_id):
        trip = TripCrud.read_by_id(trip_id)

        if trip.status in ["InTr", "Comp"]:
            raise DeleteError(
                "Delete trip denied. This trip is in transit or has already "
                "been completed"
            )

        trip.delete()
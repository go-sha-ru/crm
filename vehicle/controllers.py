import typing

from ninja_extra import api_controller, route

from vehicle import schema
from vehicle.models import SpecialVehicle, VEHICLE_STATUS_ACTIVE


@api_controller("/vehicle")
class VehicleController(object):

    @route.get('', response={200: typing.List[schema.VehicleSchema]})
    def list(self, type_id=None) -> typing.List[schema.VehicleSchema]:
        qs = SpecialVehicle.objects.filter(status=VEHICLE_STATUS_ACTIVE)
        if type_id is not None:
            qs = qs.filter(special_vehicle_type=type_id)
        return qs

from ninja import ModelSchema

from vehicle.models import SpecialVehicleType, SpecialVehicle


class VehicleSchema(ModelSchema):

    class Meta:
        model = SpecialVehicle
        fields = ('id', 'model')


class SpecialVehicleTypeSchema(ModelSchema):

    class Meta:
        model = SpecialVehicleType
        fields = ('id', 'title', 'description')

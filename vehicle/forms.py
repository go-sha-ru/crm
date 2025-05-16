from django import forms

from vehicle.models import SpecialVehicleOrder


class VehicleOrderCreateForm(forms.ModelForm):

    class Meta:
        model = SpecialVehicleOrder
        fields = ['project', 'work', 'starting_at', 'ending_at', 'special_vehicle_type', 'special_vehicle']


class VehicleOrderChangeForm(forms.ModelForm):

    class Meta:
        model = SpecialVehicleOrder
        fields = ['started_at', 'ended_at', 'status', 'notes']

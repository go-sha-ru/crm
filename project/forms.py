from django.forms import ModelForm, TextInput

from project.models import Project, Work


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }


class WorkForm(ModelForm):
    class Meta:
        model = Work
        fields = '__all__'
        widgets = {
            'color': TextInput(attrs={'type': 'color'}),
        }

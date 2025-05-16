from ninja import ModelSchema

from project.models import Project, Work


class ProjectSchema(ModelSchema):

    class Meta:
        model = Project
        fields = ('id', 'title')


class WorkSchema(ModelSchema):

    class Meta:
        model = Work
        fields = ('id', 'title')

import typing

from ninja_extra import api_controller, route

from project import schema
from project.models import Project, Work


@api_controller("/project")
class ProjectController(object):

    @route.get('', response={200: typing.List[schema.ProjectSchema]})
    def list(self):
        return Project.objects.all()

    @route.get('/works', response={200: typing.List[schema.WorkSchema]})
    def get_works(self, project_id):
        return Work.objects.filter(project_id=project_id).all()

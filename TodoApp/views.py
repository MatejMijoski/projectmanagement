from django.db.models import Q
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from ProjectManagementApp.models import Project
from TodoApp.models import ProjectTasks
from TodoApp.serializers import ProjectTaskSerializer
from projectmanagement.paginator import CustomPaginator


# Create your views here.
class TaskListCreateView(ListCreateAPIView):
    serializer_class = ProjectTaskSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        return ProjectTasks.objects.filter(
            Q(project__owner=self.request.user) | Q(project__owner=self.request.user),
            project=Project.objects.get(id=self.kwargs.get("project_id")),
        )


class TaskRetrieveView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProjectTaskSerializer
    pagination_class = CustomPaginator
    lookup_field = "id"

    def get_object(self):
        return ProjectTasks.objects.get(
            id=self.kwargs.get("id"), owner=self.request.user
        )

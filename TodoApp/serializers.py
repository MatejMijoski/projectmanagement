from django.core.exceptions import ValidationError
from django.db.models import Q
from rest_framework import serializers

from ProjectManagementApp.models import Project
from TodoApp.models import ProjectTasks
from projectmanagement.exceptions import CustomException


class ProjectTaskSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.email", read_only=True)

    class Meta:
        model = ProjectTasks
        fields = (
            "id",
            "owner",
            "type",
            "importance",
            "title",
            "is_completed",
            "description",
            "due_date",
            "created_at",
        )

    def create(self, validated_data):
        validated_data["owner"] = self.context.get("request").user
        try:
            project_id = (
                self.context.get("request")
                .parser_context.get("kwargs")
                .get("project_id")
            )
            user = self.context.get("request").user
            project = Project.objects.get(
                Q(project__owner=user) | Q(project__owner=user), id=project_id
            )
            validated_data["project"] = project
        except Project.DoesNotExist:
            raise CustomException(404, "The client was not found.")
        except ValidationError:
            raise CustomException(400, "The UUID is not valid.")
        return super(ProjectTaskSerializer, self).create(validated_data)

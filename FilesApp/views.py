from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveDestroyAPIView
from rest_framework.views import APIView
from projectmanagement.paginator import CustomPaginator
from projectmanagement.exceptions import CustomException
from FilesApp.models import Files
from FilesApp.serializers import FileSerializer, FilePostSerializer
from FilesApp.services import upload_file, download_file, delete_s3_file
from ProjectManagementApp.models import Project


# MAX 2 MB per file
# MAX 2 GB per project
# Create your views here.
class FileProjectListView(ListAPIView):
    pagination_class = CustomPaginator
    serializer_class = FileSerializer

    def get_queryset(self):
        return Files.objects.filter(owner=self.request.user)


class FileListCreateView(ListCreateAPIView):
    pagination_class = CustomPaginator
    serializer_class = FileSerializer

    def create(self, request, *args, **kwargs):
        serializer = FilePostSerializer(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['owner'] = self.request.user
            try:
                serializer.validated_data['project'] = Project.objects \
                    .get(Q(owner=self.request.user) | Q(users=self.request.user),
                         id=self.kwargs.get('project_id'))
            except Project.DoesNotExist:
                raise CustomException(400, "The project does not exist")
            except ValidationError:
                raise CustomException(400, "The UUID is not valid.")
            file_directory = "projects/" + self.kwargs.get('project_id') + "/"
            file_path_within_bucket = file_directory + serializer.validated_data.get('file').name.replace(" ", "_")
            status, data = upload_file(serializer.validated_data, file_path_within_bucket)
            return JsonResponse(data=data, status=status)
        return JsonResponse(data=serializer.errors, status=400)

    def get_queryset(self):
        try:
            return Files.objects.filter(Q(project__owner=self.request.user) | Q(project__users=self.request.user),
                                        project__id=self.kwargs.get('project_id'))
        except ValidationError:
            raise CustomException(400, "The UUID is not correct.")


class FileRetrieveView(RetrieveDestroyAPIView):
    serializer_class = FileSerializer
    lookup_field = 'id'

    def get_object(self):
        try:
            return Files.objects.get(id=self.kwargs.get('id'), owner=self.request.user)
        except Files.DoesNotExist:
            raise CustomException(404, "The file does not exist.")

    def perform_destroy(self, instance):
        delete_s3_file(instance.path)
        return super(FileRetrieveView, self).perform_destroy(instance)


class FileDownloadView(APIView):
    def get(self, request, *args, **kwargs):
        try:
            file = Files.objects.get(id=self.kwargs.get('id'), owner=self.request.user)
            url = download_file(file.path)
            response = HttpResponse(content_type='application/force-download')
            response['Content-Disposition'] = 'attachment; filename="{}"'.format(str(file.name))
            response['X-Accel-Redirect'] = url
            return response
        except (Files.DoesNotExist, Project.DoesNotExist) as e:
            raise CustomException(400, "The file does not exist.", e)

import os

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import JsonResponse
from rest_framework import status
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, CreateAPIView
from rest_framework.views import APIView
from projectmanagement.exceptions import CustomException
from .filters import InvoiceFilter
from .models import Client, Project, Invoice, Resume, TimelineItemClient, ProjectPosts, PostComments
from projectmanagement.paginator import CustomPaginator
from .serializers import ResumeSerializer, InvoicePostSerializer, TimelineItemClientSerializer, \
    ClientRetrieveUpdateSerializer, ClientListSerializer, ClientCreateSerializer, ProjectListSerializer, \
    ProjectRetrieveSerializer, ProjectCreateUpdateSerializer, ProjectPostSerializer, PostCommentSerializer, \
    InvoiceListSerializer
from .services import accept_project_invite
from django_filters import rest_framework as filters


# Create your views here.
class ClientListCreateView(ListCreateAPIView):
    """
    Get all clients for a user or create a new client
    The user is able to get only clients for himself as there are no
    M2M fields in the "Client" model.
    @permissions - Only the owner can do CRUD operations
    """
    pagination_class = CustomPaginator

    def get_queryset(self):
        return Client.objects.filter(owner=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ClientListSerializer
        else:
            return ClientCreateSerializer


class ClientRetrieveView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a client that is owned by the user from the request.
    There are no M2M fields in the "Client" model.
    @permissions - Only the owner can do CRUD operations
    """
    serializer_class = ClientRetrieveUpdateSerializer
    lookup_field = 'id'

    def get_object(self):
        try:
            return Client.objects.get(owner=self.request.user, id=self.kwargs['id'])
        except Client.DoesNotExist:
            raise CustomException(404, "The client does not exist.")
        except ValidationError:
            raise CustomException(400, "The UUID is not correct.")


class ProjectListCreateView(ListCreateAPIView):
    """
    Get all projects for a user or create a new project
    @permissions - Only the owner can do CUD operations, other users can list the projects
        they're included in
    """
    pagination_class = CustomPaginator

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProjectListSerializer
        else:
            return ProjectCreateUpdateSerializer

    def get_queryset(self):
        return Project.objects.filter(Q(owner=self.request.user) | Q(users=self.request.user))


class ProjectRetrieveView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a project
    @permissions - Only the owner can do CUD operations, other users can retrieve the project
        if they're included in it
    """
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProjectRetrieveSerializer
        else:
            return ProjectCreateUpdateSerializer

    def get_object(self):
        try:
            if self.request.method == "GET":
                return Project.objects.get(
                    Q(owner=self.request.user) | Q(users=self.request.user), id=self.kwargs['id']
                )
            else:
                return Project.objects.get(owner=self.request.user, id=self.kwargs['id'])
        except Project.DoesNotExist:
            raise CustomException(404, "The project does not exist.")
        except ValidationError:
            raise CustomException(400, "The UUID is not correct.")


class ProjectInviteView(APIView):
    """
    This view is for the Project Invites. Add the user to the project.
    """

    def get(self, request, *args, **kwargs):
        try:
            response = accept_project_invite(self.request.user, self.kwargs['id'])
            return JsonResponse(data=response, status=status.HTTP_200_OK)
        except ValidationError:
            raise CustomException(400, "The UUID is not correct.")


class ProjectPostsListCreateView(ListCreateAPIView):
    """
    Get all of the posts for a project or create a new post
    @permissions - Only the owner can do CUD operations, other users can list the posts. The user can create
         a post for a project only if he is the owner, or one of the users.
    """
    serializer_class = ProjectPostSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        try:
            return ProjectPosts.objects.filter(
                Q(project__owner=self.request.user) | Q(project__users=self.request.user),
                project=self.kwargs['project_id']
            )
        except ValidationError:
            raise CustomException(400, "The UUID is not correct.")

    def perform_create(self, serializer):
        try:
            project = Project.objects.get(
                Q(owner=self.request.user) | Q(users=self.request.user), id=self.kwargs['project_id']
            )
            return serializer.save(project=project, owner=self.request.user)
        except Project.DoesNotExist:
            raise CustomException(404, "The project does not exist.")
        except ValidationError:
            raise CustomException(400, "The UUID is not correct.")


class ProjectPostsRetrieveView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a project post
    @permissions - Only the owner can do CUD operations.
    """
    serializer_class = ProjectPostSerializer
    lookup_field = 'id'

    def get_object(self):
        try:
            return ProjectPosts.objects.get(owner=self.request.user, id=self.kwargs['id'])
        except Project.DoesNotExist:
            raise CustomException(404, "The post does not exist.")
        except ValidationError:
            raise CustomException(400, "The UUID is not correct.")


class PostCommentListCreateView(ListCreateAPIView):
    """
    Get all of the comment for a post or create a new comment
    """
    serializer_class = PostCommentSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        return PostComments.objects.filter(
            Q(post__project__owner=self.request.user) | Q(post__project__users=self.request.user),
            post=self.kwargs['post_id']
        )

    def perform_create(self, serializer):
        try:
            post = ProjectPosts.objects.get(
                Q(post__project__owner=self.request.user) | Q(post__project__users=self.request.user),
                id=self.kwargs['post_id']
            )
            return serializer.save(post=post, owner=self.request.user)
        except ProjectPosts.DoesNotExist:
            raise CustomException(404, "The post does not exist.")
        except ValidationError:
            raise CustomException(400, "The UUID is not correct.")


class PostCommentsRetrieveView(RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a project post
    """
    serializer_class = PostCommentSerializer
    lookup_field = 'id'

    def get_object(self):
        try:
            return PostComments.objects.get(
                owner=self.request.user,
                id=self.kwargs['id']
            )
        except ProjectPosts.DoesNotExist:
            raise CustomException(404, "The comment does not exist.")
        except ValidationError:
            raise CustomException(400, "The UUID is not correct.")


class InvoiceListCreateView(ListCreateAPIView):
    """
    Get all invoices or create a new one
    """
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = InvoiceFilter

    def get_serializer_class(self):
        if self.request.method == "GET":
            return InvoiceListSerializer
        else:
            return InvoicePostSerializer

    def get_queryset(self):
        return Invoice.objects.filter(owner=self.request.user)


class InvoiceRetrieveView(RetrieveUpdateDestroyAPIView):
    serializer_class = InvoicePostSerializer
    pagination_class = CustomPaginator
    lookup_field = 'id'

    def get_object(self):
        try:
            return Invoice.objects.get(
                owner=self.request.user,
                id=self.kwargs['id']
            )
        except Invoice.DoesNotExist:
            raise CustomException(404, "The invoice does not exist.")
        except ValidationError:
            raise CustomException(400, "The UUID is not correct.")


class ResumeCreateView(CreateAPIView, RetrieveUpdateDestroyAPIView):
    serializer_class = ResumeSerializer

    def get_object(self):
        return Resume.objects.get(owner=self.request.user)


class TimelineItemListCreateView(ListCreateAPIView):
    serializer_class = TimelineItemClientSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        try:
            return TimelineItemClient.objects.filter(owner=self.request.user, client=self.kwargs['client_id'])
        except ValidationError:
            raise CustomException(400, "The UUID is not correct.")


class TimelineItemRetrieveView(RetrieveUpdateDestroyAPIView):
    serializer_class = TimelineItemClientSerializer
    lookup_field = 'id'

    def get_object(self):
        try:
            return TimelineItemClient.objects.get(
                owner=self.request.user,
                id=self.kwargs['id']
            )
        except TimelineItemClient.DoesNotExist:
            raise CustomException(404, "The timeline item does not exist.")
        except ValidationError:
            raise CustomException(400, "The UUID is not correct.")

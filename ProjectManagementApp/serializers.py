from django.db import IntegrityError
from rest_framework import serializers
from django.core.exceptions import ValidationError
from rest_framework.fields import empty

from AuthenticationApp.serializers import UserSerializer
from FilesApp.serializers import FileSerializer
from FilesApp.services import project_file_size
from ProjectManagementApp.models import Client, Project, ProjectPosts, Invoice, Resume, \
    TimelineItemClient, ClientAddress, PostComments, ProjectInvites
from ProjectManagementApp.services import send_invite_project
from projectmanagement.exceptions import CustomException


class ClientAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientAddress
        fields = ('id', 'country', 'state', 'city', 'zip_code')


class ClientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ('id', 'name', 'email', 'created_at')


class ProjectListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'budget', 'due_date')

    def to_representation(self, instance):
        serializer = super(ProjectListSerializer, self).to_representation(instance)
        if self.context.get('request').user == instance.owner:
            serializer['owner'] = True
            return serializer
            # Else if the user is a client of the project, return only necessary information
        elif self.context.get('request').user in instance.users.all():
            serializer['owner'] = False
            del serializer['budget']
            return serializer


class ClientCreateSerializer(serializers.ModelSerializer):
    address = ClientAddressSerializer(required=False)

    class Meta:
        model = Client
        fields = ('id', 'name', 'email', 'phone', 'address', 'company', 'created_at')

    def create(self, validated_data):
        validated_data['owner'] = self.context.get('request').user
        address = validated_data.pop('address') if validated_data.get('address') else None
        new_client = super(ClientCreateSerializer, self).create(validated_data)
        if address:
            ClientAddress.objects.create(**address, client=new_client)
        else:
            ClientAddress.objects.create(client=new_client)
        return new_client

    def to_representation(self, instance):
        serializer = super(ClientCreateSerializer, self).to_representation(instance)
        if hasattr(instance, 'client_address'):
            serializer['address'] = ClientAddressSerializer(instance.client_address).data
        if self.context.get('request').user.project_owner.all():
            serializer['projects'] = ProjectListSerializer(self.context.get('request').user.project_owner.all(),
                                                           many=True).data
        return serializer


class ClientRetrieveUpdateSerializer(serializers.ModelSerializer):
    address = ClientAddressSerializer(source='client_address', required=False)
    projects = ProjectListSerializer(source='client_projects', many=True, required=False)

    class Meta:
        model = Client
        fields = ('name', 'email', 'phone', 'address', 'company', 'projects', 'created_at')

    def update(self, instance, validated_data):
        if validated_data.get('client_address'):
            serializer = ClientAddressSerializer(instance.client_address, validated_data.pop('client_address'))
            if serializer.is_valid():
                serializer.save()
        return super(ClientRetrieveUpdateSerializer, self).update(instance, validated_data)

    def to_representation(self, instance):
        serializer = super(ClientRetrieveUpdateSerializer, self).to_representation(instance)
        return serializer


class ProjectInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectInvites
        fields = ('email', 'expire_at', 'created_at')


class ProjectRetrieveSerializer(serializers.ModelSerializer):
    clients = ClientListSerializer(many=True)
    users = UserSerializer(many=True)

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'users', 'clients', 'time', 'budget', 'due_date', 'created_at')

    def to_representation(self, instance):
        serializer = super(ProjectRetrieveSerializer, self).to_representation(instance)
        project_files = instance.project_files.all()
        serializer['files'] = FileSerializer(project_files, many=True).data
        serializer['files_size'] = project_file_size(project_files)
        # If object is retrieve by owner, send all information
        if self.context.get('request').user == instance.owner:
            serializer['owner'] = True
            return serializer
        # Else if the user is a client of the project, return only necessary information
        elif self.context.get('request').user in instance.users.all():
            serializer['owner'] = False
            del serializer['budget']
            return serializer


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    clients = serializers.ListField(child=serializers.EmailField(), write_only=True, required=False)
    users = serializers.ListField(child=serializers.EmailField(), write_only=True, required=False)

    class Meta:
        model = Project
        fields = ('id', 'name', 'description', 'users', 'clients', 'time', 'budget', 'due_date', 'created_at')

    def create(self, validated_data):
        clients = None
        emails = None
        validated_data['owner'] = self.context.get('request').user
        if 'clients' in validated_data:
            clients = Client.objects.filter(email__in=validated_data.pop('clients'),
                                            owner=self.context.get('request').user)
        if 'users' in validated_data:
            emails = validated_data.pop('users')
            # Notify users that have been added to the project
        instance = super(ProjectCreateUpdateSerializer, self).create(validated_data)
        if clients:
            instance.clients.add(*clients)
        if emails:
            send_invite_project(emails, instance, self.context.get('request').user)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        clients = None
        if 'clients' in validated_data:
            clients = Client.objects.filter(email__in=validated_data.pop('clients'),
                                            owner=self.context.get('request').user)
        # Notify users that have been added to the project
        if 'users' in validated_data:
            send_invite_project(validated_data.pop('users'), instance, self.context.get('request').user)
        instance = super(ProjectCreateUpdateSerializer, self).update(instance, validated_data)
        instance.clients.clear()
        if clients:
            instance.clients.add(*clients)
        instance.save()
        return instance

    # TODO There might be a need for the user to delete i.e. cancel invites
    def to_representation(self, instance):
        serializer = super(ProjectCreateUpdateSerializer, self).to_representation(instance)
        serializer['owner'] = True
        serializer['users'] = UserSerializer(instance.users, many=True).data
        serializer['clients'] = ClientListSerializer(instance.clients, many=True).data
        serializer['invites'] = ProjectInviteSerializer(ProjectInvites.objects.filter(project=instance), many=True).data
        return serializer


class PostCommentSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.email', read_only=True)

    class Meta:
        model = PostComments
        fields = ('id', 'owner', 'content', 'created_at')


class ProjectPostSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.email', read_only=True)
    comments = PostCommentSerializer(source='comment_post', many=True)

    class Meta:
        model = ProjectPosts
        fields = ('id', 'owner', 'content', 'type', 'created_at', 'comments')


class InvoiceListSerializer(serializers.ModelSerializer):
    client = serializers.CharField(source='client.email')
    project = serializers.CharField(source='project.name')

    class Meta:
        model = Invoice
        fields = ("id", "client", "due_date", "number", "total", "is_paid", "project", 'created_at')


class InvoicePostSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    client = ClientRetrieveUpdateSerializer(read_only=True)

    class Meta:
        model = Invoice
        fields = ("id", 'owner', "client", "due_date", "items", "note", "number", "terms", "total", "is_paid", "project",
                  'created_at')

    def run_validation(self, data=empty):
        try:
            if 'project' in data:
                Project.objects.get(owner=self.context.get('request').user, id=data['project'])
            if 'client' in data:
                Client.objects.get(owner=self.context.get('request').user, id=data['client'])
            return super(InvoicePostSerializer, self).run_validation(data)
        except (Project.DoesNotExist, Client.DoesNotExist):
            raise CustomException(400, "The client or project does not exist.")
        except ValidationError:
            raise CustomException(400, 'The data can not be validated.')

    def create(self, validated_data):
        validated_data["owner"] = self.context.get('request').user
        return super(InvoicePostSerializer, self).create(validated_data)

    def to_representation(self, instance):
        serializer = super(InvoicePostSerializer, self).to_representation(instance)
        project = dict()
        project['name'] = instance.project.name
        project['description'] = instance.project.description
        serializer['project'] = project
        return serializer

class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = ('id', 'name', 'position', 'description', 'languages', 'skills', 'education',
                  'work_experience', 'certificates', 'achievements', 'personal_projects', 'contact_info')

    def create(self, validated_data):
        try:
            validated_data['owner'] = self.context.get('request').user
            return super(ResumeSerializer, self).create(validated_data)
        except IntegrityError:
            raise CustomException(400, "You already have an existing resume.")


class TimelineItemClientSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.email', read_only=True)

    class Meta:
        model = TimelineItemClient
        fields = ('id', 'owner', 'importance', 'title', 'description', 'date', 'created_at')

    def create(self, validated_data):
        validated_data['owner'] = self.context.get('request').user
        try:
            client_id = self.context.get('request').parser_context.get('kwargs').get('client_id')
            client = Client.objects.get(id=client_id, owner=self.context.get('request').user)
        except Client.DoesNotExist:
            raise CustomException(404, "The client was not found.")
        validated_data['client'] = client
        return super(TimelineItemClientSerializer, self).create(validated_data)

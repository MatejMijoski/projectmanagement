from django.db import IntegrityError
from rest_framework import serializers

from AuthenticationApp.serializers import UserSerializer
from FilesApp.serializers import FileSerializer
from FilesApp.services import project_file_size
from ProjectManagementApp.models import (Client, Project, ProjectPosts, Invoice, Resume, TimelineItemClient,
    PostComments, ProjectInvite, )
from ProjectManagementApp.services import send_invite_project
from projectmanagement.exceptions import CustomException


class ClientListSerializer(serializers.ModelSerializer):
    projects_no = serializers.SerializerMethodField()
    invoices_no = serializers.SerializerMethodField()

    class Meta:
        model = Client
        fields = ("id", "name", "email", "address", "phone", "created_at", "projects_no", "invoices_no",)

    def get_projects_no(self, obj):
        return Project.objects.filter(clients=obj).count()

    def get_invoices_no(self, obj):
        return Invoice.objects.filter(client=obj).count()


class ProjectListSerializer(serializers.ModelSerializer):
    clients = ClientListSerializer(many=True)
    users = UserSerializer(many=True)
    owner = UserSerializer()

    class Meta:
        model = Project
        fields = ("id", "name", "clients", "users", "owner", "description", "budget", "due_date",)


class ClientCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ("id", "name", "email", "phone", "address", "company", "created_at",)

    def create(self, validated_data):
        validated_data["owner"] = self.context.get("request").user
        try:
            return super(ClientCreateSerializer, self).create(validated_data)
        except IntegrityError:
            raise CustomException(400, "A client with the specified email already exists.")

    def to_representation(self, instance):
        serializer = super(ClientCreateSerializer, self).to_representation(instance)
        if self.context.get("request").user.project_owner.all():
            serializer["projects"] = ProjectListSerializer(self.context.get("request").user.project_owner.all(),
                many=True, context={"request": self.context.get("request")}, ).data
        return serializer


class InvoiceMinSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ('id', 'total', 'is_paid', 'created_at')


class ClientRetrieveUpdateSerializer(serializers.ModelSerializer):
    projects = ProjectListSerializer(source="client_projects", many=True, read_only=True)
    invoices = InvoiceMinSerializer(source="client_invoices", many=True, read_only=True)
    projects_no = serializers.SerializerMethodField(read_only=True)
    invoices_no = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Client
        fields = (
            "id", "name", "email", "phone", "address", "company", "projects", "invoices", "created_at", "projects_no",
            "invoices_no",)

    def update(self, instance, validated_data):
        try:
            return super(ClientRetrieveUpdateSerializer, self).update(instance, validated_data)
        except IntegrityError:
            raise CustomException(400, "A client with the specified email already exists.")

    def get_projects_no(self, obj):
        return Project.objects.filter(clients=obj).count()

    def get_invoices_no(self, obj):
        return Invoice.objects.filter(client=obj).count()


class ProjectInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectInvite
        fields = ("email", "expire_at", "created_at")


class ProjectRetrieveSerializer(serializers.ModelSerializer):
    clients = ClientListSerializer(many=True)
    users = UserSerializer(many=True)

    class Meta:
        model = Project
        fields = ("id", "name", "description", "users", "clients", "time", "budget", "due_date", "created_at",)

    def to_representation(self, instance):
        serializer = super(ProjectRetrieveSerializer, self).to_representation(instance)
        project_files = instance.project_files.all()
        serializer["files"] = FileSerializer(project_files, many=True).data
        serializer["files_size"] = project_file_size(project_files)
        # If object is retrieved by owner, send all information
        if self.context.get("request").user == instance.owner:
            serializer["owner"] = True
            return serializer
        # Else if the user is a client of the project, return only necessary information
        elif self.context.get("request").user in instance.users.all():
            serializer["owner"] = False
            del serializer["budget"]
            return serializer


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    clients = serializers.ListField(child=serializers.EmailField(), write_only=True, required=False)
    users = serializers.ListField(child=serializers.EmailField(), write_only=True, required=False)

    class Meta:
        model = Project
        fields = ("id", "name", "description", "users", "clients", "time", "budget", "due_date", "created_at",)

    def create(self, validated_data):
        clients = None
        emails = None
        validated_data["owner"] = self.context.get("request").user
        if "clients" in validated_data:
            clients = Client.objects.filter(email__in=validated_data.pop("clients"),
                owner=self.context.get("request").user, )
        if "users" in validated_data:
            emails = validated_data.pop("users")  # Notify users that have been added to the project
        try:
            instance = super(ProjectCreateUpdateSerializer, self).create(validated_data)
            if clients:
                instance.clients.add(*clients)
            if emails:
                send_invite_project(emails, instance, self.context.get("request").user)
            instance.save()
            return instance
        except IntegrityError:
            raise CustomException(400, "A project with the specified name already exists.")

    def update(self, instance, validated_data):
        clients = None
        if "clients" in validated_data:
            clients = Client.objects.filter(email__in=validated_data.pop("clients"),
                owner=self.context.get("request").user, )
        # Notify users that have been added to the project
        if "users" in validated_data:
            send_invite_project(validated_data.pop("users"), instance, self.context.get("request").user)
        try:
            instance = super(ProjectCreateUpdateSerializer, self).update(instance, validated_data)
            instance.clients.clear()
            if clients:
                instance.clients.add(*clients)
            instance.save()
            return instance
        except IntegrityError:
            raise CustomException(400, "A project with the specified name already exists.")

    # TODO There might be a need for the user to delete i.e. cancel invites
    def to_representation(self, instance):
        serializer = super(ProjectCreateUpdateSerializer, self).to_representation(instance)
        serializer["owner"] = True
        serializer["users"] = UserSerializer(instance.users, many=True).data
        serializer["clients"] = ClientListSerializer(instance.clients, many=True).data
        serializer["invites"] = ProjectInviteSerializer(ProjectInvite.objects.filter(project=instance), many=True).data
        return serializer


class PostCommentSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.email", read_only=True)

    class Meta:
        model = PostComments
        fields = ("id", "owner", "content", "created_at")


class ProjectPostSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.email", read_only=True)
    comments = PostCommentSerializer(source="comment_post", many=True)

    class Meta:
        model = ProjectPosts
        fields = ("id", "owner", "content", "type", "created_at", "comments")


class ProjectInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ("id", "name")


class ClientInvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ("id", "name", "email")


class InvoiceCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = (
            "id", "name_surname", "email", "address", "company_name", "phone", "due_date", "items", "client", "project",
            "note", "number", "terms", "total", "is_paid", "created_at",)

    def create(self, validated_data):
        validated_data["owner"] = self.context.get("request").user
        try:
            return super(InvoiceCreateUpdateSerializer, self).create(validated_data)
        except (Project.DoesNotExist, Client.DoesNotExist):
            raise CustomException(400, "The client or project does not exist.")

    def to_representation(self, instance):
        serializer = super(InvoiceCreateUpdateSerializer, self).to_representation(instance)
        if instance.client:
            serializer["client"] = ClientInvoiceSerializer(instance.client).data
        if instance.project:
            serializer["project"] = ProjectInvoiceSerializer(instance.project).data
        return serializer


class InvoiceSerializer(serializers.ModelSerializer):
    client = ClientInvoiceSerializer(read_only=True)
    project = ProjectInvoiceSerializer(read_only=True)

    class Meta:
        model = Invoice
        fields = (
            "id", "name_surname", "email", "address", "company_name", "phone", "due_date", "items", "client", "project",
            "note", "number", "terms", "total", "is_paid", "created_at",)


class ResumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resume
        fields = (
        "id", "name", "position", "description", "languages", "skills", "education", "work_experience", "certificates",
        "achievements", "personal_projects", "contact_info",)

    def create(self, validated_data):
        try:
            validated_data["owner"] = self.context.get("request").user
            return super(ResumeSerializer, self).create(validated_data)
        except IntegrityError:
            raise CustomException(400, "You already have an existing resume.")


class TimelineItemClientSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.email", read_only=True)

    class Meta:
        model = TimelineItemClient
        fields = ("id", "owner", "importance", "client", "title", "description", "date", "created_at",)

    def create(self, validated_data):
        validated_data["owner"] = self.context.get("request").user
        try:
            client_id = (self.context.get("request").parser_context.get("kwargs").get("client_id"))
            client = Client.objects.get(id=client_id, owner=self.context.get("request").user)
        except Client.DoesNotExist:
            raise CustomException(404, "The client was not found.")
        validated_data["client"] = client
        return super(TimelineItemClientSerializer, self).create(validated_data)

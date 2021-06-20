import unittest
import uuid
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from AuthenticationApp.models import Account
from ProjectManagementApp.models import Client, Project, ProjectInvite
from ProjectManagementApp.serializers import ClientListSerializer, ProjectListSerializer


# Create your tests here.
class ClientTests(APITestCase):
    client = APIClient()
    url = "http://127.0.0.1:8000/api/clients/"

    def setUp(self):
        user = Account(email="test@admin.com")
        password = "testpassword1"
        user.set_password(password)
        user.save()

        user_test = Account(email="test@test.com")
        password = "testpassword1"
        user_test.set_password(password)
        user_test.save()

        self.user = user
        self.user_test = user_test
        self.client.force_authenticate(user=user)
        Client.objects.create(
            owner=user,
            name="Test Client",
            email="email@email.com",
            phone="Test phone",
            company="Test Company",
        )
        Client.objects.create(
            owner=user,
            name="Test Client 2 ",
            email="email2@email.com",
            phone="Test phone 2",
            company="Test Company 2",
        )
        Client.objects.create(
            owner=user,
            name="Test Client 3",
            email="email3@email.com",
            phone="Test phone 3",
            company="Test Company 3",
        )
        Client.objects.create(
            owner=user_test,
            name="Test Client 3",
            email="email3@test.com",
            phone="Test phone 3",
            company="Test Company 3",
        )

    def test_get_all_clients(self):
        """
        Check whether a user can retrieve all clients (on which he is the owner of)
        :return: 200 and the serializer data should not be the same from the response i.e. 1 less client
        """
        response = self.client.get(self.url)
        serializer = ClientListSerializer(Client.objects.all(), many=True)
        self.assertNotEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_client_by_owner(self):
        """
        Clients can only be retrieved by their owners
        :return: 200 OK and list of clients
        """
        response = self.client.get(self.url)
        serializer = ClientListSerializer(
            Client.objects.filter(owner=self.user), many=True
        )
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_client_not_found(self):
        """
        Test the error message when a client doesn't exist
        :return: 404, 'The client does not exist.'
        """
        response = self.client.get(self.url + str(uuid.uuid4()))
        self.assertEqual(response.data["error"], "The client does not exist.")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_client_uuid_not_correct(self):
        """
        Check wether the UUID when retrieving a client is correct
        :return: 400, 'The UUID is not correct'
        """
        response = self.client.get(self.url + str(uuid.uuid4())[1:])  # Shortened UUID
        self.assertEqual(response.data["error"], "The UUID is not correct.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_new_client(self):
        """
        Create a new client with valid data
        :return:
        """
        data = {
            "name": "Test Client 4",
            "email": "email4@email.com",
            "phone": "1234567",
            "company": "Test Company 4",
            "address": "Test Address",
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(Client.objects.filter(owner=self.user).count(), 4)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_client_integrity_error(self):
        """
        Test for the constraint of clients owner and email i.e. one user can't have multiple clients with the same email
        :return: 400, "A client with the specified email already exists"
        """
        data = {
            "name": "Test Client 4",
            "email": "email3@email.com",
            "phone": "1234567",
            "company": "Test Company 4",
            "address": "Test Address",
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"], "A client with the specified email already exists."
        )

    def test_create_client_required_email(self):
        """
        Test for the required email field in the serializer
        :return: 400 Bad Request with "This field is required" for email
        """
        data = {
            "name": "Test Client 4",
            "phone": "1234567",
            "company": "Test Company 4",
            "address": "Test Address",
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data["email"][0]), "This field is required.")

    def test_create_client_owner(self):
        """
        Test whether the owner is properly entered in the serializer
        :return: 200 OK
        """
        data = {
            "name": "Test Client 4",
            "email": "email4@email.com",
            "phone": "1234567",
            "company": "Test Company 4",
            "address": "Test Address",
        }
        response = self.client.post(self.url, data=data, format="json")
        new_client = Client.objects.get(id=response.data["id"])
        self.assertEqual(new_client.owner, self.user)

    def test_update_client(self):
        """
        Update a client with new valid information
        :return: 200
        """
        data = {
            "name": "Updated Client Name",
            "email": "email4@email.com",
            "phone": "1234567",
            "company": "Test Company 4",
            "address": "Test Address",
        }
        client = Client.objects.all().first()
        response = self.client.put(self.url + str(client.id), data=data, format="json")
        self.assertEqual(response.data["name"], "Updated Client Name")
        self.assertEqual(Client.objects.get(id=client.id).name, "Updated Client Name")

    def test_update_client_email_integrity(self):
        """
        Update an existing clients email with an email that also already exists for another client
        :return: 400 Bad Request with "A client with the specified email already exists"
        """
        data = {
            "name": "Updated Client Name",
            "email": "email2@email.com",
            "phone": "1234567",
            "company": "Test Company 4",
            "address": "Test Address",
        }
        client = Client.objects.all().first()
        response = self.client.put(self.url + str(client.id), data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"], "A client with the specified email already exists."
        )

    def test_get_client_with_random_user(self):
        """
        Get a client by user which is not the owner of the client object
        :return: 404 Not Found
        """
        data = {
            "name": "Updated Client Name",
            "email": "email10@email.com",
            "phone": "1234567",
            "company": "Test Company 4",
            "address": "Test Address",
        }
        new_client = Client.objects.create(**data, owner=self.user_test)
        response = self.client.put(
            self.url + str(new_client.id), data=data, format="json"
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class ProjectTests(APITestCase):
    client = APIClient()
    url = "http://127.0.0.1:8000/api/projects/"

    def setUp(self):
        user = Account(email="test@admin.com")
        password = "testpassword1"
        user.set_password(password)
        user.save()

        user_test = Account(email="test@test.com")
        password = "testpassword1"
        user_test.set_password(password)
        user_test.save()

        self.user = user
        self.user_test = user_test
        self.client.force_authenticate(user=user)
        Project.objects.create(
            owner=user, name="Test Project", description="Description", time=20
        )
        Project.objects.create(
            owner=user, name="Test Project 2 ", description="Description", time=20
        )
        Project.objects.create(
            owner=user, name="Test Project 3", description="Description", time=20
        )
        Project.objects.create(
            owner=user_test, name="Test Project 3", description="Description", time=20
        )
        Client.objects.create(
            owner=user,
            name="Test Client 2 ",
            email="client@email.com",
            phone="Test phone 2",
            company="Test Company 2",
        )

    def test_get_all_projects(self):
        """
        Check whether a user can retrieve all projects (of which he is the owner of)
        :return:
        """
        response = self.client.get(self.url)
        serializer = ProjectListSerializer(Project.objects.all(), many=True)
        self.assertNotEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 3)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_project_not_found(self):
        """
        Test the error message when a project doesn't exist
        :return: 404, 'The project does not exist.'
        """
        response = self.client.get(self.url + str(uuid.uuid4()))
        self.assertEqual(response.data["error"], "The project does not exist.")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_project_uuid_not_correct(self):
        """
        Check whether the UUID when retrieving a project is correct
        :return: 400, 'The UUID is not correct'
        """
        response = self.client.get(self.url + str(uuid.uuid4())[1:])  # Shortened UUID
        self.assertEqual(response.data["error"], "The UUID is not correct.")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_new_project(self):
        """
        Create a new project with valid data
        :return: 201
        """
        date = timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%f" + "Z")
        data = {
            "name": "Test Project 4",
            "description": "Project Description",
            "time": 123,
            "budget": 20,
            "due_date": date,
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "Test Project 4")
        self.assertEqual(response.data["description"], "Project Description")
        self.assertEqual(response.data["time"], 123)
        self.assertEqual(response.data["budget"], 20)
        self.assertEqual(response.data["due_date"], date)

    def test_create_new_project_with_users(self):
        """
        Create a new project with valid data and users
        :return:
        """
        date = timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%f" + "Z")
        data = {
            "name": "Test Project 4",
            "description": "Project Description",
            "time": 123,
            "budget": 20,
            "due_date": date,
            "users": [
                self.user_test.email,
            ],
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(ProjectInvite.objects.filter(sender=self.user).count(), 1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_new_project_with_clients(self):
        """
        Create a new project with valid data and clients
        :return:
        """
        date = timezone.now().strftime("%Y-%m-%dT%H:%M:%S.%f" + "Z")
        data = {
            "name": "Test Project 6",
            "description": "Project Description",
            "time": 123,
            "budget": 20,
            "due_date": date,
            "clients": [
                "client@email.com",
            ],
        }
        response = self.client.post(self.url, data=data, format="json")
        project = Project.objects.get(id=response.data["id"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(project.clients.all().count(), 1)

    def test_create_project_integrity_error(self):
        """
        Test for the constraint of project owner and email i.e. one user can't have multiple projects with the same name
        :return: 400, "A project with the specified name already exists"
        """
        data = {
            "name": "Test Project",
            "description": "Project Description",
            "time": 123,
            "budget": 20,
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"], "A project with the specified name already exists."
        )

    def test_create_project_required_name(self):
        """
        Test for the required email field in the serializer
        :return: 400 Bad Request with "This field is required" for email
        """
        data = {
            "description": "Project Description",
            "time": 123,
            "budget": 20,
        }
        response = self.client.post(self.url, data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(str(response.data["name"][0]), "This field is required.")

    def test_create_project_owner(self):
        """
        Test whether the owner is properly entered in the serializer
        :return: 200 OK
        """
        data = {
            "name": "Test Project 5",
            "description": "Project Description",
            "time": 123,
            "budget": 20,
        }
        response = self.client.post(self.url, data=data, format="json")
        new_project = Project.objects.get(id=response.data["id"])
        self.assertEqual(new_project.owner, self.user)

    def test_update_project(self):
        """
        Update a project with new valid information
        :return: 200
        """
        data = {
            "name": "Updated Project Name",
            "description": "Project Description",
            "time": 123,
            "budget": 20,
        }
        project = Project.objects.all().first()
        response = self.client.put(self.url + str(project.id), data=data, format="json")
        self.assertEqual(response.data["name"], "Updated Project Name")
        self.assertEqual(
            Project.objects.get(id=project.id).name, "Updated Project Name"
        )

    def test_update_project_name_integrity(self):
        """
        Update an existing projects name with an name that also already exists for another project
        :return: 400 Bad Request with "A project with the specified name already exists."
        """
        data = {
            "name": "Test Project",
            "description": "Project Description",
            "time": 123,
            "budget": 20,
        }
        project = Project.objects.all().first()
        response = self.client.put(self.url + str(project.id), data=data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["error"], "A project with the specified name already exists."
        )

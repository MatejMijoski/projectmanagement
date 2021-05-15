from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.test import APITestCase, APIClient

from AuthenticationApp.models import Account
from ProjectManagementApp.models import Client
from ProjectManagementApp.serializers import ClientListSerializer


# Create your tests here.
class ClientTests(APITestCase):
    def setUp(self):
        user = Account(email="test@admin.com")
        password = 'testpassword1'
        user.set_password(password)
        user.save()
        self.client = APIClient()
        self.client.force_authenticate(user=user)
        Client.objects.create(owner=user, name="Test Client", email='email@email.com', phone='Test phone',
                              company='Test Company')
        Client.objects.create(owner=user, name="Test Client 2 ", email='email2@email.com', phone='Test phone 2',
                              company='Test Company 2')
        Client.objects.create(owner=user, name="Test Client 3", email='email3@email.com', phone='Test phone 3',
                              company='Test Company 3')

    def testGetAllClients(self):
        response = self.client.get('http://127.0.0.1:8000/api/client/')
        clients = Client.objects.all()
        serializer = ClientListSerializer(clients, many=True)
        self.assertEqual(response.data['results'], serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def testCreateNewClient(self):
        data = {
            "name": "Test Client 4",
            "email": "test@email4.com",
            "phone": "1234567",
            "company": "Test Company 4",
            "address": {
                "country": "test",
                "state": "test",
                "city": "test",
                "zip_code": "test"
            }
        }
        response = self.client.post('http://127.0.0.1:8000/api/client/', data=data, format='json')
        self.assertEqual(Client.objects.all().count(), 4)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def testIntegrityConstraintEmail(self):
        data = {
            "name": "Test Client 4",
            "email": "email3@email.com",
            "phone": "1234567",
            "company": "Test Company 4",
            "address": {
                "country": "test",
                "state": "test",
                "city": "test",
                "zip_code": "test"
            }
        }
        response = self.client.post('http://127.0.0.1:8000/api/client/', data=data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], "A client with the specified email already exists.")

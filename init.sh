# User credentials
email=test@test.com
password=testpassword

python3 manage.py migrate
echo "from AuthenticationApp.models import User; Account.objects.create_superuser('$email', '$password')" | python3 manage.py shell
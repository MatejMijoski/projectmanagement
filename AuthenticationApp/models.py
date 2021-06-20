from allauth.account.signals import email_confirmed
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.dispatch import receiver


# Create your models here.
class AccountManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class Account(AbstractUser):
    username = None
    email = models.EmailField(verbose_name="E-mail", max_length=40, unique=True)
    name_surname = models.CharField(max_length=50, verbose_name="Name and Surname")
    address = models.CharField(max_length=150, verbose_name="Address")
    company_name = models.CharField(max_length=50, verbose_name="Company Name")
    phone = models.CharField(max_length=50, verbose_name="Phone Number")
    is_freelancer = models.BooleanField(default=False, verbose_name="Freelancer")
    is_client = models.BooleanField(default=False, verbose_name="Client")
    email_verified = models.BooleanField(default=False, verbose_name="Is Verified")

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["is_freelancer", "is_client"]

    objects = AccountManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True


@receiver(email_confirmed)
def email_confirmed_(request, email_address, **kwargs):
    user = email_address.user
    user.email_verified = True
    user.save()

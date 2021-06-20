from dj_rest_auth.registration.serializers import (
    RegisterSerializer,
    SocialLoginSerializer,
)
from rest_framework import serializers
from AuthenticationApp.models import Account


class CustomRegisterSerializer(RegisterSerializer):
    is_freelancer = serializers.BooleanField(write_only=True, required=True)
    is_client = serializers.BooleanField(write_only=True, required=True)

    def get_cleaned_data(self):
        data_dict = super().get_cleaned_data()
        data_dict["is_freelancer"] = self.validated_data.get("is_freelancer", False)
        data_dict["is_client"] = self.validated_data.get("is_client", False)

        return data_dict

    def get_email_options(self):
        request = self.context.get("request")
        return {
            "use_https": request.is_secure(),
            "from_email": "Name of App <info@name.com>",
            "html_email_template_name": "account/email/email_confirmation_message.html",
        }


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ["id", "email", "name_surname", "phone", "address", "company_name"]

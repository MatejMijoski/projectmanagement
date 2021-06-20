from django.contrib import admin

# Register your models here.
from django.contrib.auth.admin import UserAdmin

from AuthenticationApp.models import Account
from django import forms


class UserCreationForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ("email", "email_verified", "is_freelancer", "is_client")

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class CustomUserAdmin(UserAdmin):
    # The forms to add and change user instances
    add_form = UserCreationForm
    list_display = ("pk", "email", "email_verified", "is_freelancer", "is_client")
    ordering = ("email",)

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "email",
                    "name_surname",
                    "address",
                    "company_name",
                    "phone",
                    "password",
                    "is_freelancer",
                    "is_client",
                    "email_verified",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "name_surname",
                    "address",
                    "company_name",
                    "phone",
                    "password",
                    "is_superuser",
                    "is_staff",
                    "is_active",
                    "email_verified",
                ),
            },
        ),
    )

    filter_horizontal = ()


admin.site.register(Account, CustomUserAdmin)

from allauth.account.adapter import DefaultAccountAdapter


class CustomAccountAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=True):
        user = super().save_user(request, user, form, commit)
        data = form.cleaned_data
        user.is_freelancer = data.get("is_freelancer")
        user.is_client = data.get("is_client")
        user.save()
        return user

    def get_email_confirmation_url(self, request, emailconfirmation):
        return f"http://127.0.0.1:8000/account/register/verify/{emailconfirmation.key}"

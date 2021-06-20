from django.db import models

# Create your models here.
from AuthenticationApp.models import Account


class Slack_Auth(models.Model):
    objects: models.Manager()
    slack_id = models.AutoField(primary_key=True)
    slack_account = models.OneToOneField(Account, on_delete=models.CASCADE, null=True)
    user_id = models.CharField(max_length=50)
    access_token = models.CharField(max_length=200)
    team_id = models.CharField(max_length=50)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user_id", "team_id"], name="Slack Constraint"
            ),
        ]


# Ne znam dali e potreben ovoj model
# class Slack_Auth_Perm(models.Model):
#     objects: models.Manager()
#     slack_account = models.OneToOneField(Account, on_delete=models.CASCADE)
#     slack_account_channel = models.ForeignKey(Slack_Auth, on_delete=models.CASCADE)
#     channel_id = models.CharField(max_length=150)
#


class WSS_Auth(models.Model):
    objects: models.Manager()
    wss_auth_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    user_uid = models.CharField(max_length=150)

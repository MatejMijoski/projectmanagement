# Generated by Django 3.1.5 on 2021-05-07 21:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="WSS_Auth",
            fields=[
                ("wss_auth_id", models.AutoField(primary_key=True, serialize=False)),
                ("user_uid", models.CharField(max_length=150)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Slack_Auth",
            fields=[
                ("slack_id", models.AutoField(primary_key=True, serialize=False)),
                ("user_id", models.CharField(max_length=50)),
                ("access_token", models.CharField(max_length=200)),
                ("team_id", models.CharField(max_length=50)),
                (
                    "slack_account",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddConstraint(
            model_name="slack_auth",
            constraint=models.UniqueConstraint(
                fields=("user_id", "team_id"), name="Slack Constraint"
            ),
        ),
    ]

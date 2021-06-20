from django.core.exceptions import ValidationError
from rest_framework import serializers
from LeadApp.models import Lead, TimelineItemLead
from projectmanagement.exceptions import CustomException


class LeadSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.email", read_only=True)

    class Meta:
        model = Lead
        fields = ("id", "owner", "name", "address", "email", "phone", "created_at")

    def create(self, validated_data):
        validated_data["owner"] = self.context.get("request").user
        return super(LeadSerializer, self).create(validated_data)


class TimelineItemLeadsSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source="owner.email", read_only=True)

    class Meta:
        model = TimelineItemLead
        fields = ("id", "owner", "title", "description", "date", "created_at")

    def create(self, validated_data):
        validated_data["owner"] = self.context.get("request").user
        try:
            lead_id = (
                self.context.get("request").parser_context.get("kwargs").get("lead_id")
            )
            lead = Lead.objects.get(owner=self.context.get("request").user, id=lead_id)
            validated_data["lead"] = lead
        except Lead.DoesNotExist:
            raise CustomException(404, "The lead was not found.")
        except ValidationError:
            raise CustomException(400, "The UUID is not valid.")
        return super(TimelineItemLeadsSerializer, self).create(validated_data)

    def update(self, instance, validated_data):
        validated_data["lead"] = instance.lead
        return super(TimelineItemLeadsSerializer, self).update(instance, validated_data)

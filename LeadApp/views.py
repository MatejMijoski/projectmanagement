from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

from LeadApp.models import Lead, TimelineItemLead
from LeadApp.serializers import LeadSerializer, TimelineItemLeadsSerializer
from projectmanagement.exceptions import CustomException
from projectmanagement.paginator import CustomPaginator


# Create your views here.
class LeadListCreateView(ListCreateAPIView):
    serializer_class = LeadSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        return Lead.objects.filter(owner=self.request.user)


class LeadRetrieveView(RetrieveUpdateDestroyAPIView):
    serializer_class = LeadSerializer
    lookup_field = "id"

    def get_object(self):
        try:
            return Lead.objects.get(owner=self.request.user, id=self.kwargs["id"])
        except Lead.DoesNotExist:
            raise CustomException(404, "The lead does not exist.")
        except ValidationError:
            raise CustomException(400, "The UUID is not correct.")


class TimelineItemListCreateView(ListCreateAPIView):
    serializer_class = TimelineItemLeadsSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        return TimelineItemLead.objects.filter(owner=self.request.user)


class TimelineItemRetrieveView(RetrieveUpdateDestroyAPIView):
    serializer_class = TimelineItemLeadsSerializer
    lookup_field = "id"

    def get_object(self):
        try:
            return TimelineItemLead.objects.get(
                owner=self.request.user, id=self.kwargs["id"]
            )
        except TimelineItemLead.DoesNotExist:
            raise CustomException(404, "The timeline item does not exist.")
        except TimelineItemLead:
            raise CustomException(400, "The UUID is not correct.")

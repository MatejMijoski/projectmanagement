from django_filters import rest_framework as filters

from ProjectManagementApp.models import Invoice, Client


class ClientFilter(filters.FilterSet):
    email = filters.CharFilter(field_name='email', lookup_expr='icontains')

    class Meta:
        model = Client
        fields = ('email',)


class InvoiceFilter(filters.FilterSet):
    status = filters.BooleanFilter(field_name='is_paid', lookup_expr='exact')
    client = filters.CharFilter(field_name='client__name', lookup_expr='icontains')

    class Meta:
        model = Invoice
        fields = ('status', 'client')

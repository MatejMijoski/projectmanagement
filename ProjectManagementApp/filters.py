from django_filters import rest_framework as filters

from ProjectManagementApp.models import Invoice


class InvoiceFilter(filters.FilterSet):
    project = filters.CharFilter(field_name='project', lookup_expr='exact')
    client = filters.CharFilter(field_name='client', lookup_expr='exact')

    class Meta:
        model = Invoice
        fields = ('project', 'client')


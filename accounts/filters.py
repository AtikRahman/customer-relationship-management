import django_filters
from .models import Order
from django_filters import DateFilter

class OrderFilter(django_filters.FilterSet):
    start_date = DateFilter(field_name='date_created', lookup_expr='gte') #gte=greater than equal
    end_date = DateFilter(field_name='date_created', lookup_expr='lte')
    # note = django_filters.CharFilter(field_name='note', lookup_expr='icontains')
    # icontains: case-insensitive containment
    class Meta:
        model = Order
        fields = '__all__'
        exclude = ['customer']
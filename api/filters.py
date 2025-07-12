import django_filters

from api.models import Order, Product
from rest_framework import filters


class ProductFilter(django_filters.FilterSet):
    class Meta:
        model = Product
        # fields = ["name", "price"]
        fields = {
            "name": ["iexact", "icontains"],
            "price": ["exact", "lt", "gt", "lte", "gte", "range"],
        }


class InStockFilterBackend(filters.BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        return queryset.filter(stock__gt=0)  # Filter where stock > 0
        # return queryset.exclude(stock__gt=0) # Filter where stock is 0


class OrderFilter(django_filters.FilterSet):
    created_at = django_filters.DateFilter(
        field_name="created_at__date"
    )  # Extract the YYYY-MM-DD part of the created_at passed to the filter and use it to filter the orders

    class Meta:
        model = Order
        fields = {"status": ["exact"], "created_at": ["lt", "gt", "exact"]}

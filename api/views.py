from typing import Any

from django.db.models import Max, QuerySet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.filters import InStockFilterBackend, ProductFilter
from api.models import Order, OrderItem, Product
from api.serializers import OrderSerializer, ProductInfoSerializer, ProductSerializer
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination

"""
Class Base Generic Views
"""


# List and Create Product


# class ProductListCreateAPIView(generics.ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     filterset_fields = ["name", "price"]  # Filtering by name and price

#     def get_permissions(self):
#         self.permission_classes = [AllowAny]
#         if self.request.method == "POST":
#             self.permission_classes = [IsAdminUser]
#         return super().get_permissions()


class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.order_by("pk")
    serializer_class = ProductSerializer
    filterset_class = ProductFilter
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
        # InStockFilterBackend,
    ]
    search_fields = [
        "name",
        "description",
    ]  # To exactly match the name, add = before the name (['=name', 'description'])
    ordering_fields = ["name", "price", "stock"]
    # pagination_class = LimitOffsetPagination
    pagination_class = PageNumberPagination
    pagination_class.page_size = 2
    pagination_class.page_query_param = 'pagenum'
    pagination_class.page_size_query_param = 'size'
    pagination_class.max_page_size = 4

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):

        return (
            # super().get_queryset().filter(stock__gt=0) # Filter where stock > 0
            super().get_queryset()
        )


# class ProductDetailAPIView(generics.RetrieveAPIView):
class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = "product_id"

    def get_permissions(self):
        self.permission_classes = [AllowAny]
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()


class OrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related("items__product", "user")
    serializer_class = OrderSerializer


class UserOrderListAPIView(generics.ListAPIView):
    queryset = Order.objects.prefetch_related("items__product", "user")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    # Override get_queryset to filter orders by the current user
    def get_queryset(self):
        qs = super().get_queryset()  ## Start with the base queryset defined above

        return qs.filter(user=self.request.user)


"""
Class Base API View
"""


class ProductInfoAPIView(APIView):
    def get(self, request):
        products = Product.objects.all()
        serializer = ProductInfoSerializer(
            {
                "products": products,
                "count": len(products),
                "max_price": products.aggregate(max_price=Max("price"))["max_price"],
            }
        )
        return Response(serializer.data)

    # Continue from Video 20

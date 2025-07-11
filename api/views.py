from typing import Any

from django.db.models import Max, QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Order, OrderItem, Product
from api.serializers import OrderSerializer, ProductInfoSerializer, ProductSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

"""
Class Base Generic Views
"""


# List and Create Product


# class ProductListCreateAPIView(generics.ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     filterset_fields = ("name", "price") # Filtering by name and price

#     def get_permissions(self):
#         self.permission_classes = [AllowAny]
#         if self.request.method == "POST":
#             self.permission_classes = [IsAdminUser]
#         return super().get_permissions()


# class ProductListCreateAPIView(generics.ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer
#     filterset_fields = ("name", "price") # Filtering by name and price

#     def get_permissions(self):
#         # self.permission_classes = [AllowAny]
#         if self.request.method == "POST":
#             self.permission_classes = [IsAdminUser]
#         return super().get_permissions()

#     # Overide the list method to return product where stock > 0
#     def list(self, request, *args, **kwargs):
#         queryset = self.get_queryset().filter(stock__gt=0)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)


class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filterset_fields = (
        "name",
        "price",
    )  # This enables filtering via ?name=...&price=...

    def get_permissions(self):
        if self.request.method == "POST":
            self.permission_classes = [IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):

        return (
            super().get_queryset().filter(stock__gt=0)
        )  # Apply stock filter here so filters and pagination still work


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
    
    # Continue from Video 16

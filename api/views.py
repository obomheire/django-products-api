from django.db.models import Max
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Order, OrderItem, Product
from api.serializers import OrderSerializer, ProductInfoSerializer, ProductSerializer

"""
Class Base Generic Views
"""


# # Use for Listing all products
# class ProductListAPIView(generics.ListAPIView):
#     # queryset = Product.objects.all() # Return all products
#     # queryset = Product.objects.exclude(
#     #     stock__gt=0
#     # )  # Return products that are out of stock i.e where stock is 0
#     queryset = Product.objects.filter(stock__gt=0)  # Return products where stock is > 0
#     serializer_class = ProductSerializer

# Use for Listing andf creating products
class ProductListCreateAPIView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductDetailAPIView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    lookup_url_kwarg = "product_id"


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

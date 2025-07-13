from typing import Any

from django.db.models import Max, QuerySet
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, viewsets
from rest_framework.decorators import action, api_view
from rest_framework.pagination import LimitOffsetPagination, PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from api.filters import InStockFilterBackend, OrderFilter, ProductFilter
from django.views.decorators.vary import vary_on_headers
from api.models import Order, OrderItem, Product, User
from rest_framework.throttling import ScopedRateThrottle
from api.serializers import (
    OrderCreateSerializer,
    OrderSerializer,
    ProductInfoSerializer,
    ProductSerializer,
    UserSerializer,
)

"""
Class Base Generic Views
"""

# List of users
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = None


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
    throttle_scope = "products" # To throttle the requests for products
    throttle_classes = [ScopedRateThrottle] # This could also be done in the settings.py file globally
    # queryset = Product.objects.all()
    queryset = Product.objects.order_by(
        "pk"
    )  # To solve :  UnorderedObjectListWarning: Pagination may yield inconsistent results with an unordered object_list: <class 'api.models.Product'> QuerySet.
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
    pagination_class.page_query_param = "pagenum"
    pagination_class.page_size_query_param = "size"
    pagination_class.max_page_size = 4


# docker run --name django-redis -d -p 6379:6379 --rm redis # To run the redis container
# docker ps # To check if the redis container is running

    # Overriding the list method to cache the product list for 15 minutes (60 * 15 = 900 seconds = 15 minutes)
    @method_decorator(cache_page(60 * 15, key_prefix='product_list'))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    # Delay for 2 seconds to simulate a slow query (for testing the cache)
    def get_queryset(self):
        import time
        time.sleep(2)
        return super().get_queryset()   
 
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


# class OrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related(
#         "items__product", "user"
#     )  # Also prefetch related objects to avoid N+1 queries
#     serializer_class = OrderSerializer


# class UserOrderListAPIView(generics.ListAPIView):
#     queryset = Order.objects.prefetch_related(
#         "items__product", "user"
#     )  # Also prefetch related objects to avoid N+1 queries
#     serializer_class = OrderSerializer
#     permission_classes = [IsAuthenticated]

#     # Override get_queryset to filter orders by the current user
#     def get_queryset(self):
#         qs = super().get_queryset()  ## Start with the base queryset defined above

#         return qs.filter(user=self.request.user)


"""
Class Base ViewSet (ViewSet allows creation of CRUD operations in a single class)
"""


class OrderViewSet(viewsets.ModelViewSet):
    throttle_scope = "orders" # To throttle the requests for orders
    throttle_classes = [ScopedRateThrottle] # This could also be done in the settings.py file globally
    # queryset = Order.objects.prefetch_related("items__product")
    queryset = Order.objects.prefetch_related("items__product").order_by(
        "pk"
    )  # To solve :  UnorderedObjectListWarning: Pagination may yield inconsistent results with an unordered object_list: <class 'api.models.Order'> QuerySet.
    serializer_class = OrderSerializer
    # permission_classes = [AllowAny] # To allow the access to the CRUD operations on the orders endpoint to any user
    permission_classes = [
        IsAuthenticated
    ]  # To restrict the access to the CRUD operations on the orders endpoint to only authenticated users
    pagination_class = None
    filterset_class = OrderFilter
    filter_backends = [DjangoFilterBackend]

    @method_decorator(cache_page(60 * 15, key_prefix='order_list'))
    @method_decorator(vary_on_headers("Authorization")) # To vary the cache based on the Authorization header
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)   

    # Pass the current user to the serializer
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        # Can also check if POST: if self.request.method == 'POST'
        # Can also check if PUT or PATCH: if self.request.method in ['PUT', 'PATCH']
        if self.action == "create" or self.action == "update":
            return OrderCreateSerializer
        return super().get_serializer_class()

    # Allow admin to perform CRUD operations on all orders, and users to perform CRUD operations on their own orders
    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_staff:
            qs = qs.filter(user=self.request.user)
        return qs

    # @action(
    #     detail=False,
    #     methods=["get"],
    #     url_path="user-orders",
    #     # permission_classes=[IsAuthenticated], # To restrict the access to the user-orders endpoint to only authenticated users
    # )
    # def user_orders(self, request):
    #     orders = self.get_queryset().filter(user=request.user)
    #     serializer = self.get_serializer(orders, many=True)
    #     return Response(serializer.data)


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

        # Continue from Video 29

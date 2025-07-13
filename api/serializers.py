from rest_framework import serializers
from django.db import transaction
from .models import Order, OrderItem, Product, User


# List of users serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "email")  # customize as needed


# List and create products serializerg
class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            "id",
            "product_id",
            "description",
            "name",
            "price",
            "stock",
        )

    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0.")
        return value

# List of order items serializer
class OrderItemSerializer(serializers.ModelSerializer):
    # product = ProductSerializer()
    product_name = serializers.CharField(source="product.name")
    product_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, source="product.price"
    )

    class Meta:
        model = OrderItem
        # fields = ("product", "quantity")
        fields = (
            "order_item_id",
            "product_name",
            "product_price",
            "quantity",
            "item_subtotal",
        )

# Create order serializer
class OrderCreateSerializer(serializers.ModelSerializer):
    class OrderItemCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = OrderItem
            fields = ("product", "quantity")

    order_id = serializers.UUIDField(read_only=True)
    items = OrderItemCreateSerializer(many=True, required=False)

    def update(self, instance, validated_data):
        if "items" in validated_data:
            orderitem_data = validated_data.pop('items') # Get the items from the validated_data dictionary
        else:
            orderitem_data = None

        with transaction.atomic():  # Ensure that the entire update operation is atomic — if any part fails, all changes are rolled back
            instance = super().update(instance, validated_data)# Update the order

            if orderitem_data is not None:
                # Clear existing items (optional, depends on requirements)
                instance.items.all().delete() # Delete the existing items

                # Recreate items with the updated data
                for item in orderitem_data:
                    OrderItem.objects.create(order=instance, **item) # Create the order items
        return instance

    def create(self, validated_data):
        if "items" in validated_data:
            orderitem_data = validated_data.pop("items") # Get the items data
        else:
            orderitem_data = None

        with transaction.atomic():  # Ensure that the entire create operation is atomic — if any part fails, all changes are rolled back
            order = Order.objects.create(**validated_data) # Create the order

            for item in orderitem_data:
                OrderItem.objects.create(order=order, **item) # Create the order items

            return order

    class Meta:
        model = Order
        fields = (
            "order_id",
            "user",
            "status",
            "items",
        )
        extra_kwargs = {"user": {"read_only": True}}  # Another way to make a field read only


# List of orders serializer
class OrderSerializer(serializers.ModelSerializer):
    # user = serializers.StringRelatedField(read_only=True) # To return a string format only
    order_id = serializers.UUIDField(read_only=True)
    user = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(method_name="total")

    def total(self, obj):
        order_items = obj.items.all()
        return sum(order_item.item_subtotal for order_item in order_items)

    class Meta:
        model = Order
        fields = (
            "order_id",
            "created_at",
            "user",
            "status",
            "items",
            "total_price",
        )


class ProductInfoSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()

# def create(validated_data):
#     orderitem_data = validated_data.pop("items")
#     order = Order.objects.create(**validated_data)

#     for item in orderitem_data:
#         OrderItem.objects.create(order=order, **item)

validated_data = {
    "items": [
        {"product": 1, "quantity": 1},
        {"product": 2, "quantity": 2},
        {"product": 3, "quantity": 3},
        {"product": 4, "quantity": 4},
        {"product": 5, "quantity": 5},
        {"product": 6, "quantity": 6},
        {"product": 7, "quantity": 7},
        {"product": 8, "quantity": 8},
        {"product": 9, "quantity": 9},
        {"product": 10, "quantity": 10},
    ],
    "user": 1,
    "status": "Pending",
}


def create(validated_data):
    if "items" in validated_data:
        orderitem_data = validated_data.pop("items")
    else:
        orderitem_data = None

    print("Order Item Data:")
    print(orderitem_data)
    print("Order Data:")
    print(validated_data)


if __name__ == "__main__":
    create(validated_data)

from django.contrib import admin
from api.models import Order, OrderItem, User


# Inline admin descriptor for OrderItem model
# Allows OrderItems to be edited inline within the Order admin page
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    # Optionally, you can control the number of extra empty forms shown:
    # extra = 0


# Custom admin for Order model
# Displays related OrderItems inline on the Order detail page
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]


# Register the customized Order admin with the site
admin.site.register(Order, OrderAdmin)
admin.site.register(User)
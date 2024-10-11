from rest_framework import serializers
from .models import Category, Product, Supplier, Order, OrderItem
from rest_framework.exceptions import ValidationError

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description']

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'sku', 'category', 'price', 'stock_quantity', 'created_at', 'updated_at']

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'name', 'contact_person', 'email', 'phone', 'address']
class OrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']
        read_only_fields = ['price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_date', 'status', 'total_amount', 'items']
        read_only_fields = ['user', 'order_date', 'total_amount']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(total_amount=0, **validated_data)

        total_amount = 0
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            price = product.price
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=price)
            total_amount += price * quantity

        order.total_amount = total_amount
        order.save()
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)

        # Update the order status
        instance.status = validated_data.get('status', instance.status)

        # If there are new items, clear the old ones and replace with the new ones
        if items_data is not None:
            # Clear existing items
            instance.items.all().delete()

            total_amount = 0
            # Create new order items and calculate total_amount again
            for item_data in items_data:
                product = item_data['product']
                quantity = item_data['quantity']
                price = product.price
                OrderItem.objects.create(order=instance, product=product, quantity=quantity, price=price)
                total_amount += price * quantity

            # Update the total amount
            instance.total_amount = total_amount

        instance.save()
        return instance


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'sku', 'price', 'stock_quantity']

    def validate_price(self, value):
        if value <= 0:
            raise ValidationError("Price must be greater than zero.")
        return value

    def validate_stock_quantity(self, value):
        if value < 0:
            raise ValidationError("Stock quantity cannot be negative.")
        return value
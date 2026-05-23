from decimal import Decimal

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
import stripe
from rest_framework import mixins, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderItem
from .serializers import OrderSerializer
from products.models import Product

stripe.api_key = settings.STRIPE_SECRET_KEY


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product').order_by('-created_at')

    def create(self, request, *args, **kwargs):
        cart = request.session.get('cart', {})
        if not cart:
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user, total_price=0)
        total = Decimal('0.00')

        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id)
            item_total = Decimal(item['price']) * item['quantity']
            total += item_total

            OrderItem.objects.create(
                order=order,
                product=product,
                price=item['price'],
                quantity=item['quantity']
            )

        order.total_price = total
        order.save()
        request.session['cart'] = {}

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def stripe_checkout(self, request):
        cart = request.session.get('cart', {})
        if not cart:
            return Response({'detail': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        order = Order.objects.create(user=request.user, total_price=0)
        line_items = []
        total = Decimal('0.00')

        for product_id, item in cart.items():
            product = get_object_or_404(Product, id=product_id)
            item_total = Decimal(item['price']) * item['quantity']
            total += item_total

            OrderItem.objects.create(
                order=order,
                product=product,
                price=item['price'],
                quantity=item['quantity']
            )

            line_items.append({
                'price_data': {
                    'currency': 'egp',
                    'product_data': {'name': item['name']},
                    'unit_amount': int(Decimal(item['price']) * 100),
                },
                'quantity': item['quantity'],
            })

        order.total_price = total
        order.save()

        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=request.build_absolute_uri(
                reverse('orders:success')
            ) + f'?order_id={order.id}&session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=request.build_absolute_uri(
                reverse('cart:cart_detail')
            ),
            metadata={'order_id': order.id}
        )

        order.stripe_session_id = session.id
        order.save()

        return Response({'checkout_url': session.url, 'session_id': session.id})

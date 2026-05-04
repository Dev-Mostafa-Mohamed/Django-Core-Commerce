
from django.shortcuts import redirect, render,get_object_or_404
from .models import Order, OrderItem
import stripe
from django.conf import settings
from django.http import HttpResponse
from products.models import Product
from django.contrib.auth.decorators import login_required

def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart:cart_detail')

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None
    )

    total_price = 0

    for product_id, item in cart.items():
        product = Product.objects.get(id=product_id)

        item_total = float(item['price']) * item['quantity']
        total_price += item_total

        OrderItem.objects.create(
            order=order,
            product=product,
            price=item['price'],
            quantity=item['quantity']
        )

    order.total_price = total_price
    order.save()

    request.session['cart'] = {}

    return redirect('orders:order_detail', order.id)

@login_required
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')

    return render(request, 'orders/order_list.html', {
        'orders': orders
    })

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        user=request.user
    )

    return render(request, 'orders/order_detail.html', {
        'order': order
    })
stripe.api_key = settings.STRIPE_SECRET_KEY

@login_required
def stripe_checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart:cart_detail')

    order = Order.objects.create(
        user=request.user if request.user.is_authenticated else None,
        total_price=0
    )

    line_items = []
    total = 0

    for product_id, item in cart.items():
        product = Product.objects.get(id=product_id)

        item_total = float(item['price']) * item['quantity']
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
                'product_data': {
                    'name': item['name'],
                },
                'unit_amount': int(float(item['price']) * 100),
            },
            'quantity': item['quantity'],
        })

    order.total_price = total
    order.save()

    session = stripe.checkout.Session.create(
    payment_method_types=['card'],
    line_items=line_items,
    mode='payment',

    success_url='http://127.0.0.1:8000/orders/success/',
    cancel_url='http://127.0.0.1:8000/cart/',

    metadata={
        "order_id": order.id
    }
)

    order.stripe_session_id = session.id
    order.save()

    return redirect(session.url)

def success(request):
    order_id = request.GET.get('order_id')
    order = Order.objects.get(id=order_id)

    order.payment_status = 'paid'
    order.save()

    request.session['cart'] = {}

    return render(request, 'orders/success.html', {'order': order})

stripe.api_key = settings.STRIPE_SECRET_KEY


def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = "your_webhook_secret"

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )

    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    # 👇 أهم event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        order_id = session.get('metadata', {}).get('order_id')

        if order_id:
            order = Order.objects.get(id=order_id)
            order.payment_status = 'paid'
            order.save()

    return HttpResponse(status=200)





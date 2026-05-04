
from django.shortcuts import render,redirect, get_object_or_404
from products.models import Product


def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})

    product = get_object_or_404(Product, id=product_id)

    product_id = str(product.id)

    if product_id in cart:
        cart[product_id]['quantity'] += 1
    else:
        cart[product_id] = {
            'name': product.name,
            'price': str(product.price),
            'quantity': 1,
            'image': product.image.name if product.image else None
        }

    request.session['cart'] = cart

    return redirect('products:product_list')

def cart_detail(request):
    cart = request.session.get('cart', {})

    cart_items = []
    total_price = 0

    for product_id, item in cart.items():

        item_total = float(item['price']) * item['quantity']
        total_price += item_total

        cart_items.append({
            'id': product_id,
            'name': item['name'],
            'price': float(item['price']),
            'quantity': item['quantity'],
            'total': item_total,

            # 👇 مهم جدًا لو عندك صورة
            'image': item.get('image', '/static/default.jpg')if item.get('image') else None
        })

    return render(request, 'cart/cart_detail.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })



def update_cart(request, product_id, action):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:

        if action == 'increase':
            cart[product_id]['quantity'] += 1

        elif action == 'decrease':
            cart[product_id]['quantity'] -= 1

            # لو الكمية وصلت 0 نحذفه
            if cart[product_id]['quantity'] <= 0:
                del cart[product_id]

    request.session['cart'] = cart

    return redirect('cart:cart_detail')
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})

    product_id = str(product_id)

    if product_id in cart:
        del cart[product_id]

    request.session['cart'] = cart

    return redirect('cart:cart_detail')

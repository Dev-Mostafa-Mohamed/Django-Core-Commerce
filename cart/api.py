from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Product


def _get_cart(session):
    return session.get('cart', {})


def _save_cart(session, cart):
    session['cart'] = cart
    session.modified = True


def _build_cart_response(cart):
    cart_items = []
    total_price = 0

    for product_id, item in cart.items():
        item_total = float(item['price']) * item['quantity']
        total_price += item_total

        cart_items.append({
            'product_id': int(product_id),
            'name': item['name'],
            'price': float(item['price']),
            'quantity': item['quantity'],
            'total': item_total,
            'image': item.get('image'),
        })

    return {
        'items': cart_items,
        'total_price': total_price,
        'count': len(cart_items),
    }


class CartAPIView(APIView):
    def get(self, request):
        cart = _get_cart(request.session)
        return Response(_build_cart_response(cart))


class CartAddAPIView(APIView):
    def post(self, request):
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        if not product_id:
            return Response({'detail': 'product_id is required.'}, status=status.HTTP_400_BAD_REQUEST)

        product = get_object_or_404(Product, id=product_id)
        cart = _get_cart(request.session)
        key = str(product.id)

        if key in cart:
            cart[key]['quantity'] += quantity
        else:
            cart[key] = {
                'name': product.name,
                'price': str(product.price),
                'quantity': quantity,
                'image': product.image.name if product.image else None,
            }

        _save_cart(request.session, cart)
        return Response(_build_cart_response(cart), status=status.HTTP_200_OK)


class CartItemAPIView(APIView):
    def patch(self, request, product_id):
        cart = _get_cart(request.session)
        key = str(product_id)

        if key not in cart:
            return Response({'detail': 'Product not in cart.'}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get('action')
        quantity = request.data.get('quantity')

        if quantity is not None:
            try:
                quantity = int(quantity)
            except (ValueError, TypeError):
                return Response({'detail': 'Quantity must be a number.'}, status=status.HTTP_400_BAD_REQUEST)
            cart[key]['quantity'] = max(0, quantity)
        elif action == 'increase':
            cart[key]['quantity'] += 1
        elif action == 'decrease':
            cart[key]['quantity'] -= 1
        else:
            return Response({'detail': 'Action must be increase, decrease, or quantity.'}, status=status.HTTP_400_BAD_REQUEST)

        if cart[key]['quantity'] <= 0:
            del cart[key]

        _save_cart(request.session, cart)
        return Response(_build_cart_response(cart))

    def delete(self, request, product_id):
        cart = _get_cart(request.session)
        key = str(product_id)

        if key in cart:
            del cart[key]
            _save_cart(request.session, cart)

        return Response(_build_cart_response(cart))


class CartClearAPIView(APIView):
    def post(self, request):
        _save_cart(request.session, {})
        return Response(_build_cart_response({}))

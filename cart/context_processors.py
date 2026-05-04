def cart_item_count(request):
    cart = request.session.get('cart', {})

    total_items = 0

    for item in cart.values():
        total_items += item['quantity']

    return {
        'cart_count': total_items
    }



from django.urls import path
from .views import add_to_cart, cart_detail, update_cart,remove_from_cart

app_name = 'cart'

urlpatterns = [
    path('add/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('', cart_detail, name='cart_detail'),
    path('update/<int:product_id>/<str:action>/', update_cart, name='update_cart'),
    path('remove/<int:product_id>/', remove_from_cart, name='remove_from_cart'),

]
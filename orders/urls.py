
from django.urls import path
from .views import checkout,order_list,order_detail,stripe_checkout,success,stripe_webhook
app_name = 'orders'
urlpatterns = [
    path('checkout/', checkout, name='checkout'),
    path('', order_list, name='order_list'),
    path('<int:order_id>/', order_detail, name='order_detail'),
    path('stripe-checkout/', stripe_checkout, name='stripe_checkout'),
    path('success/', success, name='success'),
    path('webhook/', stripe_webhook, name='stripe_webhook'),
    
]
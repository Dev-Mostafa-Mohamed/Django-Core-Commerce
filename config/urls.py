"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from products.api import CategoryViewSet, ProductViewSet
from orders.api import OrderViewSet
from accounts.api import (
    RegisterAPIView, LoginAPIView, LogoutAPIView,
    CurrentUserAPIView, WishlistViewSet
)
from cart.api import (
    CartAPIView, CartAddAPIView, CartItemAPIView,
    CartClearAPIView
)

router = DefaultRouter()
router.register('products', ProductViewSet, basename='product')
router.register('categories', CategoryViewSet, basename='category')
router.register('orders', OrderViewSet, basename='order')
router.register('wishlist', WishlistViewSet, basename='wishlist')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls')),
    path('accounts/', include('accounts.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('api/auth/register/', RegisterAPIView.as_view(), name='api-auth-register'),
    path('api/auth/login/', LoginAPIView.as_view(), name='api-auth-login'),
    path('api/auth/logout/', LogoutAPIView.as_view(), name='api-auth-logout'),
    path('api/auth/user/', CurrentUserAPIView.as_view(), name='api-auth-user'),
    path('api/cart/', CartAPIView.as_view(), name='api-cart-detail'),
    path('api/cart/add/', CartAddAPIView.as_view(), name='api-cart-add'),
    path('api/cart/<int:product_id>/', CartItemAPIView.as_view(), name='api-cart-item'),
    path('api/cart/clear/', CartClearAPIView.as_view(), name='api-cart-clear'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

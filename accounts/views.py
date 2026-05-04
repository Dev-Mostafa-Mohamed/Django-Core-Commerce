
from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import RegisterForm
from .models import Wishlist
from products.models import Product
from django.contrib.auth.decorators import login_required


app_name = 'accounts'

def register_view(request):
    if request.user.is_authenticated:
        return redirect('products:product_list')

    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('products:product_list')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {
        'form': form
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect('products:product_list')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:
            login(request, user)
            return redirect('products:product_list')

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect('products:product_list')

@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    wishlist_item = Wishlist.objects.filter(
        user=request.user,
        product=product
    )

    if wishlist_item.exists():
        wishlist_item.delete()
    else:
        Wishlist.objects.create(
            user=request.user,
            product=product
        )

    return redirect(request.META.get('HTTP_REFERER', 'products:list'))

def wishlist_view(request):
    wishlist = Wishlist.objects.filter(user=request.user)

    return render(request, 'accounts/wishlist.html', {
        'wishlist': wishlist
    })
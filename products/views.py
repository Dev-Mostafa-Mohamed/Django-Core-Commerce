
from django.views.generic import ListView, DetailView
from .models import Product, Category
from django.db.models import Q
from django.shortcuts import get_object_or_404


class ProductListView(ListView):
    model = Product
    template_name = 'products/product_list.html'
    context_object_name = 'products'
    paginate_by = 8

    def get_queryset(self):
        queryset = Product.objects.filter(
            available=True
        ).select_related('category')

        self.category = None
        slug = self.kwargs.get('category_slug')

        if slug:
            
            self.category = get_object_or_404(Category, slug=slug)
            queryset = queryset.filter(category=self.category)

        # 🔍 Search
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )

        # 💰 Sort
        sort = self.request.GET.get('sort')
        if sort == 'price_asc':
            queryset = queryset.order_by('price')
        elif sort == 'price_desc':
            queryset = queryset.order_by('-price')
        else:
            queryset = queryset.order_by('-id')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['categories'] = Category.objects.all()
        context['current_category'] = self.category

        # ❤️ Wishlist
        if self.request.user.is_authenticated:
            context['wishlist_ids'] = self.request.user.wishlist.values_list('product_id', flat=True)
        else:
            context['wishlist_ids'] = []

        return context

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'

    def get_queryset(self):
        return Product.objects.filter(
            available=True
        ).select_related('category')
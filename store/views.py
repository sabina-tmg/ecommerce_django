from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, ReviewRating, ProductGallery
from category.models import Category
from cart.models import CartItem
from django.db.models import Q
from django.contrib import messages
from cart.views import _cart_id
from django.core.paginator import Paginator
from .forms import ReviewForm
from order.models import OrderProduct
def store(request, category_slug=None):
    products = Product.objects.filter(is_available=True)

    # Filter by category
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    # Get selected sizes
    selected_sizes = request.GET.getlist('size')
    if selected_sizes:
        products = products.filter(size__in=selected_sizes)

    # Get selected price range
    min_price = request.GET.get('min_price', '0')
    max_price = request.GET.get('max_price', '2000')
    if min_price and max_price:
        products = products.filter(price__gte=min_price, price__lte=max_price)

    # Pagination
    paginator = Paginator(products, 3)
    page = request.GET.get('page')
    paged_products = paginator.get_page(page)

    context = {
        'products': paged_products,
        'product_count': products.count(),
        'sizes': ['XS', 'SM', 'LG', 'XXL'],  # Hardcoded or dynamic
        'selected_sizes': selected_sizes,
        'min_price': min_price,
        'max_price': max_price,
        'min_price_options': ['0', '50', '100', '150', '200', '500', '1000'],
        'max_price_options': ['50', '100', '150', '200', '500', '1000', '2000'],
    }
    return render(request, 'store/store.html', context)

def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        in_cart = CartItem.objects.filter(cart__cart_id=_cart_id(request), product=single_product).exists()
    except Exception as e:
        raise e

    if request.user.is_authenticated:
        orderproduct = OrderProduct.objects.filter(user=request.user, product_id=single_product.id).exists()
    else:
        orderproduct = None

    reviews = ReviewRating.objects.filter(product_id=single_product.id, status=True)
    product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

    context = {
        'single_product': single_product,
        'in_cart': in_cart,
        'orderproduct': orderproduct,
        'reviews': reviews,
        'product_gallery': product_gallery,
    }
    return render(request, 'store/product_detail.html', context)


def search(request):
    products = Product.objects.none()
    product_count = 0
    links = Category.objects.all()
    sizes = ['XS', 'SM', 'LG', 'XXL']

    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(
                Q(description__icontains=keyword) | Q(product_name__icontains=keyword)
            )
            product_count = products.count()

    context = {
        'products': products,
        'product_count': product_count,
        'links': links,
        'sizes': sizes,
        'selected_sizes': [],
        'min_price': None,
        'max_price': None,
    }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            if form.is_valid():
                form.save()
                messages.success(request, 'Thank you! Your review has been updated.')
                return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)
    return redirect(url)



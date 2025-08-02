from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, CartItem ,Variation 
from django.core.exceptions import ObjectDoesNotExist
from cart.utils import _cart_id

def cart(request):
    try:
        total = 0
        quantity = 0
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
    except ObjectDoesNotExist:
        cart_items = []
        total = 0
        quantity = 0
        tax = 0
        grand_total = 0

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
    }
    return render(request, 'store/cart.html', context)



def remove_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = get_object_or_404(CartItem, product=product, cart=cart, id=cart_item_id)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()

    return redirect('cart')




def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')



def add_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_variation = []

    if request.method == 'POST':
        for key in request.POST:
            value = request.POST[key]
            variations = Variation.objects.filter(
                product=product,
                variation_category__iexact=key,
                variation_value__iexact=value
            )
            if variations.exists():
                product_variation.extend(list(variations))

    # Get or create cart
    cart, created = Cart.objects.get_or_create(cart_id=_cart_id(request))

    # Check if cart item exists
    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()

    if is_cart_item_exists:
        cart_items = CartItem.objects.filter(product=product, cart=cart)
        existing_variation_list = []
        id_list = []

        for item in cart_items:
            existing_variation = item.variations.all()
            existing_variation_list.append(list(existing_variation))
            id_list.append(item.id)

        if product_variation in existing_variation_list:
            index = existing_variation_list.index(product_variation)
            item_id = id_list[index]
            item = CartItem.objects.get(id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if product_variation:
                item.variations.set(product_variation)
            item.save()
    else:
        item = CartItem.objects.create(product=product, quantity=1, cart=cart)
        if product_variation:
            item.variations.set(product_variation)
        item.save()

    return redirect('cart')

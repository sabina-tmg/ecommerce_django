from .models import Cart, CartItem
from .utils import _cart_id

def counter(request):
    cart_count = 0
    try:
        cart = Cart.objects.filter(cart_id=_cart_id(request))
        if cart.exists():
            cart_items = CartItem.objects.filter(cart=cart.first())
        else:
            cart_items = []
        for cart_item in cart_items:
            cart_count += cart_item.quantity
    except Cart.DoesNotExist:
        cart_count = 0
    return dict(cart_count=cart_count)

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from cart.models import CartItem
from .forms import OrderForm
import datetime
from .models import Order, Transaction
from store.models import Product
import uuid
from .esewa import EsewaPayment

def buy(request, id):
    product = get_object_or_404(Product, id=id)
    uid = uuid.uuid4()
    
    transaction = Transaction.objects.create(
        product=product,
        transaction_uuid=str(uid),
        transaction_amount=product.price,
        transaction_status='PENDING'
    )
    
    epayment = EsewaPayment(
        product_code="EPAYTEST",
        success_url=f"http://localhost:8000/success/{transaction.id}/",
        failure_url=f"http://localhost:8000/failure/{transaction.id}/",
        secret_key="8gBm/:&EnhH.1/q,"
    )
    
    epayment.create_signature(
        total_amount=product.price,
        transaction_uuid=transaction.transaction_uuid
    )
    
    context = {
        'product': product,
        'form': epayment.generate_form()
    }
    
    return render(request, 'orders/payments.html', context)

# Place Order
def place_order(request, total=0, quantity=0):
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)

    # Redirect if no cart items
    if not cart_items.exists():
        return redirect('store')

    # Calculate totals
    for cart_item in cart_items:
        total += cart_item.product.price * cart_item.quantity
        quantity += cart_item.quantity
    tax = (2 * total) / 100
    grand_total = total + tax

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line_1 = form.cleaned_data['address_line_1']
            data.address_line_2 = form.cleaned_data['address_line_2']
            data.country = form.cleaned_data['country']
            data.state = form.cleaned_data['state']
            data.city = form.cleaned_data['city']
            data.order_note = form.cleaned_data['order_note']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get('REMOTE_ADDR')
            data.save()

            # Generate order number
            current_date = datetime.date.today().strftime("%Y%m%d")
            data.order_number = current_date + str(data.id)
            data.save()

            order = Order.objects.get(user=current_user, is_ordered=False, order_number=data.order_number)

            context = {
                'order': order,
                'cart_items': cart_items,
                'total': total,
                'tax': tax,
                'grand_total': grand_total,
            }
            return render(request, 'orders/payments.html', context)
    return redirect('checkout')




def success(request, id):
    transaction = get_object_or_404(Transaction, id=id)

    epayment = EsewaPayment(
        product_code='EPAYTEST',
        success_url=request.build_absolute_uri(f'/success/{transaction.id}/'),
        failure_url=request.build_absolute_uri(f'/failure/{transaction.id}/'),
        secret_key='8gBm/:&EnhH.1/q'
    )

    epayment.create_signature(
        total_amount=transaction.transaction_amount,
        transaction_uuid=transaction.transaction_uuid
    )

    if epayment.is_completed(True):  
        transaction.transaction_status = "Completed"
        transaction.save()
        return render(request, 'success.html')
    else:
        transaction.transaction_status = "Failed"
        transaction.save()
        return render(request, 'failure.html')

def failure(request, id):
    transaction = get_object_or_404(Transaction, id=id)
    transaction.transaction_status = "Failed"
    transaction.save()
    return render(request, 'failure.html')
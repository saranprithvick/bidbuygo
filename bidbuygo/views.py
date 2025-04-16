from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,Orders,Transaction
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login,authenticate,logout
from django.utils import timezone
import uuid
from django.contrib.auth.decorators import login_required
# Create your views here.
def home(request):
    return render(request, 'bidbuygo/home.html')

def product_list(request):
    products = Product.objects.all()  # This fetches all products from the database
    return render(request, 'bidbuygo/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)  # Fetches product based on their ID
    return render(request, 'bidbuygo/product_detail.html', {'product': product})

def user_registration(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'bidbuygo/user_registration.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  
    else:
        form = AuthenticationForm()

    return render(request, 'bidbuygo/user_login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def place_order(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == 'POST':
        address = request.POST.get('order_address')
        price_amt = product.price 
        order = Orders.objects.create(
            order_id=str(uuid.uuid4())[:8],  
            user=request.user,
            product=product,
            order_address=address,
            price_amt=price_amt,
            order_date=timezone.now(),
            order_status='Pending'
        )
        return redirect('order_list') 

    return render(request, 'bidbuygo/place_order.html', {'product': product})
@login_required
def order_list(request):
    orders = Orders.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'bidbuygo/order_list.html', {'orders': orders})

@login_required
def complete_payment(request, order_id):
    order = get_object_or_404(Orders, order_id=order_id)

    if request.method == 'POST':
        transaction = Transaction.objects.create(
            transaction_id=str(uuid.uuid4())[:8], 
            order=order,
            transaction_amt=order.price_amt,
            account_details=request.POST.get('account_details'),
            mode_of_payment=request.POST.get('mode_of_payment')
        )
        order.order_status = 'Paid'
        order.save()

        return redirect('order_list')

    return render(request, 'bidbuygo/complete_payment.html', {'order': order})
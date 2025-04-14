from django.shortcuts import render,get_object_or_404,redirect
from .models import Product
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import login,authenticate
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

    return render(request, 'bidbuygo/login.html', {'form': form})


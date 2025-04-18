from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.db.models import Q, Avg, Count, Sum
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import *
from .forms import *
import uuid
from decimal import Decimal
from django.contrib.auth.forms import AuthenticationForm

def home(request):
    # Featured products (new arrivals)
    featured_products = Product.objects.filter(is_available=True).order_by('-created_at')[:8]
    
    # Thrift store products
    thrift_products = Product.objects.filter(
        product_type='Thrift',
        is_available=True
    )[:4]
    
    # Auction products
    auction_products = Product.objects.filter(
        product_type='Auction',
        is_available=True
    )[:4]
    
    context = {
        'featured_products': featured_products,
        'thrift_products': thrift_products,
        'auction_products': auction_products,
    }
    return render(request, 'bidbuygo/home.html', context)

def product_list(request):
    form = SearchForm(request.GET)
    products = Product.objects.filter(is_available=True)
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        product_type = form.cleaned_data.get('product_type')
        product_condition = form.cleaned_data.get('product_condition')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        
        if query:
            products = products.filter(
                Q(product_name__icontains=query) |
                Q(description__icontains=query)
            )
        if category:
            products = products.filter(category=category)
        if product_type:
            products = products.filter(product_type=product_type)
        if product_condition:
            products = products.filter(product_condition=product_condition)
        if min_price:
            products = products.filter(price__gte=min_price)
        if max_price:
            products = products.filter(price__lte=max_price)
    
    # Add pagination
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'form': form,
    }
    return render(request, 'bidbuygo/product_list.html', context)

def product_detail(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    reviews = ProductReview.objects.filter(product=product)
    average_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    review_count = reviews.count()
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        is_available=True
    ).exclude(product_id=product_id)[:4]
    
    # For auction products, get bidding information
    bidding_info = None
    if product.product_type == 'Auction':
        bidding_info = Bidding.objects.filter(
            product=product,
            bid_status='Pending'
        ).order_by('-bid_amt').first()
    
    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'review_count': review_count,
        'related_products': related_products,
        'bidding_info': bidding_info,
    }
    return render(request, 'bidbuygo/product_detail.html', context)

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
def place_bid(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    
    if product.product_type != 'Auction':
        messages.error(request, 'This product is not available for bidding.')
        return redirect('product_detail', product_id=product_id)
    
    if request.method == 'POST':
        form = BiddingForm(request.POST)
        if form.is_valid():
            bid_amt = form.cleaned_data['bid_amt']
            auto_bid_limit = form.cleaned_data['auto_bid_limit']
            is_auto_bid = form.cleaned_data['is_auto_bid']
            
            # Check if bid amount is higher than current highest bid
            current_highest_bid = Bidding.objects.filter(
                product=product,
                bid_status='Pending'
            ).order_by('-bid_amt').first()
            
            if current_highest_bid and bid_amt <= current_highest_bid.bid_amt:
                messages.error(request, 'Your bid must be higher than the current highest bid.')
                return redirect('product_detail', product_id=product_id)
            
            # Create new bid
            bid = Bidding.objects.create(
                user=request.user,
                product=product,
                bid_amt=bid_amt,
                auto_bid_limit=auto_bid_limit,
                is_auto_bid=is_auto_bid,
                bid_status='Pending',
                initial_bid_amt=current_highest_bid.bid_amt if current_highest_bid else product.price
            )
            
            messages.success(request, 'Your bid has been placed successfully!')
            return redirect('product_detail', product_id=product_id)
    else:
        form = BiddingForm()
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'bidbuygo/place_bid.html', context)

@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    
    # Check if user has already reviewed this product
    existing_review = ProductReview.objects.filter(
        user=request.user,
        product=product
    ).exists()
    
    if existing_review:
        messages.error(request, 'You have already reviewed this product.')
        return redirect('product_detail', product_id=product_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, 'Your review has been added successfully!')
            return redirect('product_detail', product_id=product_id)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'bidbuygo/add_review.html', context)

@login_required
def user_profile(request):
    user = request.user
    orders = Orders.objects.filter(user=user).order_by('-order_date')
    bids = Bidding.objects.filter(user=user).order_by('-bid_time')
    reviews = ProductReview.objects.filter(user=user).order_by('-created_at')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('user_profile')
    else:
        form = CustomUserCreationForm(instance=user)
    
    context = {
        'user': user,
        'form': form,
        'orders': orders,
        'bids': bids,
        'reviews': reviews,
    }
    return render(request, 'bidbuygo/user_profile.html', context)

@login_required
def seller_dashboard(request):
    if not hasattr(request.user, 'seller'):
        messages.error(request, 'You are not authorized to access the seller dashboard.')
        return redirect('home')
    
    seller = request.user.seller
    products = Product.objects.filter(seller=seller)
    orders = Orders.objects.filter(product__seller=seller)
    total_sales = orders.filter(order_status='Completed').aggregate(
        total=Sum('price_amt')
    )['total'] or 0
    
    context = {
        'seller': seller,
        'products': products,
        'orders': orders,
        'total_sales': total_sales,
    }
    return render(request, 'bidbuygo/seller_dashboard.html', context)

@login_required
def add_product(request):
    if not hasattr(request.user, 'seller'):
        messages.error(request, 'You are not authorized to add products.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user.seller
            product.product_id = str(uuid.uuid4())[:8]
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('seller_dashboard')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
    }
    return render(request, 'bidbuygo/add_product.html', context)

@login_required
def place_order(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.order_id = str(uuid.uuid4())[:8]
            order.user = request.user
            order.product = product
            order.price_amt = product.price
            order.order_date = timezone.now()
            order.order_status = 'Pending'
            order.save()
            
            # Update product quantity
            product.quantity -= 1
            if product.quantity == 0:
                product.is_available = False
            product.save()
            
            messages.success(request, 'Order placed successfully!')
            return redirect('order_list')
    else:
        form = OrderForm()
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'bidbuygo/place_order.html', context)

@login_required
def order_list(request):
    orders = Orders.objects.filter(user=request.user).order_by('-order_date')
    context = {
        'orders': orders,
    }
    return render(request, 'bidbuygo/order_list.html', context)

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
        
        messages.success(request, 'Payment completed successfully!')
        return redirect('order_list')
    
    context = {
        'order': order,
    }
    return render(request, 'bidbuygo/complete_payment.html', context)
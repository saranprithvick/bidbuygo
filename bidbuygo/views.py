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
from .services.bidding_service import BiddingService
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from .payment_utils import PaymentManager
import json
import razorpay
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import User

# Initialize Razorpay client only if settings are configured
try:
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
except AttributeError:
    client = None

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
    
    # Get auction information
    auction_info = None
    bid_form = None
    user_highest_bid = None
    
    if product.product_type == 'Auction':
        auction_info = BiddingService.get_auction_status(product)
        if request.user.is_authenticated and not auction_info['has_ended']:
            bid_form = BidForm()
            user_highest_bid = Bidding.objects.filter(
                user=request.user,
                product=product,
                bid_status='Pending'
            ).order_by('-bid_amt').first()
    
    context = {
        'product': product,
        'reviews': reviews,
        'average_rating': average_rating,
        'review_count': review_count,
        'related_products': related_products,
        'auction_info': auction_info,
        'bid_form': bid_form,
        'user_highest_bid': user_highest_bid,
    }
    return render(request, 'bidbuygo/product_detail.html', context)

def user_registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to BidBuyGo.')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'bidbuygo/register.html', {'form': form})

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
    if request.method == 'POST':
        product = get_object_or_404(Product, product_id=product_id)
        try:
            bid_amount = Decimal(request.POST.get('bid_amount'))
            is_auto_bid = request.POST.get('is_auto_bid') == 'true'
            auto_bid_limit = Decimal(request.POST.get('auto_bid_limit')) if request.POST.get('auto_bid_limit') else None
            bid_increment = Decimal(request.POST.get('bid_increment', '1.00'))
            
            bid = BiddingService.place_bid(
                user=request.user,
                product=product,
                bid_amount=bid_amount,
                is_auto_bid=is_auto_bid,
                auto_bid_limit=auto_bid_limit,
                bid_increment=bid_increment
            )
            
            messages.success(request, 'Your bid has been placed successfully!')
            return redirect('product_detail', product_id=product_id)
            
        except Exception as e:
            messages.error(request, str(e))
            return redirect('product_detail', product_id=product_id)
            
    return redirect('product_detail', product_id=product_id)

def get_auction_status(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    try:
        status = BiddingService.get_auction_status(product)
        return JsonResponse(status)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

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
    try:
        # Get orders for the current user
        orders = Orders.objects.filter(user=request.user).order_by('-order_date')
        return render(request, 'bidbuygo/profile.html', {
            'user': request.user,
            'orders': orders
        })
    except Exception as e:
        messages.error(request, f'Error accessing profile: {str(e)}')
        return redirect('home')

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

@login_required
def my_bids(request):
    bids = Bidding.objects.filter(user=request.user).order_by('-bid_time')
    return render(request, 'bidbuygo/my_bids.html', {'bids': bids})

@login_required
def end_auction(request, product_id):
    if not request.user.is_staff:
        messages.error(request, 'Only staff members can end auctions')
        return redirect('product_detail', product_id=product_id)
        
    product = get_object_or_404(Product, product_id=product_id)
    try:
        BiddingService.end_auction(product)
        messages.success(request, 'Auction has been ended successfully')
    except Exception as e:
        messages.error(request, str(e))
        
    return redirect('product_detail', product_id=product_id)

def payment_page(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        context = {
            'order': order,
            'razorpay_key': settings.RAZORPAY_KEY_ID
        }
        return render(request, 'bidbuygo/payment.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('home')

def create_payment(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        
        # Create Razorpay Order
        razorpay_order = client.order.create({
            'amount': int(order.amount * 100),  # Amount in paise
            'currency': 'INR',
            'receipt': str(order.id)
        })
        
        # Update order with Razorpay order ID
        order.razorpay_order_id = razorpay_order['id']
        order.save()
        
        return JsonResponse({
            'order_id': razorpay_order['id'],
            'amount': razorpay_order['amount'],
            'currency': razorpay_order['currency']
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def payment_callback(request):
    if request.method == "POST":
        try:
            # Get payment data
            payment_data = json.loads(request.body)
            razorpay_payment_id = payment_data.get('razorpay_payment_id')
            razorpay_order_id = payment_data.get('razorpay_order_id')
            razorpay_signature = payment_data.get('razorpay_signature')
            
            # Verify signature
            params_dict = {
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_order_id': razorpay_order_id,
                'razorpay_signature': razorpay_signature
            }
            
            try:
                client.utility.verify_payment_signature(params_dict)
            except Exception:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid payment signature'
                }, status=400)
            
            # Update order and create transaction
            order = Order.objects.get(razorpay_order_id=razorpay_order_id)
            order.status = 'PAID'
            order.save()
            
            Transaction.objects.create(
                order=order,
                payment_id=razorpay_payment_id,
                amount=order.amount,
                status='SUCCESS'
            )
            
            return JsonResponse({'status': 'success'})
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def payment_success(request):
    return render(request, 'bidbuygo/payment_success.html')

def initiate_refund(request, transaction_id):
    """Initiate a refund for a transaction"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
        
    try:
        transaction = get_object_or_404(Transaction, id=transaction_id)
        
        # Create refund
        refund_data = {
            'payment_id': transaction.payment_id,
            'amount': int(transaction.amount * 100),  # Amount in paise
            'speed': 'normal'
        }
        
        refund = client.payment.refund(transaction.payment_id, refund_data)
        
        # Update transaction status
        transaction.status = 'REFUNDED'
        transaction.refund_id = refund['id']
        transaction.save()
        
        return JsonResponse({
            'success': True,
            'refund_id': refund['id']
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
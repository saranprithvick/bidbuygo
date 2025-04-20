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
import json
from django.conf import settings
from django.urls import reverse
from django.db import connection
from .models import Order, OrderItem, ProductSize, Cart, CartItem, User
import stripe
from django.db import transaction
from django.core.mail import send_mail
from datetime import timedelta
import random
from .models import UnverifiedUser

def home(request):
    """Home page view"""
    context = {
        'site_name': 'BidBuyGo',
        'description': 'Welcome to BidBuyGo - Your Premier Destination for Fashion Auctions and Shopping',
        'features': [
            'Exclusive fashion items from top brands',
            'Competitive bidding on unique pieces',
            'Secure payment processing',
            'Fast and reliable delivery',
            'Customer satisfaction guaranteed'
        ]
    }
    return render(request, 'bidbuygo/home.html', context)

def product_list(request):
    # Get all available products
    products = Product.objects.filter(is_available=True)
    
    # Get search query
    search_query = request.GET.get('query')
    if search_query:
        products = products.filter(
            Q(product_name__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Get category filter
    category = request.GET.get('category')
    if category:
        products = products.filter(category__name=category)
    
    # Get product type filter
    product_type = request.GET.get('product_type')
    if product_type:
        products = products.filter(product_type=product_type)
    
    # Order products alphabetically by product name
    products = products.order_by('product_name')
    
    # Get all categories for the filter dropdown
    categories = Category.objects.all()
    
    # Pagination
    paginator = Paginator(products, 12)  # Show 12 products per page
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'products': products,
        'categories': categories,
        'search_query': search_query,
        'selected_category': category,
        'selected_product_type': product_type,
    }
    return render(request, 'bidbuygo/product_list.html', context)

def auction_list(request):
    """View for listing all active auctions"""
    # Get all active auction products
    auctions = Product.objects.filter(
        product_type='auction',
        auction_status='Active',
        is_available=True
    ).order_by('-last_bid_time')
    
    # Get auctions ending in the next 24 hours (using last_bid_time as a proxy)
    ends_soon = auctions.filter(
        last_bid_time__lte=timezone.now() + timezone.timedelta(hours=24)
    ).order_by('last_bid_time')
    
    # Get other active auctions
    other_auctions = auctions.exclude(
        last_bid_time__lte=timezone.now() + timezone.timedelta(hours=24)
    ).order_by('last_bid_time')
    
    paginator = Paginator(other_auctions, 12)  # Show 12 auctions per page
    page = request.GET.get('page')
    other_auctions = paginator.get_page(page)
    
    return render(request, 'bidbuygo/auction_list.html', {
        'ends_soon': ends_soon,
        'other_auctions': other_auctions
    })

def product_detail(request, product_id):
    try:
        product = Product.objects.get(product_id=product_id)
        auction_info = {
            'current_bid': 0,
            'total_bids': 0,
            'time_remaining': 0,
            'highest_bidder': None,
            'has_ended': False
        }
        
        if product.product_type == 'Auction':
            try:
                auction_info = BiddingService.get_auction_status(product)
            except Exception as e:
                print(f"Error getting auction status: {e}")
                auction_info['has_ended'] = False

        user_highest_bid = None
        if request.user.is_authenticated and product.product_type == 'Auction':
            user_highest_bid = BiddingService.get_user_highest_bid(request.user, product)
            bid_form = BidForm(initial={'max_bid': user_highest_bid.amount if user_highest_bid else None})
        else:
            bid_form = BidForm()

        context = {
            'product': product,
            'auction_info': auction_info,
            'user_highest_bid': user_highest_bid,
            'bid_form': bid_form,
            'is_auction': product.product_type == 'Auction'
        }
        return render(request, 'bidbuygo/product_detail.html', context)
    except Product.DoesNotExist:
        messages.error(request, 'Product not found')
        return redirect('bidbuygo:home')
    except Exception as e:
        messages.error(request, f'Error loading product: {str(e)}')
        return redirect('bidbuygo:home')

@login_required
def add_to_cart(request, product_id):
    try:
        product = get_object_or_404(Product, product_id=product_id, is_available=True)
        
        # Prevent auction products from being added to cart
        if product.product_type == 'Auction':
            messages.error(request, 'Auction products cannot be added to cart. Please place a bid instead.')
            return redirect('bidbuygo:product_detail', product_id=product_id)
            
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        if request.method == 'POST':
            quantity = int(request.POST.get('quantity', 1))
            selected_size = request.POST.get('selected_size')
            
            if not selected_size:
                messages.error(request, 'Please select a size')
                return redirect('bidbuygo:product_detail', product_id=product_id)
                
            # Check if the selected size exists and has enough stock
            try:
                product_size = ProductSize.objects.get(product=product, size=selected_size)
                if product_size.stock < quantity:
                    messages.error(request, f'Only {product_size.stock} items available in size {selected_size}')
                    return redirect('bidbuygo:product_detail', product_id=product_id)
            except ProductSize.DoesNotExist:
                messages.error(request, 'Invalid size selected')
                return redirect('bidbuygo:product_detail', product_id=product_id)
            
            # Get or create cart item with the selected size
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                size=selected_size,
                defaults={'quantity': quantity}
            )
            
            if not created:
                new_quantity = cart_item.quantity + quantity
                if new_quantity > product_size.stock:
                    messages.error(request, f'Cannot add more items. Only {product_size.stock} available in size {selected_size}')
                    return redirect('bidbuygo:product_detail', product_id=product_id)
                cart_item.quantity = new_quantity
                cart_item.save()
                
            messages.success(request, f'{product.product_name} (Size: {selected_size}) added to cart')
            return redirect('bidbuygo:cart')
            
        return redirect('bidbuygo:product_detail', product_id=product_id)
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('bidbuygo:product_detail', product_id=product_id)

@login_required
def update_cart(request, product_id):
    try:
        if request.method == 'POST':
            cart = Cart.objects.get(user=request.user)
            size = request.POST.get('size')
            quantity = int(request.POST.get('quantity', 1))
            
            try:
                cart_item = CartItem.objects.get(cart=cart, product__product_id=product_id, size=size)
                product_size = ProductSize.objects.get(product=cart_item.product, size=size)
                
                if quantity <= 0:
                    cart_item.delete()
                    messages.success(request, 'Item removed from cart.')
                else:
                    if quantity > product_size.stock:
                        messages.error(request, f'Only {product_size.stock} items available in size {size}')
                        return redirect('bidbuygo:cart')
                    
                    cart_item.quantity = quantity
                    cart_item.save()
                    messages.success(request, 'Cart updated successfully.')
            except CartItem.DoesNotExist:
                messages.error(request, 'Item not found in cart.')
            except ProductSize.DoesNotExist:
                messages.error(request, 'Invalid product size.')
        
        return redirect('bidbuygo:cart')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('bidbuygo:cart')

@login_required
def remove_from_cart(request, product_id):
    try:
        if request.method == 'POST':
            cart = Cart.objects.get(user=request.user)
            size = request.POST.get('size')
            
            try:
                cart_item = CartItem.objects.get(cart=cart, product__product_id=product_id, size=size)
                cart_item.delete()
                messages.success(request, 'Item removed from cart.')
            except CartItem.DoesNotExist:
                messages.error(request, 'Item not found in cart.')
        
        return redirect('bidbuygo:cart')
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('bidbuygo:cart')

@login_required
def view_cart(request):
    try:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = CartItem.objects.filter(cart=cart).select_related('product')
        
        # Calculate total price using the cart's total_price property
        cart_total = cart.total_price
        
        context = {
            'cart_items': cart_items,
            'cart_total': cart_total,
        }
        return render(request, 'bidbuygo/cart.html', context)
    except Exception as e:
        messages.error(request, f'An error occurred: {str(e)}')
        return redirect('bidbuygo:home')

def register_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        print(f"DEBUG: Registration attempt for email: {email}")  # Debug print
        
        # Check if email already exists in verified users
        if User.objects.filter(email=email).exists():
            print(f"DEBUG: Email {email} already registered")  # Debug print
            messages.error(request, 'This email is already registered. Please sign in instead or use a different email address.')
            return redirect('bidbuygo:register_email')
        
        # Generate 6-digit OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        print(f"DEBUG: Generated OTP: {otp}")  # Debug print
        
        # Delete any existing unverified user with this email
        UnverifiedUser.objects.filter(email=email).delete()
        
        # Create new unverified user
        unverified_user = UnverifiedUser.objects.create(
            email=email,
            otp=otp,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        print(f"DEBUG: Created unverified user record")  # Debug print
        
        # Send OTP email
        from django.conf import settings
        print(f"DEBUG: Attempting to send email from {settings.EMAIL_HOST_USER} to {email}")  # Debug print
        try:
            send_mail(
                'Your OTP for Email Verification',
                f'Your OTP is: {otp}. It will expire in 10 minutes.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )
            print("DEBUG: Email sent successfully")  # Debug print
        except Exception as e:
            print(f"DEBUG: Error sending email: {str(e)}")  # Debug print
            messages.error(request, 'Error sending OTP. Please try again.')
            return redirect('bidbuygo:register_email')
        
        messages.success(request, 'OTP sent to your email')
        return redirect('bidbuygo:verify_email', email=email)
    
    return render(request, 'bidbuygo/register_email.html')

def verify_email(request, email):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        try:
            unverified_user = UnverifiedUser.objects.get(email=email)
            
            if unverified_user.is_expired():
                messages.error(request, 'OTP has expired. Please request a new one.')
                return redirect('bidbuygo:register_email')
            
            if unverified_user.otp != otp:
                messages.error(request, 'Invalid OTP')
                return redirect('bidbuygo:verify_email', email=email)
            
            # Mark as verified and redirect to password setup
            unverified_user.is_verified = True
            unverified_user.save()
            return redirect('bidbuygo:set_password', email=email)
            
        except UnverifiedUser.DoesNotExist:
            messages.error(request, 'Invalid email or OTP expired')
            return redirect('bidbuygo:register_email')
    
    return render(request, 'bidbuygo/verify_email.html', {'email': email})

def set_password(request, email):
    try:
        unverified_user = UnverifiedUser.objects.get(email=email, is_verified=True)
    except UnverifiedUser.DoesNotExist:
        messages.error(request, 'Please verify your email first')
        return redirect('bidbuygo:register_email')
    
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        # Password validation
        if len(password) < 8:
            messages.error(request, 'Password must be at least 8 characters long')
            return redirect('bidbuygo:set_password', email=email)
            
        if not any(c.isalpha() for c in password):
            messages.error(request, 'Password must contain at least one letter')
            return redirect('bidbuygo:set_password', email=email)
            
        if not any(c.isdigit() for c in password):
            messages.error(request, 'Password must contain at least one number')
            return redirect('bidbuygo:set_password', email=email)
            
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password):
            messages.error(request, 'Password must contain at least one special character')
            return redirect('bidbuygo:set_password', email=email)
            
        if ' ' in password:
            messages.error(request, 'Password cannot contain spaces')
            return redirect('bidbuygo:set_password', email=email)
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match')
            return redirect('bidbuygo:set_password', email=email)
        
        # Create the user with the custom User model
        user = User.objects.create_user(
            email=email,
            password=password
        )
        
        # Delete the unverified user
        unverified_user.delete()
        
        # Automatically log in the user
        login(request, user)
        
        messages.success(request, 'Account created successfully!')
        return redirect('bidbuygo:home')  # Redirect to home page after successful registration
    
    return render(request, 'bidbuygo/set_password.html', {'email': email})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('bidbuygo:home')
    else:
        form = AuthenticationForm()
    return render(request, 'bidbuygo/user_login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('bidbuygo:home')

@login_required
def place_bid(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    if request.method == 'POST':
        form = BidForm(request.POST)
        if form.is_valid():
            bid_amt = form.cleaned_data['bid_amt']
            
            # Get current bid, defaulting to product price if None
            current_bid = product.current_bid if product.current_bid is not None else product.price
            
            # Check if bid is higher than current bid
            if bid_amt <= current_bid:
                messages.warning(request, 'Your bid must be higher than the current bid.')
                return redirect('bidbuygo:place_bid', product_id=product_id)
            
            # Check if bid is at least the minimum bid amount (product price)
            if bid_amt < product.price:
                messages.warning(request, f'Your bid must be at least ₹{product.price} (minimum bid amount).')
                return redirect('bidbuygo:place_bid', product_id=product_id)
            
            try:
                # Create new bid
                bid = Bidding.objects.create(
            user=request.user,
            product=product,
                    bid_amt=bid_amt,
                    bid_time=timezone.now(),
                    bid_status='pending'
                )
                
                # Update product's current bid and last bid time
                product.current_bid = bid_amt
                product.last_bid_time = bid.bid_time
                product.save()
                
                # Redirect to success page
                return redirect('bidbuygo:bid_success', product_id=product_id)
            except Exception as e:
                messages.error(request, f'Error placing bid: {str(e)}')
                return redirect('bidbuygo:place_bid', product_id=product_id)
    else:
        form = BidForm()
    
    # Get bid history sorted by bid amount
    bid_history = Bidding.objects.filter(product=product).order_by('-bid_amt')
    
    context = {
        'product': product,
        'form': form,
        'bid_history': bid_history,
        'minimum_bid': product.price
    }
    return render(request, 'bidbuygo/place_bid.html', context)

@login_required
def bid_success(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)
    latest_bid = Bidding.objects.filter(
        product=product,
        user=request.user
    ).order_by('-bid_time').first()
    
    context = {
        'product': product,
        'bid': latest_bid
    }
    return render(request, 'bidbuygo/bid_success.html', context)

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
        return redirect('bidbuygo:product_detail', product_id=product_id)
    
    # Check if user has purchased this product
    has_purchased = Order.objects.filter(
        user=request.user,
        product=product,
        status='PAID'
    ).exists()
    
    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.is_verified_purchase = has_purchased
            review.save()
            messages.success(request, 'Review added successfully!')
            return redirect('bidbuygo:product_detail', product_id=product_id)
    else:
        form = ReviewForm()
    
    context = {
        'form': form,
        'product': product,
        'has_purchased': has_purchased
    }
    
    return render(request, 'bidbuygo/add_review.html', context)

@login_required
def user_profile(request):
    try:
        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        
        # Get user's addresses
        addresses = Address.objects.filter(user=request.user)
        
        # Handle profile form submission
        if request.method == 'POST' and 'profile_form' in request.POST:
            profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Profile updated successfully!')
                return redirect('bidbuygo:user_profile')
        else:
            profile_form = UserProfileForm(instance=profile)
        
        # Handle address form submission
        if request.method == 'POST' and 'address_form' in request.POST:
            address_form = AddressForm(request.POST)
            if address_form.is_valid():
                address = address_form.save(commit=False)
                address.user = request.user
                address.save()
                messages.success(request, 'Address added successfully!')
                return redirect('bidbuygo:user_profile')
        else:
            address_form = AddressForm()
        
        # Get user's orders
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
        
        context = {
            'profile': profile,
            'profile_form': profile_form,
            'address_form': address_form,
            'addresses': addresses,
            'orders': orders,
        }
        return render(request, 'bidbuygo/profile.html', context)
    except Exception as e:
        messages.error(request, f'Error accessing profile: {str(e)}')
        return redirect('bidbuygo:home')

@login_required
def order_detail(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        order_items = OrderItem.objects.filter(order=order).select_related('product')
        
        context = {
            'order': order,
            'order_items': order_items,
        }
        return render(request, 'bidbuygo/order_detail.html', context)
    except Exception as e:
        messages.error(request, f'Error accessing order details: {str(e)}')
        return redirect('bidbuygo:order_list')

@login_required
def edit_address(request, address_id):
    try:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        
        if request.method == 'POST':
            form = AddressForm(request.POST, instance=address)
            if form.is_valid():
                form.save()
                messages.success(request, 'Address updated successfully!')
                return redirect('bidbuygo:user_profile')
        else:
            form = AddressForm(instance=address)
        
        context = {
            'form': form,
            'address': address,
        }
        return render(request, 'bidbuygo/edit_address.html', context)
    except Exception as e:
        messages.error(request, f'Error editing address: {str(e)}')
        return redirect('bidbuygo:user_profile')

@login_required
def delete_address(request, address_id):
    try:
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.delete()
        messages.success(request, 'Address deleted successfully!')
    except Exception as e:
        messages.error(request, f'Error deleting address: {str(e)}')
    return redirect('bidbuygo:user_profile')

@login_required
def seller_dashboard(request):
    if not hasattr(request.user, 'seller'):
        messages.error(request, 'You are not authorized to access the seller dashboard.')
        return redirect('bidbuygo:home')
    
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
        return redirect('bidbuygo:home')
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user.seller
            product.product_id = str(uuid.uuid4())[:8]
            product.save()
            messages.success(request, 'Product added successfully!')
            return redirect('bidbuygo:seller_dashboard')
    else:
        form = ProductForm()
    
    context = {
        'form': form,
    }
    return render(request, 'bidbuygo/add_product.html', context)

@login_required
def place_order(request, product_id):
    product = get_object_or_404(Product, product_id=product_id)

    # Prevent auction products from being ordered directly
    if product.product_type == 'Auction':
        messages.error(request, 'Auction products cannot be ordered directly. Please place a bid instead.')
        return redirect('bidbuygo:product_detail', product_id=product_id)
    
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
            return redirect('bidbuygo:order_list')
    else:
        form = OrderForm()
    
    context = {
        'form': form,
        'product': product,
    }
    return render(request, 'bidbuygo/place_order.html', context)

@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
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
        return redirect('bidbuygo:order_list')
    
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
        return redirect('bidbuygo:product_detail', product_id=product_id)
        
    product = get_object_or_404(Product, product_id=product_id)
    try:
        BiddingService.end_auction(product)
        messages.success(request, 'Auction ended successfully!')
    except Exception as e:
        messages.error(request, str(e))
        
    return redirect('bidbuygo:product_detail', product_id=product_id)

@login_required
def payment_page(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        context = {
            'order': order,
            'STRIPE_PUBLISHABLE_KEY': settings.STRIPE_PUBLISHABLE_KEY
        }
        return render(request, 'bidbuygo/payment.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('bidbuygo:home')

@login_required
def create_payment(request, order_id):
    try:
        print("Starting payment creation...")
        print(f"Order ID: {order_id}")
        print(f"User: {request.user}")
        
        order = Order.objects.get(id=order_id, user=request.user)
        print(f"Order found: {order.id}")
        print(f"Order amount: {order.amount}")
        
        # Create a PaymentIntent with the order amount and currency
        intent = stripe.PaymentIntent.create(
            amount=int(order.amount * 100),  # Convert to cents
            currency='inr',
            automatic_payment_methods={
                'enabled': True,
            },
            metadata={
                'order_id': order.id,
                'user_id': request.user.id
            }
        )
        
        print(f"PaymentIntent created: {intent.id}")
        print(f"Client secret: {intent.client_secret}")
        
        return JsonResponse({
            'clientSecret': intent.client_secret
        })
    except Exception as e:
        print(f"Error creating payment: {str(e)}")
        return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)
    except stripe.error.SignatureVerificationError as e:
        return JsonResponse({'error': str(e)}, status=400)
    
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        order_id = payment_intent['metadata']['order_id']
        
        try:
            order = Order.objects.get(id=order_id)
            order.status = 'PAID'
            order.save()
            
            # Create transaction record
            Transaction.objects.create(
                order=order,
                payment_id=payment_intent['id'],
                amount=order.amount,
                status='SUCCESS'
            )
        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
    
    return JsonResponse({'status': 'success'})

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

@login_required
def checkout(request):
    if not request.user.is_authenticated:
        return redirect('bidbuygo:login')
    
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('bidbuygo:cart')
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            try:
                # Get form data
                full_name = form.cleaned_data['full_name']
                phone_number = form.cleaned_data['phone_number']
                address_line1 = form.cleaned_data['address_line1']
                address_line2 = form.cleaned_data['address_line2']
                city = form.cleaned_data['city']
                state = form.cleaned_data['state']
                postal_code = form.cleaned_data['postal_code']
                country = form.cleaned_data['country']

                # Calculate total amount
                total_amount = cart.total_price
                
                # Start transaction
                with transaction.atomic():
                    # Create order
                    order = Order.objects.create(
                        order_id=str(uuid.uuid4())[:8],
                        user=request.user,
                        amount=total_amount,
                        status='PENDING',
                        payment_method='COD',
                        full_name=full_name,
                        phone_number=phone_number,
                        address_line1=address_line1,
                        address_line2=address_line2,
                        city=city,
                        state=state,
                        postal_code=postal_code,
                        country=country
                    )
                    
                    # Create order items and update stock
                    for cart_item in cart.items.all():
                        # Create order item
                        OrderItem.objects.create(
                            order=order,
                            product=cart_item.product,
                            quantity=cart_item.quantity,
                            price=cart_item.product.price,
                            size=cart_item.size
                        )
                        
                        # Check stock availability
                        product_size = ProductSize.objects.select_for_update().get(
                            product=cart_item.product, 
                            size=cart_item.size
                        )
                        
                        if product_size.stock < cart_item.quantity:
                            raise ValidationError(
                                f"Sorry, only {product_size.stock} items available for {cart_item.product.product_name} in size {cart_item.size}"
                            )
                        
                        # Update stock
                        product_size.stock -= cart_item.quantity
                        product_size.save()
                        
                        if product_size.stock <= 0:
                            cart_item.product.is_available = False
                            cart_item.product.save()
                    
                    # Create transaction record for COD
                    Transaction.objects.create(
                        order=order,
                        amount=total_amount,
                        status='SUCCESS',
                        payment_id=f'COD-{order.order_id}'
                    )
                    
                    # Clear the cart
                    cart.items.all().delete()
                    cart.delete()
                    
                    messages.success(request, 'Order placed successfully!')
                    return redirect('bidbuygo:order_success', order_id=order.order_id)
                    
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('bidbuygo:cart')
            except Exception as e:
                messages.error(request, f'Error placing order: {str(e)}')
                return redirect('bidbuygo:cart')
    else:
        form = OrderForm()

    context = {
        'form': form,
        'cart': cart,
    }
    return render(request, 'bidbuygo/checkout.html', context)

@login_required
def order_success(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id, user=request.user)
        context = {
            'order': order,
            'page_title': 'Order Success'
        }
        return render(request, 'bidbuygo/order_success.html', context)
    except Order.DoesNotExist:
        messages.error(request, 'Order not found.')
        return redirect('bidbuygo:home')

@login_required
def delivery_detail(request, order_id):
    try:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        delivery = get_object_or_404(Delivery, order=order)
        tracking_updates = Tracking.objects.filter(delivery=delivery)
        
        context = {
            'order': order,
            'delivery': delivery,
            'tracking_updates': tracking_updates,
        }
        return render(request, 'bidbuygo/delivery_detail.html', context)
    except Exception as e:
        messages.error(request, f'Error accessing delivery details: {str(e)}')
        return redirect('bidbuygo:order_list')

@login_required
def update_delivery_status(request, delivery_id):
    if not request.user.is_staff:
        messages.error(request, 'You are not authorized to update delivery status.')
        return redirect('bidbuygo:home')
    
    try:
        delivery = get_object_or_404(Delivery, id=delivery_id)
        
        if request.method == 'POST':
            new_status = request.POST.get('status')
            location = request.POST.get('location')
            description = request.POST.get('description')
            
            if new_status in dict(Delivery.DELIVERY_STATUS_CHOICES):
                delivery.status = new_status
                delivery.save()
                
                # Create tracking update
                Tracking.objects.create(
                    delivery=delivery,
                    location=location,
                    status=new_status,
                    description=description
                )
                
                messages.success(request, 'Delivery status updated successfully!')
            else:
                messages.error(request, 'Invalid delivery status.')
        
        return redirect('bidbuygo:delivery_detail', order_id=delivery.order.id)
    except Exception as e:
        messages.error(request, f'Error updating delivery status: {str(e)}')
        return redirect('bidbuygo:home')

def send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        # Generate 6-digit OTP
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Delete any existing OTPs for this email
        OTP.objects.filter(email=email).delete()
        
        # Create new OTP
        otp_obj = OTP.objects.create(
            email=email,
            otp=otp,
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        
        # Send email
        send_mail(
            'Your OTP for Email Verification',
            f'Your OTP is: {otp}. It will expire in 5 minutes.',
            'your-email@example.com',  # Replace with your email
            [email],
            fail_silently=False,
        )
        
        return JsonResponse({'status': 'success', 'message': 'OTP sent successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def verify_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        otp = request.POST.get('otp')
        
        try:
            otp_obj = OTP.objects.get(email=email, otp=otp)
            
            if otp_obj.is_expired():
                return JsonResponse({'status': 'error', 'message': 'OTP has expired'})
            
            if otp_obj.is_verified:
                return JsonResponse({'status': 'error', 'message': 'OTP already verified'})
            
            otp_obj.is_verified = True
            otp_obj.save()
            
            return JsonResponse({'status': 'success', 'message': 'Email verified successfully'})
            
        except OTP.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid OTP'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def email_verification(request):
    return render(request, 'email_verification.html')

def check_email(request):
    if request.method == 'GET':
        email = request.GET.get('email')
        is_taken = User.objects.filter(email=email).exists()
        return JsonResponse({'is_taken': is_taken})
    return JsonResponse({'error': 'Invalid request'}, status=400)
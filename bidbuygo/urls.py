from django.urls import path
from . import views

app_name = 'bidbuygo'

urlpatterns = [
    # Home and Product URLs
    path('', views.home, name='home'),
    path('products/', views.product_list, name='products'),
    path('products/<str:product_id>/', views.product_detail, name='product_detail'),
    path('auctions/', views.auction_list, name='auctions'),
    
    # User Authentication URLs
    path('register/', views.user_registration, name='user_registration'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='user_logout'),
    
    # User Profile URLs
    path('profile/', views.user_profile, name='user_profile'),
    
    # Order URLs
    path('orders/', views.order_list, name='order_list'),
    path('place_order/<str:product_id>/', views.place_order, name='place_order'),
    path('complete_payment/<str:order_id>/', views.complete_payment, name='complete_payment'),
    path('add_to_cart/<str:product_id>/', views.add_to_cart, name='add_to_cart'),
    
    # Bidding URLs
    path('place_bid/<str:product_id>/', views.place_bid, name='place_bid'),
    
    # Review URLs
    path('add_review/<str:product_id>/', views.add_review, name='add_review'),
    
    # Seller URLs
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/add_product/', views.add_product, name='add_product'),
    
    # Payment URLs
    path('payment/create/<str:order_id>/', views.create_payment, name='create_payment'),
    path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('payment/refund/<str:transaction_id>/', views.initiate_refund, name='initiate_refund'),
] 
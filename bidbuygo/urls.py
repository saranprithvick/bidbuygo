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
    path('profile/address/edit/<int:address_id>/', views.edit_address, name='edit_address'),
    path('profile/address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    
    # Order URLs
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('place_order/<str:product_id>/', views.place_order, name='place_order'),
    path('complete_payment/<int:order_id>/', views.complete_payment, name='complete_payment'),
    path('add_to_cart/<str:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('update_cart/<str:product_id>/', views.update_cart, name='update_cart'),
    path('remove_from_cart/<str:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    
    # Bidding URLs
    path('place_bid/<str:product_id>/', views.place_bid, name='place_bid'),
    path('bid_success/<str:product_id>/', views.bid_success, name='bid_success'),
    
    # Review URLs
    path('add_review/<str:product_id>/', views.add_review, name='add_review'),
    
    # Seller URLs
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('seller/add_product/', views.add_product, name='add_product'),
    
    # Payment URLs
    path('payment/<int:order_id>/', views.payment_page, name='payment_page'),
    path('payment/create/<int:order_id>/', views.create_payment, name='create_payment'),
    path('payment/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('payment/success/', views.payment_success, name='payment_success'),

    path('order/<int:order_id>/delivery/', views.delivery_detail, name='delivery_detail'),
    path('delivery/<int:delivery_id>/update/', views.update_delivery_status, name='update_delivery_status'),
] 
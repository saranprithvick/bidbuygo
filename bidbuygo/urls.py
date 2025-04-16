from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<str:product_id>/', views.product_detail, name='product_detail'),
    path('register/', views.user_registration, name='user_registration'),
    path('login/', views.user_login, name='user_login'),
    path('logout/', views.user_logout, name='logout'),
    path('orders/', views.order_list, name='order_list'),
    path('place_order/<str:product_id>/', views.place_order, name='place_order'),
    path('complete_payment/<str:order_id>/', views.complete_payment, name='complete_payment'),
] 
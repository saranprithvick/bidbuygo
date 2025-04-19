from .models import Cart, CartItem

def cart_count(request):
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_count = CartItem.objects.filter(cart=cart).count()
        except Cart.DoesNotExist:
            cart_count = 0
    else:
        cart_count = 0
    return {'cart_count': cart_count} 
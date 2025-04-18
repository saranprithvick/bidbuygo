from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product, Bidding, ProductReview, Orders
from django.core.validators import MinValueValidator
from decimal import Decimal

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('user_name', 'email', 'password', 'mobile_number', 'address')

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords don't match")

        return cleaned_data

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'product_type', 'product_condition', 'description', 
                 'category', 'price', 'quantity', 'image', 'warranty_period',
                 'refurbishment_details', 'thrift_condition_details']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'refurbishment_details': forms.Textarea(attrs={'rows': 4}),
            'thrift_condition_details': forms.Textarea(attrs={'rows': 4}),
        }

class BiddingForm(forms.ModelForm):
    bid_amt = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    auto_bid_limit = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    class Meta:
        model = Bidding
        fields = ['bid_amt', 'auto_bid_limit', 'is_auto_bid']
        widgets = {
            'is_auto_bid': forms.CheckboxInput(),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ['rating', 'review_text', 'images']
        widgets = {
            'review_text': forms.Textarea(attrs={'rows': 4}),
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Orders
        fields = ['order_address']
        widgets = {
            'order_address': forms.Textarea(attrs={'rows': 4}),
        }

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, required=False)
    category = forms.CharField(max_length=50, required=False)
    product_type = forms.ChoiceField(
        choices=Product.PRODUCT_TYPE_CHOICES,
        required=False
    )
    product_condition = forms.ChoiceField(
        choices=Product.PRODUCT_CONDITION_CHOICES,
        required=False
    )
    min_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    )
    max_price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False
    ) 
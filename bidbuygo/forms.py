from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product, Bidding, ProductReview, Orders, Seller, Transaction
from django.core.validators import MinValueValidator
from decimal import Decimal

class UserRegistrationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    email = forms.EmailField(required=True)
    mobile_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ('email', 'mobile_number', 'address')

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user

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

class BidForm(forms.Form):
    bid_amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    enable_auto_bid = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    auto_bid_limit = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        min_value=0.01,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        enable_auto_bid = cleaned_data.get('enable_auto_bid')
        auto_bid_limit = cleaned_data.get('auto_bid_limit')
        bid_amount = cleaned_data.get('bid_amount')

        if enable_auto_bid and not auto_bid_limit:
            raise forms.ValidationError("Auto-bid limit is required when auto-bidding is enabled")

        if enable_auto_bid and auto_bid_limit and auto_bid_limit <= bid_amount:
            raise forms.ValidationError("Auto-bid limit must be greater than your bid amount")

        return cleaned_data 
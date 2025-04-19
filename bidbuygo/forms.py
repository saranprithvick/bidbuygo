from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product, Bidding, ProductReview, Orders, Seller, Transaction, ProductSize, UserProfile, Address
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
        fields = [
            'product_name',
            'description',
            'price',
            'product_type',
            'product_condition',
            'quantity',
            'category',
            'image',
            'warranty_period',
            'refurbishment_details',
            'thrift_condition_details'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'refurbishment_details': forms.Textarea(attrs={'rows': 4}),
            'thrift_condition_details': forms.Textarea(attrs={'rows': 4}),
        }

class ProductSizeForm(forms.ModelForm):
    class Meta:
        model = ProductSize
        fields = ['size', 'stock', 'price_adjustment']

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
        fields = ['rating', 'review_text']
        widgets = {
            'rating': forms.RadioSelect(choices=ProductReview.RATING_CHOICES),
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this product...'
            })
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
    bid_amt = forms.DecimalField(
        label='Your Bid Amount',
        min_value=Decimal('0.01'),
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your bid amount',
            'step': '0.01'
        })
    )
    
    def clean_bid_amt(self):
        bid_amt = self.cleaned_data['bid_amt']
        if bid_amt <= 0:
            raise forms.ValidationError("Bid amount must be greater than 0")
        return bid_amt

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'profile_picture']
        widgets = {
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['address_type', 'full_name', 'phone_number', 'address_line1', 
                 'address_line2', 'city', 'state', 'postal_code', 'country', 'is_default']
        widgets = {
            'address_type': forms.Select(attrs={'class': 'form-control'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_default = cleaned_data.get('is_default')
        
        if is_default:
            # If this address is set as default, unset all other default addresses
            Address.objects.filter(user=self.instance.user, is_default=True).update(is_default=False)
        
        return cleaned_data 
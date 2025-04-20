from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Product, Bidding, ProductReview, Seller, Transaction, ProductSize, UserProfile, Address, Order
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.core.exceptions import ValidationError

class CustomFileInput(forms.FileInput):
    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['attrs']['data-text'] = 'No file selected'
        return context

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    mobile_number = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=True)
    city = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    pincode = forms.CharField(max_length=10, required=True)

    class Meta:
        model = User
        fields = ('email', 'mobile_number', 'address', 'city', 'state', 'pincode', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email is required")
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already registered")
        return email

    def clean_mobile_number(self):
        mobile_number = self.cleaned_data.get('mobile_number')
        if not mobile_number:
            raise ValidationError("Mobile number is required")
        if not mobile_number.isdigit():
            raise ValidationError("Mobile number should contain only digits")
        if len(mobile_number) < 10:
            raise ValidationError("Mobile number should be at least 10 digits")
        return mobile_number

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if not pincode:
            raise ValidationError("Pincode is required")
        if not pincode.isdigit():
            raise ValidationError("Pincode should contain only digits")
        if len(pincode) != 6:
            raise ValidationError("Pincode should be 6 digits")
        return pincode

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create user profile with address information
            UserProfile.objects.create(
                user=user,
                phone_number=self.cleaned_data['mobile_number'],
                address=self.cleaned_data['address'],
                city=self.cleaned_data['city'],
                state=self.cleaned_data['state'],
                pincode=self.cleaned_data['pincode']
            )
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
    rating = forms.ChoiceField(
        choices=ProductReview.RATING_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'star-rating',
            'style': 'display: none;'
        })
    )

    class Meta:
        model = ProductReview
        fields = ['rating', 'review_text', 'images']
        widgets = {
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience with this product...'
            }),
            'images': CustomFileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            })
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'phone_number', 'address_line1', 'address_line2', 'city', 'state', 'postal_code', 'country']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'address_line1': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'address_line2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
        }

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not phone_number.isdigit():
            raise forms.ValidationError("Phone number should contain only digits")
        if len(phone_number) < 10:
            raise forms.ValidationError("Phone number should be at least 10 digits")
        return phone_number

    def clean_postal_code(self):
        postal_code = self.cleaned_data.get('postal_code')
        if not postal_code.isdigit():
            raise forms.ValidationError("Postal code should contain only digits")
        if len(postal_code) != 6:
            raise forms.ValidationError("Postal code should be 6 digits")
        return postal_code

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
            'profile_picture': CustomFileInput(attrs={'class': 'form-control'}),
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
from django import forms 
from django.contrib.auth.models import User 
from django.contrib.auth.forms import UserCreationForm 

PAID_CHOICES = (
    ('True', 'Yes'),
    ('False', 'No'),
)
GENDER_CHOICES = (
    ('M', 'Male'),
    ('F', 'Female'),
)
class UserSignupForm(UserCreationForm):
    username = forms.CharField(required = True, widget=forms.TextInput(attrs={
        'placeholder': 'Username'

    }))
    email = forms.EmailField(required = True,widget=forms.EmailInput(attrs={
        'class': '',
        'placeholder':'Email',
        'id':''
        })
       ) 
    password1 = forms.CharField(max_length=27, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password '}))
    password2 = forms.CharField(max_length=27, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password confirm'}))
    phonenumber =   forms.IntegerField(required=True, label= "nothing", widget=forms.NumberInput(attrs={'placeholder': 'Phone number'}))

    class Meta:
        model = User
        fields = ['username','email','password1','password2']
        

class UserUpdateEmailForm(forms.ModelForm):
    email = forms.EmailField(required = True,widget=forms.EmailInput(attrs={
        'class': '',
        'placeholder':'Email',
        'id':''
        })
       ) 
    #username = forms.CharField(required=False)
    class Meta:
        model = User
        fields = ['email']

class UserUpdatePhone(forms.Form):
    phone = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={'placeholder': 'phone number'}))


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username','email']


#class ProfileUpdateForm(forms.ModelForm):
    #image  = forms.ImageField(required=False)
   # class Meta: 
    #    model = Profile
      #  fields = ['image']

class AdminAmountForm(forms.Form):
    estimated_amount = forms.FloatField(required=True, widget=forms.NumberInput(attrs={'placeholder': '0.00'}))
 
class AdminPaidForm(forms.Form):
    paid_option = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAID_CHOICES)

class AdminImageTyped(forms.Form):
    typed = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAID_CHOICES)

class AdminCollectionDone(forms.Form):
    done = forms.ChoiceField(
        widget=forms.RadioSelect, choices=PAID_CHOICES)

class AdminAmountDepositForm(forms.Form):
    deposit = forms.FloatField(required=True, widget=forms.NumberInput(attrs={'placeholder': '0.00'}))

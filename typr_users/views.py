from django.shortcuts import render
from .forms import UserSignupForm
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from .models import Profile, Temp
from django.views.generic import View, UpdateView
# Create your views here.

def signup(request, *args, **kwargs):
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        print(request.POST)
        print('**********************')
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            phone = request.POST['phonenumber']
            gender = "Unknown"
            pp = Temp.objects.create(number= phone, username = username, gender = gender )
            messages.success(request, f'Account created for {username} successfully, login to continue!')
         
            return redirect('typr_users:login')
        print(form.errors)
        print('***********')
    else:
        form = UserSignupForm()
    return render(request, 'typr_users/signup.html', {'form': form})



def numberview(request, *args, **kwargs):
    if request.method == 'POST':
        phone = request.POST['phone']
    
        print(phone)

    return render(request, "sec/number.html")

    
                  
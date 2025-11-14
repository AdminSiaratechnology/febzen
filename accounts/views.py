from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse


# Create your views here.
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get("email")
        password = request.POST.get("password")
        print("mail and password",email,password)
        # Authenticate user using username field OR email
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)

            # Redirect based on role
            if user.role == "admin":
                return redirect('dashboard')   # change with your URL name
            elif user.role == "client":
                return redirect('client_dashboard')  # change with your URL name

            return redirect('/')  # fallback

        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'accounts/login.html')


def logout_view(request):
    logout(request)
    return redirect(reverse('login'))
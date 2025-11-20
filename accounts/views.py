from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from fabzen_app.models import Company


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
                print("helooooooooooooooooooooo")
                
                return redirect('dashboard')
            elif user.role == "client":
                print('client calling here......')
                
                companies = user.client.company.all()
                if companies.count() == 1:
                    request.session['active_company_id'] = companies.first().company_code
                    request.session['needs_company_select'] = False
                    return redirect('select_company')
                request.session['needs_company_select'] = True
                return redirect('select_company')
                # return redirect('login')

            return redirect('login')  # fallback

        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'accounts/login.html')



# def login_view(request):
#     if request.method == 'POST':
#         email = request.POST.get("email")
#         password = request.POST.get("password")

#         # authenticate using email as username
#         user = authenticate(request, username=email, password=password)

#         if user is not None:
#             login(request, user)
#             # Bas direct select_company par bhej do
#             return redirect('select_company')

#         else:
#             messages.error(request, "Invalid email or password!")

#     return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect(reverse('login'))


# @login_required(login_url='/')
def select_company(request):
    if request.method == 'POST':
        company_id = request.POST.get('selected_company')
        if request.user.role == 'client':
            qs = request.user.client.company.filter(id=company_id)
        else:
            qs = Company.objects.filter(user=request.user, id=company_id)
        if qs.exists():
            request.session['active_company_id'] = qs.first().company_code
            request.session['needs_company_select'] = False
            next_url = request.POST.get('next')
            return redirect(next_url or 'dashboard')
        messages.error(request, 'Invalid company selection')
    if request.user.role == 'client':
        companies = request.user.client.company.all()
    else:
        companies = Company.objects.filter(user=request.user)
    return render(request, 'accounts/select_company.html', {
        'companies': companies
    })

from django.shortcuts import render,redirect,get_object_or_404
from .models import Party,Company,CompanyBank
from .forms import PartyForm
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.urls import reverse_lazy

import json
# Create your views here.


def home(request):
    return render(request, 'fabzen_app/dashboard.html')

def company(request):
    return render(request, 'fabzen_app/Masters/company/company.html')


def company_list(request):
    search_query = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
    company = Company.objects.all().order_by('-id')
    # company = Company.objects.filter(status ='active').order_by('-id')
   

    if search_query:
        company = company.filter(
            Q(company_name_street__icontains=search_query) |
            Q(company_name_print__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(zip_code__icontains=search_query)
        )
    
    # if status == '':
    #     company = Company.objects.all().order_by('-id')
    if  status:
        company = Company.objects.filter(status__iexact=status)
        # company = company.filter(status__iexact=status)
    
    page = request.GET.get('page', 10)
    paginator = Paginator(company, 10)
    try:
        companies = paginator.page(page)
    except PageNotAnInteger:
        companies = paginator.page(1)
    except EmptyPage:
        companies = paginator.page(paginator.num_pages)
    context = {
        'company':companies,     
        'is_paginated': True,
        'paginator': paginator

    }
    return render(request, 'fabzen_app/Masters/company/partials/company_list.html',context)

def edit_company(request,pk):
    company = get_object_or_404(Company, id=pk)
    company_banks = CompanyBank.objects.filter(company=company)
    
    if request.method == "POST":
        # ------------------------- Basic Info --------------------
        company.company_name_street = request.POST.get('companystreet')
        company.company_name_print = request.POST.get('cmpprint')
        company.address_line1 = request.POST.get('addressline1')
        company.address_line2 = request.POST.get('addressline2')
        company.address_line3 = request.POST.get('addressline3')
        company.country = request.POST.get('country')
        company.state = request.POST.get('state')
        company.city = request.POST.get('city')
        company.zipcode = request.POST.get('zipcode')
        company.currency = request.POST.get('currancy')

        # ------------------------- Contact Details -------------------
        company.telephone = request.POST.get('telephone')
        company.mobile_no = request.POST.get('mob_no')
        company.fax_no = request.POST.get('fax_no')
        company.email = request.POST.get('email')
        company.website_url = request.POST.get('website')

        # ------------------------- Registration Details -------------------
        company.gst_number = request.POST.get('gstno')
        company.pan_no = request.POST.get('pan_no')
        company.tan_no = request.POST.get('tan_no')
        company.msme_no = request.POST.get('msme_no')
        company.udyan_no = request.POST.get('udyan_no')
        
        # Save the company data
        company.save()
        
        # ------------------------- Bank Details -------------------
        # First delete existing bank details to avoid duplicates
        CompanyBank.objects.filter(company=company).delete()
        
        # Get all bank details from the form - handle both field name formats
        # In edit mode, the field names might be different
        account_holder_names = request.POST.getlist('account_holder_name') or request.POST.getlist('holder_name')
        ac_nos = request.POST.getlist('account_number') or request.POST.getlist('ac_no')
        ifsc_codes = request.POST.getlist('ifsc_code')
        swift_codes = request.POST.getlist('swift_code')
        micr_nos = request.POST.getlist('micr_no') or request.POST.getlist('micr_number')
        bank_names = request.POST.getlist('bank_name')
        branches = request.POST.getlist('branch')
        
        # Create new bank records
        for i in range(len(bank_names)):
            if bank_names[i]:  # Only create if bank name is provided
                CompanyBank.objects.create(
                    company=company,
                    holder_name=account_holder_names[i] if i < len(account_holder_names) else "",
                    account_number=ac_nos[i] if i < len(ac_nos) else "",
                    ifsc_code=ifsc_codes[i] if i < len(ifsc_codes) else "",
                    swift_code=swift_codes[i] if i < len(swift_codes) else "",
                    micr_no=micr_nos[i] if i < len(micr_nos) else "",
                    bank_name=bank_names[i],
                    branch=branches[i] if i < len(branches) else ""
                )
        
        # Redirect to company list page after successful update
        return redirect('company')
    
    context = {
        'company': company,
        'company_banks': company_banks,
        'mode': 'edit'
    }
    return render(request,'fabzen_app/Masters/company/partials/multistep2.html',context)
def toggle_company_status(request, pk):
    company = get_object_or_404(Company, id=pk)
    
    # Toggle status
    if company.status == 'active':
        company.status = 'inactive'
    else:
        company.status = 'active'
    company.save()

    # Re-render only the updated row HTML and return it
    return render(request, 'fabzen_app/Masters/company/partials/company_list.html', {'cmp': company})

def add_company(request):
    if request.method == "POST":

        # ------------------------- Basic Info --------------------
        cmp_steet = request.POST.get('companystreet')
        cmpprint = request.POST.get('cmpprint')
        addressline1 = request.POST.get('addressline1')
        addressline2 = request.POST.get('addressline2')
        addressline3 = request.POST.get('addressline3')
        country = request.POST.get('country')
        state = request.POST.get('state')
        city = request.POST.get('city')
        zipcode = request.POST.get('zipcode')
        currancy = request.POST.get('currancy')

        # ------------------------- END Basic Info --------------------

        # ------------------------------ Contact Details -------------------
        telephone = request.POST.get('telephone')
        mobile_no = request.POST.get('mob_no')
        fax_no = request.POST.get('fax_no')
        email = request.POST.get('email')
        website_url = request.POST.get('website')


        # ------------------------------ END Contact Details -------------------

        # ------------------------------ Registration Details -------------------
        
        
        # ------------------------------ Registration Details -------------------

        gst_number = request.POST.get('gstno')
        pan_no = request.POST.get('pan_no')
        tan_no = request.POST.get('tan_no')
        msme_no = request.POST.get('msme_no')
        udyan_no = request.POST.get('udyan_no')


            
        # ------------------------------  END Registration Details -------------------
            
            
        # ------------------------------  Bank Details -------------------

        # account_holder_name = request.POST.get('holder_name')
        # ac_no = request.POST.get('ac_no')
        # ifsc_code = request.POST.get('ifsc_code')
        # swift_code = request.POST.get('swift_code')
        # micr_no = request.POST.get('micr_no')
        # bank_name = request.POST.get('bank_name')
        # branch = request.POST.get('branch')

        account_holder_names = request.POST.getlist('account_holder_name') or request.POST.getlist('holder_name')
        ac_nos = request.POST.getlist('account_number') or request.POST.getlist('ac_no')
        ifsc_codes = request.POST.getlist('ifsc_code')
        swift_codes = request.POST.getlist('swift_code')
        micr_nos = request.POST.getlist('micr_no') or request.POST.getlist('micr_number')
        bank_names = request.POST.getlist('bank_name')
        branches = request.POST.getlist('branch')



        company = Company.objects.create(
            company_name_street=cmp_steet,
            company_name_print=cmpprint,
            address_line1=addressline1,
            address_line2=addressline2,
            address_line3=addressline3,
            country=country,
            state=state,
            city=city,
            zip_code=zipcode,
            default_currency=currancy,
            telephone=telephone,
            mobile_no=mobile_no,
            fax_no=fax_no,
            email=email,
            website=website_url,
            gst_no=gst_number,
            pan_no=pan_no,
            tan_no=tan_no,
            msme_no=msme_no,
            udyan_no=udyan_no
        )

   

        for i in range(len(account_holder_names)):
            CompanyBank.objects.create(
                company=company,
                holder_name=account_holder_names[i],
                account_number=ac_nos[i],
                ifsc_code=ifsc_codes[i],
                swift_code=swift_codes[i],
                micr_no=micr_nos[i],
                bank_name=bank_names[i],
                branch=branches[i]
            )

        return redirect(reverse_lazy('company'))
        # ----------------------------  END Bank Details -------------------


        
    return render(request,'fabzen_app/Masters/company/partials/multistep3.html',{'mode': 'add'})
# def party_list(request):
    
#     parties_list = Party.objects.all().order_by('-id')
    
#     # पेजिनेशन लॉजिक
#     page = request.GET.get('page', 1)
#     paginator = Paginator(parties_list, 10)  # हर पेज पर 10 पार्टियां दिखाएं
    
#     try:
#         parties = paginator.page(page)
#     except PageNotAnInteger:
#         parties = paginator.page(1)
#     except EmptyPage:
#         parties = paginator.page(paginator.num_pages)
    
#     return render(request, 'fabzen_app/Masters/partials/party_table.html', {
#         'parties': parties,
#         'is_paginated': True,
#         'paginator': paginator
#     })


def party_list(request):
    search_query = request.GET.get('search', '').strip()
    party_type = request.GET.get('type', '').strip()

    parties_list = Party.objects.all().order_by('-id')

    # 🔍 Search filter
    if search_query:
        parties_list = parties_list.filter(
            Q(party_name__icontains=search_query) |
            Q(city__icontains=search_query) |
            Q(gst_number__icontains=search_query) |
            Q(contact_person__icontains=search_query)
        )

    # 🧩 Type filter (optional)
    if party_type:
        parties_list = parties_list.filter(party_type__iexact=party_type)

    # Pagination
    page = request.GET.get('page', 10)
    paginator = Paginator(parties_list, 10)

    try:
        parties = paginator.page(page)
    except PageNotAnInteger:
        parties = paginator.page(1)
    except EmptyPage:
        parties = paginator.page(paginator.num_pages)

    return render(request, 'fabzen_app/Masters/partials/party_table.html', {
        'parties': parties,
        'is_paginated': True,
        'paginator': paginator
    })


def party(request):
    return render(request,'fabzen_app/Masters/Party/party.html')


def add_party(request):
    if request.method == 'POST':
        form = PartyForm(request.POST)
        if form.is_valid():
            form.save()
            parties_list = Party.objects.all().order_by('-id')
            
            # पेजिनेशन लॉजिक
            page = request.GET.get('page', 1)
            paginator = Paginator(parties_list, 10)  # हर पेज पर 10 पार्टियां दिखाएं
            
            try:
                parties = paginator.page(page)
            except PageNotAnInteger:
                parties = paginator.page(1)
            except EmptyPage:
                parties = paginator.page(paginator.num_pages)
                
            # Return only updated table body (HTMX) with trigger to close modal
            response = render(request, 'fabzen_app/Masters/partials/party_table.html', {
                'parties': parties,
                'is_paginated': True,
                'paginator': paginator
            })
            # response['HX-Trigger'] = 'closeModal'
            response['HX-Trigger'] = json.dumps({"partyAdded": "पार्टी सफलतापूर्वक जोड़ी गई है!", "closeModal": True})
            return response
    else:
        form = PartyForm()

    return render(request, 'fabzen_app/Masters/partials/party_form.html', {'form': form})


def edit_party(request, id):
    party = get_object_or_404(Party, id=id)  # fetch existing record

    if request.method == 'POST':
        form = PartyForm(request.POST, instance=party)
        if form.is_valid():
            form.save()
            # After successful edit, return updated table and trigger closing modal (HTMX)
            parties_list = Party.objects.all().order_by('-id')
            page = request.GET.get('page', 1)
            paginator = Paginator(parties_list, 10)

            try:
                parties = paginator.page(page)
            except PageNotAnInteger:
                parties = paginator.page(1)
            except EmptyPage:
                parties = paginator.page(paginator.num_pages)

            response = render(request, 'fabzen_app/Masters/partials/party_table.html', {
                'parties': parties,
                'is_paginated': True,
                'paginator': paginator
            })
            response['HX-Trigger'] = json.dumps({"closeModal": True})
            return response
    else:
        form = PartyForm(instance=party)  # pre-fill form with existing data

    return render(request, 'fabzen_app/Masters/partials/party_form.html', {'form': form,'mode':'edit','id':id})


def view_party(request, id):
    party = get_object_or_404(Party, id=id)
    return render(request, 'fabzen_app/Masters/partials/party_view.html', {
        'party': party
    })


# def add_party(request):
#     if request.method == 'POST':
#         form = PartyForm(request.POST)
#         if form.is_valid():
#             form.save()
#             parties = Party.objects.all().order_by('-id')
#             response = render(request, 'fabzen_app/Masters/partials/party_table.html', {'parties': parties})
#             # 🔥 Send custom trigger to frontend
#             response['HX-Trigger'] = 'partyAdded'
#             return response
#     else:
#         form = PartyForm()
#     return render(request, 'fabzen_app/Masters/partials/party_form.html', {'form': form})

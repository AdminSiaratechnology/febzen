from django.shortcuts import render,redirect,get_object_or_404
from .models import Party,Company,CompanyContact,CompanyRegistraionDetails,CompanyBank
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
    company = Company.objects.all().order_by('-id')
    context = {
        'company':company

    }
    return render(request, 'fabzen_app/Masters/company/partials/company_list.html',context)

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
        mob_no = request.POST.get('mob_no')
        firstname = request.POST.get('firstname')
        email = request.POST.get('email')
        website = request.POST.get('website')

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

        account_holder_names = request.POST.getlist('holder_name')
        ac_nos = request.POST.getlist('ac_no')
        ifsc_codes = request.POST.getlist('ifsc_code')
        swift_codes = request.POST.getlist('swift_code')
        micr_nos = request.POST.getlist('micr_no')
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
            default_currency=currancy
        )

        telephone = request.POST.get('telephone')
        mobile_no = request.POST.get('mob_no')
        fax_no = request.POST.get('fax_no')
        email = request.POST.get('email')
        website_url = request.POST.get('website')


        print("dddddddddddddddddd",fax_no)

        CompanyContact.objects.create(
            company=company,
            telephone=telephone,
            mobile_no=mobile_no,
            fax_no=fax_no,
            email=email,
            website=website_url
        )


         # STEP 3: Registration
        # gst_no = request.POST.get('gst_no')
        # pan_no = request.POST.get('pan_no')
        # tan_no = request.POST.get('tan_no')
        # msme_no = request.POST.get('msme_no')
        # udyan_no = request.POST.get('udyan_no')

        CompanyRegistraionDetails.objects.create(
            company=company,
            gst_no=gst_number,
            pan_no=pan_no,
            tan_no=tan_no,
            msme_no=msme_no,
            udyan_no=udyan_no
        )
        

         # STEP 4: Banks (Multiple)
        bank_count = int(request.POST.get('bank_count', 1))  # number of banks dynamically added
        # for i in range(bank_count):
        #     CompanyBank.objects.create(
        #         company=company,
        #         holder_name= account_holder_name,
        #         account_number=ac_no,
        #         ifsc_code=ifsc_code,
        #         swift_code=swift_code,
        #         micr_no=micr_no,
        #         bank_name=bank_name,
        #         branch=branch
        #     )

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


        
    return render(request,'fabzen_app/Masters/company/partials/multistep.html')
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

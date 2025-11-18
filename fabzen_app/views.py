from django.shortcuts import render,redirect,get_object_or_404
from .models import Client, Party,Company,CompanyBank,Fabric,Size,Garment,Process,Machine,Operator,Ledger,LedgerGroup,PurchaseIndent,PurchaseIndentItem,PurchaseOrder,PurchaseOrderItem,GreyPurchase,GreyPurchaseItem,PurchaseReturn,PurchaseReturnItem,CustomUser
from .forms import PartyForm,FabricForm
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView,CreateView
from django.urls import reverse_lazy
import json
from datetime import date
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
# Create your views here.


def get_garment_details(request, garment_id):
    """HTMX endpoint to fetch garment description and price"""
    try:
        garment = Garment.objects.get(id=garment_id)
        return JsonResponse({
            'description': garment.description or '',
            'price': str(garment.rate_per_piece),
        })
    except Garment.DoesNotExist:
        return JsonResponse({'description': '', 'price': ''})


@login_required(login_url='/')
def home(request):
          
    return render(request, 'fabzen_app/dashboard.html')

@login_required(login_url='/')
def company(request):
    
    return render(request, 'fabzen_app/Masters/company/company.html')

def company_list(request):
    search_query = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
    company = Company.objects.filter(user=request.user).order_by('-id')
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


@login_required(login_url='/')
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

@login_required(login_url='/')
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

        

        account_holder_names = request.POST.getlist('account_holder_name') or request.POST.getlist('holder_name')
        ac_nos = request.POST.getlist('account_number') or request.POST.getlist('ac_no')
        ifsc_codes = request.POST.getlist('ifsc_code')
        swift_codes = request.POST.getlist('swift_code')
        micr_nos = request.POST.getlist('micr_no') or request.POST.getlist('micr_number')
        bank_names = request.POST.getlist('bank_name')
        branches = request.POST.getlist('branch')



        company = Company.objects.create(
            user = request.user,
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

   

        # for i in range(len(account_holder_names)):
        #     CompanyBank.objects.create(
        #         company=company,
        #         holder_name=account_holder_names[i],
        #         account_number=ac_nos[i],
        #         ifsc_code=ifsc_codes[i],
        #         swift_code=swift_codes[i],
        #         micr_no=micr_nos[i],
        #         bank_name=bank_names[i],
        #         branch=branches[i]
        #     )
        for i in range(len(account_holder_names)):
            CompanyBank.objects.create(
                company=company,
                holder_name=account_holder_names[i],
                account_number=ac_nos[i] if i < len(ac_nos) else '',
                ifsc_code=ifsc_codes[i] if i < len(ifsc_codes) else '',
                swift_code=swift_codes[i] if i < len(swift_codes) else '',
                micr_no=micr_nos[i] if i < len(micr_nos) else '',
                bank_name=bank_names[i] if i < len(bank_names) else '',
                branch=branches[i] if i < len(branches) else ''
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
    company_code = request.session.get('active_company_id')

    parties_list = Party.objects.filter(created_by = request.user, company__company_code = company_code).order_by('-id')
    # parties_list = Party.objects.all().order_by('-id')
   

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
    page = request.GET.get('page', 1)
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


@login_required(login_url='/')
def party(request):
    return render(request,'fabzen_app/Masters/Party/party.html')


def add_party(request):
    if request.method == 'POST':
        # form = PartyForm(request.POST)
        # if form.is_valid():
        #     form.save()
            party_name = request.POST.get('party_name')
            party_type = request.POST.get('party_type')
            contact_person = request.POST.get('contact_person')
            mobile = request.POST.get('mobile')
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            pincode = request.POST.get('pincode')
            gstno = request.POST.get('gstno')
            panno = request.POST.get('panno')
            company_id = request.POST.get('company_id')

            company = Company.objects.get(id=company_id)

            

            party = Party.objects.create(party_name=party_name,party_type=party_type,contact_person=contact_person,mobile=mobile,address=address,city=city,state=state,pincode=pincode,gst_number=gstno,pan_number=panno,company=company,created_by=request.user)
            party.save()
            
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
            response['HX-Trigger'] = 'closeModal'
            # response['HX-Trigger'] = json.dumps({"partyAdded": "पार्टी सफलतापूर्वक जोड़ी गई है!", "closeModal": True})
            return response
    else:
        form = PartyForm()

    return render(request, 'fabzen_app/Masters/partials/party_form.html', {'form': form})

from django.contrib import messages
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
            # request.notifications.add('Hello world.')
            messages.success(request, "Company updated successfully!")
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






# ----------------------------------- FABRIC QUALITIEST ---------------------

class FabricListView(LoginRequiredMixin,ListView):
    login_url = '/'
    model = Fabric
    template_name = 'fabzen_app/Masters/fabrics/fabric.html'
    context_object_name = 'fabrics'
    ordering = ['-id']
    paginate_by = 10



# def fabric_list(request):
#     fabric = Fabric.objects.all().order_by('-id')
#     context={
#         'fabrics':fabric
#     }

#     return render(request,'fabzen_app/Masters/fabrics/partials/fabric_list.html',context)

def fabric_list(request):
    search_query = request.GET.get('search', '').strip()
    category_type = request.GET.get('type', '').strip()
    company_code = request.session.get('active_company_id')

    fabrics_qs = Fabric.objects.filter(created_by=request.user,company__company_code = company_code).order_by('-id')
    # fabrics_qs = Fabric.objects.all().order_by('-id')
    if search_query:
        fabrics_qs = fabrics_qs.filter(
            Q(code__icontains=search_query) |
            Q(quality_name__icontains=search_query) |
            Q(construction__icontains=search_query) 
           
        )
    if category_type:
        fabrics_qs = fabrics_qs.filter(category__iexact=category_type)

    # --- Pagination logic ---
    page_number = request.GET.get('page', 1)  # Get ?page= from URL (default: 1)
    paginator = Paginator(fabrics_qs, 10)     # Show 10 fabrics per page

    try:
        fabrics = paginator.page(page_number)
    except Exception:
        fabrics = paginator.page(1)

    context = {
        'fabrics': fabrics,
        'paginator': paginator,
        'is_paginated': True,  # Used by your template
    }

    return render(request, 'fabzen_app/Masters/fabrics/partials/fabric_list.html', context)


def create_fabric(request):
    if request.method == 'POST':
        code = request.POST.get('fabric_code')
        quality_name = request.POST.get('quality_name')
        construction = request.POST.get('construction')
        width = request.POST.get('width')
        gsm = request.POST.get('gsm')
        category = request.POST.get('category')
        rate_per_meter = request.POST.get('rate_per_meter')
        description = request.POST.get('description')
        company_id = request.POST.get('company_id')



        company = Company.objects.get(id=company_id)
        

        
    
        fabric = Fabric.objects.create(code=code,quality_name=quality_name,construction=construction,width=width,gsm=gsm,category=category,rate_per_meter=rate_per_meter,description=description,company=company,created_by=request.user)
        # if not fabric.code:
        #     last = Fabric.objects.order_by('-id').first()
        #     next_num = (last.id + 1) if last else 1
        #     fabric.code = f"Q-{next_num:04d}"
        #     fabric.save()
        messages.success(request, f"Fabic '{fabric.quality_name}' added successfully!")
        return redirect('fabric')
       

def update_fabric(request, pk):
    fabric = get_object_or_404(Fabric, pk=pk)
    
    
    form = FabricForm(request.POST, instance=fabric)
    if form.is_valid():
        updated = form.save(commit=False)
        # preserve existing code if not provided
        if not updated.code:
            updated.code = fabric.code
        updated.save()
        messages.success(request, f"Fabic '{fabric.quality_name}' Updated successfully!")
        return redirect('fabric')
            # Return updated list partial with pagination
            

# ----------------------------------- FABRIC QUALITIEST ---------------------

# ----------------------------------- SIZES ---------------------

@login_required(login_url='/')
def SizesListView(request):
    if request.method == "POST":
       
        size_category = request.POST.get("size_category")
        size_label = request.POST.get("size_label")
        display_order = request.POST.get("display_order")
        chest = request.POST.get("chest") or None
        waist = request.POST.get("waist") or None
        length = request.POST.get("length") or None
        company_id = request.POST.get("company_id")

        company = Company.objects.get(id=company_id)

        # Validation (optional but recommended)
        if not size_category or not size_label:
            messages.error(request, "Please fill in all required fields.")
        else:
            size = Size.objects.create(
                size_category=size_category,
                size_label=size_label,
                display_order=display_order,
                chest=chest,
                waist=waist,
                length=length,
                company = company,
                created_by = request.user
            )
            messages.success(request, f"Size '{size.size_label}' added successfully!")
            return redirect("size")  # <- apne URL name ke hisaab se change karein

    # GET request (show list)
    # sizes = Size.objects.all().order_by("display_order")
    return render(request, "fabzen_app/Masters/sizes/size.html")

# class SizesListView(ListView):
#     model = Size
#     template_name = 'fabzen_app/Masters/sizes/size.html'
#     context_object_name = 'sizes'
#     ordering = ['-id']
#     paginate_by = 10




def size_list(request):
    company_code = request.session.get('active_company_id')
    context = {
        "shirts": Size.objects.filter(created_by=request.user,company__company_code=company_code,size_category="shirts").order_by("display_order"),
        "pants": Size.objects.filter(created_by=request.user,company__company_code=company_code,size_category="pants").order_by("display_order"),
        "ladies": Size.objects.filter(created_by=request.user,company__company_code=company_code,size_category="ladies").order_by("display_order"),
        "kids": Size.objects.filter(created_by=request.user,company__company_code=company_code,size_category="kids").order_by("display_order"),
    }

    return render(request, 'fabzen_app/Masters/sizes/sizelist.html', context)

# def size_list(request):
#     size_qs = Size.objects.all().order_by('-id')

#     # --- Pagination logic ---
#     page_number = request.GET.get('page', 1)  # Get ?page= from URL (default: 1)
#     paginator = Paginator(size_qs, 10)     # Show 10 fabrics per page

#     try:
#         sizes = paginator.page(page_number)
#     except Exception:
#         sizes = paginator.page(1)




#     context = {
#         'fabrics': sizes,
#         'paginator': paginator,
#         'is_paginated': True,  # Used by your template
#     }

#     return render(request, 'fabzen_app/Masters/sizes/sizelist.html', context)


# ----------------------------------- END SIZES ---------------------

# -----------------------------------  Garments ---------------------

@login_required(login_url='/')
def GarmentsListView(request):
    garments = Garment.objects.all().order_by('-id')

    # CREATE Garment
    if request.method == "POST":
        garment_code = request.POST.get('garment_code', '').strip()
        garment_name = request.POST.get('garment_name', '').strip()
        garment_category = request.POST.get('garment_category', '').strip()
        rate_per_meter = request.POST.get('rate_per_meter', '').strip()
        avg_fabric_consumption = request.POST.get('avg_fabric_consumption', '').strip()
        avg_production_time = request.POST.get('avg_production_time', '').strip()
        description = request.POST.get('description', '').strip()
        company_id = request.POST.get('company_id')

        company = Company.objects.get(id=company_id)
        # Validate required fields
        if not garment_code or not garment_name or not garment_category or not rate_per_meter:
            messages.error(request, "Please fill all required fields.")
            return redirect('garments')

        # Check for duplicate garment code
        if Garment.objects.filter(garment_code__iexact=garment_code).exists():
            messages.error(request, f"Garment code '{garment_code}' already exists!")
            return redirect('garments')

        # Create new garment
        Garment.objects.create(
            garment_code=garment_code,
            garment_name=garment_name,
            category=garment_category,
            rate_per_piece=rate_per_meter,
            avg_fabric_consumption=avg_fabric_consumption,
            avg_production_time=avg_production_time,
            description=description,
            company=company,
            created_by = request.user
        )

        messages.success(request, "Garment added successfully!")
        return redirect('garments')

    return render(request, 'fabzen_app/Masters/garments/garments.html', {'garments': garments})


def edit_garment(request, garment_id):
    garment = get_object_or_404(Garment, id=garment_id)
    

    if request.method == "POST":
       
        garment_code = request.POST.get('garment_code', '').strip()
        garment_name = request.POST.get('garment_name', '').strip()
        garment_category = request.POST.get('garment_category', '').strip()
        rate_per_meter = request.POST.get('rate_per_meter', '').strip()
        avg_fabric_consumption = request.POST.get('avg_fabric_consumption', '').strip()
        avg_production_time = request.POST.get('avg_production_time', '').strip()
        description = request.POST.get('description', '').strip()

        # Check if code changed & is unique
        if garment.garment_code != garment_code:
            if Garment.objects.filter(garment_code__iexact=garment_code).exists():
                messages.error(request, f"Garment code '{garment_code}' already exists!")
                return redirect('edit_garment', garment_id=garment.id)

        garment.garment_code = garment_code
        garment.garment_name = garment_name
        garment.category = garment_category
        garment.rate_per_piece = rate_per_meter
        garment.avg_fabric_consumption = avg_fabric_consumption
        garment.avg_production_time = avg_production_time
        garment.description = description
        garment.save()

        messages.success(request, "Garment updated successfully!")
        return redirect('garments')

    # return render(request, 'fabzen_app/Masters/garments/partials/edit_garments.html', {'garment': garment})


def delete_garment(request, garment_id):
    garment = get_object_or_404(Garment, id=garment_id)
    garment.delete()
    messages.success(request, "Garment deleted successfully!")
    return redirect('garments_list')


def garments_list(request):
    search_query = request.GET.get('search', '').strip()
    category_type = request.GET.get('type', '').strip()
    company_code = request.session.get('active_company_id')
    garments_qs = Garment.objects.filter(created_by= request.user,company__company_code=company_code ).order_by('-id')
    # garments_qs = Garment.objects.all().order_by('-id')

    if search_query:
        garments_qs = garments_qs.filter(
            Q(garment_code__icontains=search_query) |
            Q(garment_name__icontains=search_query) |
            Q(category__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if category_type:
        garments_qs = garments_qs.filter(category__iexact=category_type)

    # --- Pagination logic ---
    page_number = request.GET.get('page', 1)  # Get ?page= from URL (default: 1)
    paginator = Paginator(garments_qs, 10)     # Show 10 fabrics per page

    try:
        garments = paginator.page(page_number)
    except Exception:
        garments = paginator.page(1)

    context = {
        'fabrics': garments,
        'paginator': paginator,
        'is_paginated': True,  # Used by your template
    }

    return render(request, 'fabzen_app/Masters/garments/partials/garments_list.html', context)


# ----------------------------------- END Garments ---------------------

# ----------------------------------- Processes ---------------------



# def ProcessesListView(request):
#     garments = Garment.objects.all().order_by('-id')

#     # CREATE Garment
#     if request.method == "POST":
#         process_code = request.POST.get('process_code', '').strip()
        

#         # Validate required fields
#         if not process_code or not garment_name or not garment_category or not rate_per_meter:
#             messages.error(request, "Please fill all required fields.")
#             return redirect('garments')

#         # Check for duplicate garment code
#         if Garment.objects.filter(garment_code__iexact=garment_code).exists():
#             messages.error(request, f"Garment code '{garment_code}' already exists!")
#             return redirect('garments')

#         # Create new garment
#         Garment.objects.create(
#             garment_code=garment_code,
#             garment_name=garment_name,
#             category=garment_category,
#             rate_per_piece=rate_per_meter,
#             avg_fabric_consumption=avg_fabric_consumption,
#             avg_production_time=avg_production_time,
#             description=description,
#         )

#         messages.success(request, "Garment added successfully!")
#         return redirect('garments')

#     return render(request, 'fabzen_app/Masters/processes/processes.html', {'garments': garments})


@login_required(login_url='/')
def ProcessesListView(request):
    processes = Process.objects.all().order_by('-id')

    if request.method == "POST":
        process_code = request.POST.get('process_code', '').strip()
        process_name = request.POST.get('process_name', '').strip()
        process_type = request.POST.get('type', '').strip()
        unit = request.POST.get('unit', '').strip()
        rate = request.POST.get('rate', '').strip()
        average_time = request.POST.get('avg_time', '').strip()
        description = request.POST.get('description', '').strip()
        company_id = request.POST.get('company_id')

        company = Company.objects.get(id=company_id)
        # Validate required fields
        if not process_code or not process_name or not process_type or not unit or not rate:
            messages.error(request, "Please fill all required fields.")
            return redirect('processes')

        # Check for duplicate process code
        if Process.objects.filter(process_code__iexact=process_code).exists():
            messages.error(request, f"Process code '{process_code}' already exists!")
            return redirect('processes')

        # Create the new process
        Process.objects.create(
            process_code=process_code,
            process_name=process_name,
            process_type=process_type,
            unit=unit,
            rate=rate,
            average_time=average_time,
            description=description,
            company=company,
            created_by = request.user
        )

        messages.success(request, f"Process '{process_name}' added successfully!")
        return redirect('processes')

    return render(request, 'fabzen_app/Masters/processes/processes.html', {'processes': processes})




def process_list(request):
    search_query = request.GET.get('search', '').strip()
    category_type = request.GET.get('type', '').strip()
    company_code = request.session.get('active_company_id')
    process_qs = Process.objects.filter(created_by = request.user, company__company_code=company_code).order_by('-id')
    # process_qs = Process.objects.all().order_by('-id')

    if search_query:
        process_qs = process_qs.filter(
            Q(process_code__icontains=search_query) |
            Q(process_name__icontains=search_query) |
            Q(process_type__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    if category_type:
        process_qs = process_qs.filter(process_type__iexact=category_type)

    # --- Pagination logic ---
    page_number = request.GET.get('page', 1)  # Get ?page= from URL (default: 1)
    paginator = Paginator(process_qs, 10)     # Show 10 fabrics per page

    try:
        garments = paginator.page(page_number)
    except Exception:
        garments = paginator.page(1)

    context = {
        'fabrics': garments,
        'paginator': paginator,
        'is_paginated': True,  # Used by your template
    }

    return render(request, 'fabzen_app/Masters/processes/partials/process_list.html', context)



def edit_process(request, pk):
    process = get_object_or_404(Process, pk=pk)

    if request.method == "POST":
        print("edit processssssssss")
        # process.process_code = request.POST.get('process_code', '').strip()
        process.process_name = request.POST.get('process_name', '').strip()
        process.process_type = request.POST.get('type', '').strip()
        process.unit = request.POST.get('unit', '').strip()
        process.rate = request.POST.get('rate', '').strip()
        process.average_time = request.POST.get('avg_time', '').strip()
        process.description = request.POST.get('description', '').strip()

        # Validation
        # if not process.process_code or not process.process_name:
        #     messages.error(request, "Please fill all required fields.")
        #     return redirect('processes')

        process.save()
        messages.success(request, "Process updated successfully!")
        return redirect('processes')

    


# ----------------------------------- END Processes ---------------------


# -----------------------------------  Machine ---------------------



@login_required(login_url='/')
def MachineListView(request):

    if request.method == "POST":
        machine_code = request.POST.get('machine_code', '').strip()
        machine_name = request.POST.get('machine_name', '').strip()
        machine_type = request.POST.get('machine_type', '').strip()
        brand = request.POST.get('brand', '').strip()
        capacity = request.POST.get('capacity', '').strip()
        purchase_date = request.POST.get('purchase_date', '').strip()
        assign_operator_id = request.POST.get('assign_operator', '').strip()

        notes  = request.POST.get('notes', '').strip()
        company_id = request.POST.get('company_id')
        company = Company.objects.get(id=company_id)

       

        # Check for duplicate process code
        if Machine.objects.filter(machine_code__iexact=machine_code).exists():
            messages.error(request, f"Process code '{machine_code}' already exists!")
            return redirect('processes')
        assign_operator = Operator.objects.get(id=assign_operator_id)
        # Create the new process
        Machine.objects.create(
            machine_code=machine_code,
            machine_name=machine_name,
            machine_type=machine_type,
            brand=brand,
            capacity_per_day=capacity,
            purchase_date=purchase_date,
            assigned_operator=assign_operator,
            notes=notes,
            created_by = request.user,
            company = company
        )
        messages.success(request, f"Machine '{machine_name}' added successfully!")
        return redirect('machine')
    operator = Operator.objects.all().order_by('-id')
    context={
        'operators':operator
    }

    return render(request, 'fabzen_app/Masters/machine/machine.html',context)





def machine_list(request):
    
    search_query = request.GET.get('search', '').strip()
    type = request.GET.get('type', '').strip()
    company_code = request.session.get('active_company_id')
    machine_qs = Machine.objects.filter(created_by=request.user,company__company_code=company_code).order_by('-id')
    # machine_qs = Machine.objects.all().order_by('-id')

    if search_query:
        machine_qs = machine_qs.filter(
            Q(machine_code__icontains=search_query) |
            Q(machine_name__icontains=search_query) |
            Q(machine_type__icontains=search_query) |
            Q(brand__icontains=search_query)
        )
    
    if type:
        machine_qs = machine_qs.filter(machine_type__iexact=type)

    # --- Pagination logic ---
    page_number = request.GET.get('page', 1)  # Get ?page= from URL (default: 1)
    paginator = Paginator(machine_qs, 10)     # Show 10 fabrics per page

    try:
        machines = paginator.page(page_number)
    except Exception:
        machines = paginator.page(1)
    
    operator = Operator.objects.all().order_by('-id')

    context = {
        'fabrics': machines,
        'paginator': paginator,
        'is_paginated': True,  # Used by your template
        'operator':operator
    }

    return render(request, 'fabzen_app/Masters/machine/partials/machine_list.html', context)



from datetime import datetime
def edit_machine(request, pk):
    
    machine = get_object_or_404(Machine, pk=pk)

    if request.method == "POST":
        operator_id = request.POST.get('assign_operator', '').strip()
        assigned_operator = Operator.objects.get(id=operator_id)
        # process.process_code = request.POST.get('process_code', '').strip()
        machine.machine_name = request.POST.get('machine_name', '').strip()
        machine.machine_type  = request.POST.get('machine_type', '').strip()
        machine.brand = request.POST.get('brand', '').strip()
        machine.capacity_per_day = request.POST.get('capacity', '').strip()
        # machine.purchase_date = request.POST.get('purchase_date', '').strip()
       
        machine.notes = request.POST.get('notes', '').strip()
        purchase_date_str = request.POST.get('purchase_date', '').strip()


        
        machine.assigned_operator = assigned_operator
        # Validation
        # if not process.process_code or not process.process_name:
        #     messages.error(request, "Please fill all required fields.")
        #     return redirect('processes')


        if purchase_date_str:
                machine.purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
        machine.save()
        messages.success(request, "Machine updated successfully!")
        return redirect('machine')

# ----------------------------------- END Machine ---------------------



# ----------------------------------- Operator ---------------------



# def OperatorListView(request):
    

#     if request.method == "POST":
#         machine_code = request.POST.get('machine_code', '').strip()
#         machine_name = request.POST.get('machine_name', '').strip()
#         machine_type = request.POST.get('machine_type', '').strip()
#         brand = request.POST.get('brand', '').strip()
#         capacity = request.POST.get('capacity', '').strip()
#         purchase_date = request.POST.get('purchase_date', '').strip()
#         assign_operator = request.POST.get('assign_operator', '').strip()

#         notes  = request.POST.get('notes', '').strip()

       

#         # Check for duplicate process code
#         if Machine.objects.filter(machine_code__iexact=machine_code).exists():
#             messages.error(request, f"Process code '{machine_code}' already exists!")
#             return redirect('processes')

#         # Create the new process
#         Machine.objects.create(
#             machine_code=machine_code,
#             machine_name=machine_name,
#             machine_type=machine_type,
#             brand=brand,
#             capacity_per_day=capacity,
#             purchase_date=purchase_date,
#             assigned_operator=assign_operator,
#             notes=notes
#         )
#         messages.success(request, f"Process '{machine_name}' added successfully!")
#         return redirect('machine')

#     return render(request, 'fabzen_app/Masters/operators/operator.html')

@login_required(login_url='/')
def OperatorListView(request):
    if request.method == "POST":
        operator_code = request.POST.get('operator_code', '').strip()
        full_name = request.POST.get('full_name', '').strip()
        department = request.POST.get('department', '').strip()
        mobile_number = request.POST.get('mobile_number', '').strip()
        skills = request.POST.get('skills', '').strip()
        date_of_joining = request.POST.get('date_of_joining', '').strip()
        daily_wage = request.POST.get('daily_wage', '').strip()
        address = request.POST.get('address', '').strip()
        company_id = request.POST.get('company_id')

        # ✅ Check for duplicate operator code
        if Operator.objects.filter(operator_code__iexact=operator_code).exists():
            messages.error(request, f"Operator code '{operator_code}' already exists!")
            return redirect('operator-list')
        company = Company.objects.get(id=company_id)
        # ✅ Create and save operator
        Operator.objects.create(
            operator_code=operator_code,
            full_name=full_name,
            department=department,
            mobile_number=mobile_number,
            skills=skills,
            date_of_joining=date_of_joining,
            daily_wage=daily_wage,
            address=address,
            company = company,
            created_by = request.user
        )

        messages.success(request, f"Operator '{full_name}' added successfully!")
        return redirect('operator')

    # ✅ Fetch all operators for listing
    operators = Operator.objects.all().order_by('operator_code')
    return render(request, 'fabzen_app/Masters/operators/operator.html', {'operators': operators})




def operator_list(request):
    
    search_query = request.GET.get('search', '').strip()
    type = request.GET.get('type', '').strip()
    company_code = request.session.get('active_company_id')
    operator_qs = Operator.objects.filter(created_by=request.user,company__company_code=company_code).order_by('-id')
    # operator_qs = Operator.objects.all().order_by('-id')
 

    if search_query:
        operator_qs = operator_qs.filter(
            Q(operator_code__icontains=search_query) |
            Q(full_name__icontains=search_query) |
            Q(department__icontains=search_query) |
            Q(mobile_number__icontains=search_query) |
            Q(skills__icontains=search_query) 
            
        )
    
    if type:
        operator_qs = operator_qs.filter(department__iexact=type)

    # --- Pagination logic ---
    page_number = request.GET.get('page', 1)  # Get ?page= from URL (default: 1)
    paginator = Paginator(operator_qs, 10)     # Show 10 fabrics per page
    print("paginatorsssss",paginator)

    try:
        operator = paginator.page(page_number)
    except Exception:
        operator = paginator.page(1)

    context = {
        'operator': operator,
        'paginator': paginator,
        'is_paginated': True,  # Used by your template
    }

    return render(request, 'fabzen_app/Masters/operators/partials/operator_list.html', context)





# def edit_operator(request, pk):
    
#     operator = get_object_or_404(Operator, pk=pk)

#     if request.method == "POST":
        
#         # process.process_code = request.POST.get('process_code', '').strip()
#         machine.machine_name = request.POST.get('machine_name', '').strip()
#         machine.machine_type  = request.POST.get('machine_type', '').strip()
#         machine.brand = request.POST.get('brand', '').strip()
#         machine.capacity_per_day = request.POST.get('capacity', '').strip()
#         # machine.purchase_date = request.POST.get('purchase_date', '').strip()
#         machine.assigned_operator = request.POST.get('assign_operator', '').strip()
#         machine.notes = request.POST.get('notes', '').strip()
#         purchase_date_str = request.POST.get('purchase_date', '').strip()
#         # Validation
#         # if not process.process_code or not process.process_name:
#         #     messages.error(request, "Please fill all required fields.")
#         #     return redirect('processes')


#         if purchase_date_str:
#                 machine.purchase_date = datetime.strptime(purchase_date_str, '%Y-%m-%d').date()
#         machine.save()
#         messages.success(request, "Machine updated successfully!")
#         return redirect('operator')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Operator
from datetime import datetime

def edit_operator(request, pk):
    operator = get_object_or_404(Operator, pk=pk)

    if request.method == "POST":
        # We don't allow editing of operator_code since it’s disabled in HTML
        operator.full_name = request.POST.get('full_name', '').strip()
        operator.department = request.POST.get('department', '').strip()
        operator.mobile_number = request.POST.get('mobile_number', '').strip()
        operator.skills = request.POST.get('skills', '').strip()
        operator.address = request.POST.get('address', '').strip()
        operator.status = request.POST.get('status', '').strip()

        # Handle date_of_joining (convert string to date)
        date_of_joining_str = request.POST.get('date_of_joining', '').strip()
        if date_of_joining_str:
            try:
                operator.date_of_joining = datetime.strptime(date_of_joining_str, '%Y-%m-%d').date()
            except ValueError:
                messages.error(request, "Invalid date format for Date of Joining.")
                return redirect('operator')

        # Handle daily_wage (convert to decimal)
        daily_wage_str = request.POST.get('daily_wage', '').strip()
        if daily_wage_str:
            try:
                operator.daily_wage = float(daily_wage_str)
            except ValueError:
                messages.error(request, "Invalid value for Daily Wage.")
                return redirect('operator')

        # Save the updated record
        operator.save()

        messages.success(request, f"Operator '{operator.full_name}' updated successfully!")
        return redirect('operator')

    # In case of GET request (optional — e.g., if editing via separate page)
    

# ----------------------------------- END Operator ---------------------



# ----------------------------------- Ledger Operator ---------------------


# def LedgerListView(request):
#     if request.method == "POST":
#         ledger_code = request.POST.get('ledger_code', '').strip()
#         ledger_name = request.POST.get('ledger_name', '').strip()
#         group_id= request.POST.get('ledger_group', '').strip()
#         opening_balance = request.POST.get('opening_balance', '').strip()
#         balance_type = request.POST.get('opening_balance', '').strip()
       

#         # ✅ Check for duplicate operator code
#         if Ledger.objects.filter(ledger_code__iexact=ledger_code).exists():
#             messages.error(request, f"Ledger code '{ledger_code}' already exists!")
#             return redirect('ledger')

#         ledger_group = LedgerGroup.objects.get(id=group_id)
#         # ✅ Create and save operator
#         Ledger.objects.create(
#             ledger_code=ledger_code,
#             ledger_name=ledger_name,
#             ledger_group=ledger_group,
#             opening_balance=opening_balance,
#             balance_type=balance_type,
            
#         )

#         messages.success(request, f"Ledger '{ledger_name}' added successfully!")
#         return redirect('ledger')

#     # ✅ Fetch all operators for listing
    
#     ledger_group = LedgerGroup.objects.all().order_by('-id')
#     return render(request, 'fabzen_app/Masters/ledgers/ledger.html',{'ledger_group':ledger_group})


@login_required(login_url='/')
def LedgerListView(request):
    if request.method == "POST":
        ledger_code = request.POST.get('ledger_code', '').strip()
        ledger_name = request.POST.get('ledger_name', '').strip()
        group_id = request.POST.get('ledger_group', '').strip()
        opening_balance = request.POST.get('opening_balance', '').strip()
        balance_type = request.POST.get('balance_type', '').strip()  # ✅ fixed field name
        company_id = request.POST.get('company_id')

        # ✅ Validate and convert opening_balance
        opening_balance = int(opening_balance) if opening_balance else 0

        # ✅ Check for duplicate ledger code
        if Ledger.objects.filter(ledger_code__iexact=ledger_code).exists():
            messages.error(request, f"Ledger code '{ledger_code}' already exists!")
            return redirect('ledger')

        try:
            ledger_group = LedgerGroup.objects.get(id=group_id)
        except LedgerGroup.DoesNotExist:
            messages.error(request, "Invalid ledger group selected.")
            return redirect('ledger')

        company = Company.objects.get(id=company_id)
        # ✅ Create and save Ledger
        Ledger.objects.create(
            ledger_code=ledger_code,
            ledger_name=ledger_name,
            ledger_group=ledger_group,
            opening_balance=opening_balance,
            balance_type=balance_type,
            company = company,
            created_by = request.user
        )

        messages.success(request, f"Ledger '{ledger_name}' added successfully!")
        return redirect('ledger')

    # ✅ Fetch all ledger groups for listing
    ledger_group = LedgerGroup.objects.all().order_by('-id')
    return render(request, 'fabzen_app/Masters/ledgers/ledger.html', {'ledger_group': ledger_group})


def ledger_list(request):
    
    search_query = request.GET.get('search', '').strip()
    type = request.GET.get('type', '').strip()
    company_code = request.session.get('active_company_id')
    ledger_qs = Ledger.objects.filter(created_by=request.user,company__company_code=company_code).order_by('-id')
    # ledger_qs = Ledger.objects.all().order_by('-id')
    ledger_group = LedgerGroup.objects.filter(created_by=request.user,company__company_code=company_code).order_by('-id')
    # ledger_group = LedgerGroup.objects.all().order_by('-id')

    if search_query:
        ledger_qs = ledger_qs.filter(
            Q(ledger_code__icontains=search_query) |
            Q(ledger_name__icontains=search_query) |
            Q(ledger_group__name__icontains=search_query) |
            Q(ledger_group__type__icontains=search_query) |
            Q(balance_type__icontains=search_query) 
        )
    
    if type:
        ledger_qs = ledger_qs.filter(ledger_group__type__iexact=type)

    # --- Pagination logic ---
    page_number = request.GET.get('page', 1)  # Get ?page= from URL (default: 1)
    paginator = Paginator(ledger_qs, 10)     # Show 10 ledgers per page
  
    try:
        ledgers = paginator.page(page_number)
    except PageNotAnInteger:
        ledgers = paginator.page(1)
    except EmptyPage:
        ledgers = paginator.page(paginator.num_pages)

    context = {
        'ledgers': ledgers,
        'paginator': paginator,
        'is_paginated': True,  # Used by your template
        'ledger_group':ledger_group
    }

    return render(request, 'fabzen_app/Masters/ledgers/partials/ledger_list.html', context)


# ----------------------------------- Ledger Group ---------------------

def add_ledger_group(request):
    if request.method == "POST":
        name = request.POST.get('name', '').strip()
        group_type = request.POST.get('type', '').strip()
        company_id = request.POST.get('company_id')
        # Validation
        if not name or not group_type:
            return HttpResponse("<div class='alert alert-danger'>Group name and type are required!</div>")
        
        # Check if group name already exists
        if LedgerGroup.objects.filter(name__iexact=name).exists():
            return HttpResponse("<div class='alert alert-warning'>Group name already exists! Please use a different name.</div>")
            
        # Create the ledger group
        company = Company.objects.get(id=company_id)
        new_group = LedgerGroup.objects.create(
            name=name,
            type=group_type,
            company=company,
            created_by = request.user
        )
        
        # Return success response with trigger to close modal and reopen ledger modal
        response = HttpResponse()
        response['HX-Trigger'] = json.dumps({
            "closeGroupModal": True,
            "reopenLedgerModal": True,
            "newGroupId": new_group.id
        })
        return response
        
    return HttpResponse("<div class='alert alert-danger'>Invalid request method!</div>")


def edit_ledger(request, pk):
    ledger = get_object_or_404(Ledger, pk=pk)

    if request.method == "POST":
        # print("edit ledgersssssssss..........")
        # ledger_code = request.POST.get('ledger_code', '').strip()
        ledger_name = request.POST.get('ledger_name', '').strip()
        group_id = request.POST.get('ledger_group', '').strip()
        opening_balance = request.POST.get('opening_balance', '').strip()
        balance_type = request.POST.get('balance_type', '').strip()

        # 🧩 Validate group exists
        ledger_group = get_object_or_404(LedgerGroup, id=group_id)

        # 🛠 Update fields (not create)
        # ledger.ledger_code = ledger_code
        ledger.ledger_name = ledger_name
        ledger.ledger_group = ledger_group
        ledger.opening_balance = opening_balance
        ledger.balance_type = balance_type

        # 💾 Save updated record
        ledger.save()

        messages.success(request, f"Ledger '{ledger_name}' updated successfully!")
        return redirect('ledger')  # ✅ Redirect to 'ledger' URL name

    # If GET request, render the edit page/modal
    ledger_group = LedgerGroup.objects.all().order_by('-id')
    context = {
        'ledger': ledger,
        'ledger_group': ledger_group
    }
    return render(request, 'fabzen_app/Masters/ledgers/edit_ledger.html', context)

# ----------------------------------- END Ledger ---------------------



# -----------------------------------  BOM & Boo ---------------------

def BomListView(request):
    
    return render(request, 'fabzen_app/Masters/bom/bom.html')

# ----------------------------------- END BOM & Boo ---------------------





# ----------------------------------- Indent ---------------------
# def IndentListView(request):
#     garment = Garment.objects.all()
#     context = {
#         'garment':garment
#     }
#     return render(request,'fabzen_app/Purchase/PurchaseIndent/indent.html',context)





# def IndentListView(request):
#     garment = Garment.objects.all()

#     if request.method == "POST":
#         # Get Indent main fields
#         indent_date = request.POST.get('indent_date')  # from inputConstruction
#         department = request.POST.get('department')
#         priority = request.POST.get('priority')
#         required_date = request.POST.get('required_date')
#         remarks = request.POST.get('purpose')

#         # ✅ Generate a unique indent number automatically
#         last_indent = PurchaseIndent.objects.order_by('-id').first()
#         if last_indent:
#             new_number = int(last_indent.indent_no.split('-')[-1]) + 1
#         else:
#             new_number = 1
#         indent_no = f"PI-{new_number:04d}"

#         # ✅ Create PurchaseIndent
#         indent = PurchaseIndent.objects.create(
#             indent_no=indent_no,
#             department=department,
#             indent_date=indent_date,
#             required_date=required_date,
#             priority=priority,
#             # remarks=remarks,
#             status='Pending'
#         )

#         # ✅ Now handle multiple item rows
#         item_descriptions = request.POST.getlist('item_description[]')
#         quantities = request.POST.getlist('quantity[]')
#         units = request.POST.getlist('unit[]')
#         item_remarks = request.POST.getlist('remarks[]')

#         for i in range(len(item_descriptions)):
#             garment_name = item_descriptions[i]
#             quantity = quantities[i]
#             unit = units[i]
#             remark = item_remarks[i]

#             if garment_name and quantity:  # avoid empty rows
#                 try:
#                     garment_obj = Garment.objects.get(garment_name=garment_name)
#                 except Garment.DoesNotExist:
#                     continue

#                 PurchaseIndentItem.objects.create(
#                     indent=indent,
#                     garment=garment_obj,
#                     quantity=quantity,
#                     uom=unit,
#                     remarks=remark
#                 )

#         return redirect('indent')  # redirect after saving

#     context = {
#         'garment': garment
#     }
#     return render(request, 'fabzen_app/Purchase/PurchaseIndent/indent.html', context)

@login_required(login_url='/')
def IndentListView(request):
    garment = Garment.objects.all()
    pending = PurchaseIndent.objects.filter(status='Pending').count()
    approved = PurchaseIndent.objects.filter(status='Approved').count()
    rejected = PurchaseIndent.objects.filter(status='Rejected').count()
    converted = PurchaseIndent.objects.filter(status='Close').count()

    if request.method == "POST":
        # Get main fields
        indent_date = request.POST.get('indent_date')
        department = request.POST.get('department')
        priority = request.POST.get('priority')
        requested_by = request.POST.get('requested_by')
        required_date = request.POST.get('required_date')
        remarks = request.POST.get('purpose')
        

        # ✅ Generate unique indent number
        last_indent = PurchaseIndent.objects.order_by('-id').first()
        if last_indent:
            new_number = int(last_indent.indent_no.split('-')[-1]) + 1
        else:
            new_number = 1
        indent_no = f"PI-{new_number:04d}"

        # ✅ Create main PurchaseIndent record
        indent = PurchaseIndent.objects.create(
            indent_no=indent_no,
            department=department,
            indent_date=indent_date,
            required_date=required_date,
            priority=priority,
            requested_by=requested_by,
            remarks=remarks,
            status='Pending'
        )

        # ✅ Get list fields
        item_descriptions = request.POST.getlist('item_description[]')
        quantities = request.POST.getlist('quantity[]')
        units = request.POST.getlist('unit[]')
        item_remarks = request.POST.getlist('description[]')

        # ✅ Loop through all items
        for i in range(len(item_descriptions)):
            garment_id = item_descriptions[i]
            quantity = quantities[i]
            unit = units[i]
            remark = item_remarks[i]

            if garment_id and quantity:
                try:
                    garment_obj = Garment.objects.get(id=garment_id)
                except Garment.DoesNotExist:
                    continue

                PurchaseIndentItem.objects.create(
                    indent=indent,
                    garment=garment_obj,
                    quantity=quantity,
                    uom=unit,
                    remarks=remark
                )

        messages.success(request, f"Purchase Indent {indent.indent_no} created successfully!")
        return redirect('indent')

    context = {
        'garment': garment,
        'pending' : pending,
        'approved' : approved,
        'rejected' : rejected,
        'converted' : converted,
        
    }
    return render(request, 'fabzen_app/Purchase/PurchaseIndent/indent.html', context)

@login_required(login_url='/')
def add_indent(request):
    garment = Garment.objects.all()
    
    if request.method == "POST":
        # Get main fields
        indent_date = request.POST.get('indent_date')
        department = request.POST.get('department')
        priority = request.POST.get('priority')
        requested_by = request.POST.get('requested_by')
        required_date = request.POST.get('required_date')
        remarks = request.POST.get('purpose')
        

        # ✅ Generate unique indent number
        last_indent = PurchaseIndent.objects.order_by('-id').first()
        if last_indent:
            new_number = int(last_indent.indent_no.split('-')[-1]) + 1
        else:
            new_number = 1
        indent_no = f"PI-{new_number:04d}"

        # ✅ Create main PurchaseIndent record
        indent = PurchaseIndent.objects.create(
            indent_no=indent_no,
            department=department,
            indent_date=indent_date,
            required_date=required_date,
            priority=priority,
            requested_by=requested_by,
            remarks=remarks,
            status='Pending'
        )

        # ✅ Get list fields
        item_descriptions = request.POST.getlist('item_description[]')
        quantities = request.POST.getlist('quantity[]')
        units = request.POST.getlist('unit[]')
        item_remarks = request.POST.getlist('description[]')

        # ✅ Loop through all items
        for i in range(len(item_descriptions)):
            garment_id = item_descriptions[i]
            quantity = quantities[i]
            unit = units[i]
            remark = item_remarks[i]

            if garment_id and quantity:
                try:
                    garment_obj = Garment.objects.get(id=garment_id)
                except Garment.DoesNotExist:
                    continue

                try:
                    quantity_decimal = Decimal(quantity)
                except:
                    quantity_decimal = Decimal('0')

                PurchaseIndentItem.objects.create(
                    indent=indent,
                    garment=garment_obj,
                    quantity=quantity_decimal,  # ✅ string → Decimal
                    uom=unit,
                    remarks=remark
                )

        messages.success(request, f"Purchase Indent {indent.indent_no} created successfully!")
        return redirect('indent')

    context = {
        'garment': garment
    }
    return render(request, 'fabzen_app/Purchase/PurchaseIndent/adding_purchase_indent.html', context)





def indent_list(request):
    
    search_query = request.GET.get('search', '').strip()
    
    type = request.GET.get('type', '').strip()
    purchase_qs = PurchaseIndent.objects.all().order_by('-id')
    garment = Garment.objects.all()
    # ledger_group = LedgerGroup.objects.all().order_by('-id')

    if search_query:
        purchase_qs = purchase_qs.filter(
            Q(indent_no__icontains=search_query) |
            Q(department__icontains=search_query) 
        )
        
    
    if type:
        purchase_qs = purchase_qs.filter(status__iexact=type)

    # --- Pagination logic ---
    page_number = request.GET.get('page', 1)  # Get ?page= from URL (default: 1)
    paginator = Paginator(purchase_qs, 10)     # Show 10 ledgers per page
  
    try:
        indents = paginator.page(page_number)
    except PageNotAnInteger:
        indents = paginator.page(1)
    except EmptyPage:
        indents = paginator.page(paginator.num_pages)
    

    context = {
        'indents': indents,
        'paginator': paginator,
        'is_paginated': True,  # Used by your template
        # 'ledger_group':ledger_group
        'garment':garment
    }

    return render(request, 'fabzen_app/Purchase/PurchaseIndent/partials/purchase_list.html', context)

    #     return redirect('indent')




# def edit_indent(request):
#     garment = Garment.objects.all()

#     if request.method == "POST":
#         # Get main fields
#         indent_date = request.POST.get('indent_date')
#         department = request.POST.get('department')
#         priority = request.POST.get('priority')
#         required_date = request.POST.get('required_date')
#         remarks = request.POST.get('purpose')

#         # ✅ Generate unique indent number
#         last_indent = PurchaseIndent.objects.order_by('-id').first()
#         if last_indent:
#             new_number = int(last_indent.indent_no.split('-')[-1]) + 1
#         else:
#             new_number = 1
#         indent_no = f"PI-{new_number:04d}"

#         # ✅ Create main PurchaseIndent record
#         indent = PurchaseIndent.objects.create(
#             indent_no=indent_no,
#             department=department,
#             indent_date=indent_date,
#             required_date=required_date,
#             priority=priority,
#             remarks=remarks,
#             status='Pending'
#         )

#         # ✅ Get list fields
#         item_descriptions = request.POST.getlist('item_description[]')
#         quantities = request.POST.getlist('quantity[]')
#         units = request.POST.getlist('unit[]')
#         item_remarks = request.POST.getlist('remarks[]')

#         # ✅ Loop through all items
#         for i in range(len(item_descriptions)):
#             garment_id = item_descriptions[i]
#             quantity = quantities[i]
#             unit = units[i]
#             remark = item_remarks[i]

#             if garment_id and quantity:
#                 try:
#                     garment_obj = Garment.objects.get(id=garment_id)
#                 except Garment.DoesNotExist:
#                     continue

#                 PurchaseIndentItem.objects.create(
#                     indent=indent,
#                     garment=garment_obj,
#                     quantity=quantity,
#                     uom=unit,
#                     remarks=remark
#                 )

#         messages.success(request, f"Purchase Indent {indent.indent_no} created successfully!")
#         return redirect('indent')

#     context = {
#         'garment': garment
#     }
#     return render(request, 'fabzen_app/Purchase/PurchaseIndent/indent.html', context)


# def edit_indent(request, pk):
#     indent = get_object_or_404(PurchaseIndent, pk=pk)
#     garment = Garment.objects.all()

#     if request.method == "POST":
#         # 🔹 Update main fields
#         indent.indent_date = request.POST.get('indent_date')
#         indent.department = request.POST.get('department')
#         indent.priority = request.POST.get('priority')
#         indent.requested_by = request.POST.get('requested_by')
#         indent.required_date = request.POST.get('required_date')
#         indent.remarks = request.POST.get('purpose')

#         indent.save()

#         # 🔹 Remove old items first (to replace with new ones)
#         indent.items.all().delete()

#         # 🔹 Get new item list fields
#         item_descriptions = request.POST.getlist('item_description[]')
#         quantities = request.POST.getlist('quantity[]')
#         units = request.POST.getlist('unit[]')
#         item_remarks = request.POST.getlist('description[]')

#         # 🔹 Recreate all items
#         for i in range(len(item_descriptions)):
#             garment_id = item_descriptions[i]
#             quantity = quantities[i]
#             unit = units[i]
#             remark = item_remarks[i]

#             if garment_id and quantity:
#                 try:
#                     garment_obj = Garment.objects.get(id=garment_id)
#                 except Garment.DoesNotExist:
#                     continue

#                 PurchaseIndentItem.objects.create(
#                     indent=indent,
#                     garment=garment_obj,
#                     quantity=quantity,
#                     uom=unit,
#                     remarks=remark
#                 )

#         messages.success(request, f"Purchase Indent {indent.indent_no} updated successfully!")
#         return redirect('indent')

#     context = {
#         'indent': indent,
#         'garment': garment,
#     }
#     return render(request, 'fabzen_app/Purchase/PurchaseIndent/edit_indentt.html', context)
#     # return render(request, 'fabzen_app/Purchase/PurchaseIndent/indent_edit.html', context)

from decimal import Decimal
@login_required(login_url='/')
def edit_indent(request, pk):
    indent = get_object_or_404(PurchaseIndent, pk=pk)
    garment = Garment.objects.all()

    if request.method == "POST":
        indent.indent_date = request.POST.get('indent_date')
        indent.department = request.POST.get('department')
        indent.priority = request.POST.get('priority')
        indent.requested_by = request.POST.get('requested_by')
        indent.required_date = request.POST.get('required_date')
        indent.remarks = request.POST.get('purpose')
        indent.save()

        # Collect posted lists for items
        item_descriptions = request.POST.getlist('item_description[]')
        quantities = request.POST.getlist('quantity[]')
        units = request.POST.getlist('unit[]')
        item_remarks = request.POST.getlist('description[]')
        item_ids = request.POST.getlist('item_id[]')

        processed_existing_ids = set()

        # Iterate over posted rows and update or create items accordingly
        total_rows = len(item_descriptions)
        for i in range(total_rows):
            garment_id = item_descriptions[i] if i < len(item_descriptions) else None
            quantity = quantities[i] if i < len(quantities) else None
            unit = units[i] if i < len(units) else ''
            remark = item_remarks[i] if i < len(item_remarks) else ''
            item_id = item_ids[i] if i < len(item_ids) else ''

            # Skip completely blank rows
            if not garment_id or not quantity:
                continue

            try:
                garment_obj = Garment.objects.get(id=garment_id)
            except Garment.DoesNotExist:
                continue

            # Convert quantity safely to Decimal
            try:
                quantity_decimal = Decimal(quantity)
            except Exception:
                quantity_decimal = Decimal('0')

            if item_id:
                # Update existing item if it belongs to this indent
                try:
                    existing_item = PurchaseIndentItem.objects.get(id=item_id, indent=indent)
                    existing_item.garment = garment_obj
                    existing_item.quantity = quantity_decimal
                    existing_item.uom = unit
                    existing_item.remarks = remark
                    existing_item.save()
                    processed_existing_ids.add(existing_item.id)
                except PurchaseIndentItem.DoesNotExist:
                    # If the posted ID does not exist, create a new item
                    new_item = PurchaseIndentItem.objects.create(
                        indent=indent,
                        garment=garment_obj,
                        quantity=quantity_decimal,
                        uom=unit,
                        remarks=remark
                    )
                    processed_existing_ids.add(new_item.id)
            else:
                # No ID posted means a new row; create the item
                new_item = PurchaseIndentItem.objects.create(
                    indent=indent,
                    garment=garment_obj,
                    quantity=quantity_decimal,
                    uom=unit,
                    remarks=remark
                )
                processed_existing_ids.add(new_item.id)

        # Delete any items that were removed in the edit form
        indent.items.exclude(id__in=processed_existing_ids).delete()

        messages.success(request, f"Purchase Indent {indent.indent_no} updated successfully!")
        return redirect('indent')

    context = {
        'indent': indent,
        'garment': garment,
    }
    return render(request, 'fabzen_app/Purchase/PurchaseIndent/edit_indentt.html', context)


# ----------------------------------- END Indent ---------------------




# def convert_to_po(request, pk):
#     indent = get_object_or_404(PurchaseIndent, pk=pk)
#     indent_items = PurchaseIndentItem.objects.filter(indent=indent)
    
   
#     garments = Garment.objects.all()

#     if request.method == "POST":
        
#         po_no = request.POST.get('po_no')
#         supplier_id = request.POST.get('supplier')
#         payment_terms = request.POST.get('payment_terms')
#         indent_id = request.POST.get('indent_id')  # optional hidden field
#         # optional hidden field
#         terms = request.POST.get('terms')  # optional hidden field
        
        
# # 
#         po = PurchaseOrder.objects.create(
#             indent_id=indent_id,
#             po_no=po_no,
#             po_date=request.POST.get('po_date'),
#             delivery_date=request.POST.get('delivery_date'),
#             payment_terms=payment_terms,
#             supplier=supplier_id,
#             termscondition=terms,
#         )


#         # get lists safely
#         item_descriptions = request.POST.getlist('item_description[]')
#         descriptions = request.POST.getlist('description[]')
#         colors = request.POST.getlist('color[]')
#         quantities = request.POST.getlist('quantity[]')
#         units = request.POST.getlist('unit[]')
#         rates = request.POST.getlist('price[]')
#         discounts = request.POST.getlist('discount[]')
#         amounts = request.POST.getlist('amount[]')

#         num_rows = len(item_descriptions)
#         for i in range(num_rows):
            
#             try:
#                 garment_id = item_descriptions[i]
#                 if not garment_id:
#                     continue

#                 garment_obj = Garment.objects.filter(id=garment_id).first()
                

#                 # ✅ use safe indexing with fallback values
#                 desc = descriptions[i] if i < len(descriptions) else ""
#                 color = colors[i] if i < len(colors) else ""
#                 qty = Decimal(quantities[i]) if i < len(quantities) and quantities[i] else Decimal(0)
#                 uom = units[i] if i < len(units) else ""
#                 rate = Decimal(rates[i]) if i < len(rates) and rates[i] else Decimal(0)
#                 discount = Decimal(discounts[i]) if i < len(discounts) and discounts[i] else Decimal(0)
#                 amt = Decimal(amounts[i]) if i < len(amounts) and amounts[i] else Decimal(0)

#                 PurchaseOrderItem.objects.create(
#                     po=po,
#                     garment=garment_obj,
#                     description=desc,
#                     color=color,
#                     quantity=qty,
#                     uom=uom,
#                     rate=rate,
#                     discount=discount,
#                     amount=amt,
#                 )

#                 indent_item = PurchaseIndentItem.objects.get(indent=indent, garment=garment_obj)
#                 indent_item.converted_qty += qty
#                 indent_item.save()

#             except Exception as inner_e:
#                 print(f"❌ Skipping row {i} due to error:", inner_e)

#         po.calculate_totals()
#         messages.success(request, f"Purchase Order {po_no} created successfully!")
#         return redirect('purchaseorder')
    


#     context = {
#         'indent': indent,
#         'indent_items': indent_items,
#         'garment': garments,
#     }
#     # return render(request, 'fabzen_app/Purchase/PurchaseOrder/add_purchase_order.html', context)
#     return render(request, 'fabzen_app/Purchase/PurchaseOrder/adding_purchase_ordercopy.html', context)


from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import PurchaseOrder, PurchaseOrderItem, PurchaseIndent, PurchaseIndentItem, Garment
@login_required(login_url='/')
def convert_to_po(request, pk):
    indent = get_object_or_404(PurchaseIndent, pk=pk)
    indent_items = PurchaseIndentItem.objects.filter(indent=indent)
    garments = Garment.objects.all()

    if request.method == "POST":
        po_no = request.POST.get('po_no')
        supplier_id = request.POST.get('supplier')
        payment_terms = request.POST.get('payment_terms')
        indent_id = request.POST.get('indent_id')
        terms = request.POST.get('terms')

        # ✅ Create PO
        po = PurchaseOrder.objects.create(
            indent_id=indent_id,
            po_no=po_no,
            po_date=request.POST.get('po_date'),
            delivery_date=request.POST.get('delivery_date'),
            payment_terms=payment_terms,
            supplier=supplier_id,
            termscondition=terms,
        )

        # ✅ Fetch all lists safely
        indent_item_ids = request.POST.getlist('indent_item_id[]')  # added hidden field
        item_descriptions = request.POST.getlist('item_description[]')
        descriptions = request.POST.getlist('description[]')
        colors = request.POST.getlist('color[]')
        quantities = request.POST.getlist('quantity[]')
        units = request.POST.getlist('unit[]')
        rates = request.POST.getlist('price[]')
        discounts = request.POST.getlist('discount[]')
        amounts = request.POST.getlist('amount[]')

        num_rows = len(item_descriptions)
        for i in range(num_rows):
            try:
                garment_id = item_descriptions[i]
                if not garment_id:
                    continue

                garment_obj = Garment.objects.filter(id=garment_id).first()
                if not garment_obj:
                    continue

                # ✅ Safe values with fallbacks
                desc = descriptions[i] if i < len(descriptions) else ""
                color = colors[i] if i < len(colors) else ""
                qty = Decimal(quantities[i]) if i < len(quantities) and quantities[i] else Decimal(0)
                uom = units[i] if i < len(units) else ""
                rate = Decimal(rates[i]) if i < len(rates) and rates[i] else Decimal(0)
                discount = Decimal(discounts[i]) if i < len(discounts) and discounts[i] else Decimal(0)
                amt = Decimal(amounts[i]) if i < len(amounts) and amounts[i] else Decimal(0)

                # ✅ Create PO Item
                PurchaseOrderItem.objects.create(
                    po=po,
                    garment=garment_obj,
                    description=desc,
                    color=color,
                    quantity=qty,
                    uom=uom,
                    rate=rate,
                    discount=discount,
                    amount=amt,
                )

                # ✅ Update converted qty only if this item was from indent
                indent_item_id = indent_item_ids[i] if i < len(indent_item_ids) else ""
                if indent_item_id:
                    indent_item = PurchaseIndentItem.objects.filter(id=indent_item_id).first()
                    if indent_item:
                        indent_item.converted_qty += qty
                        indent_item.save()

            except Exception as inner_e:
                print(f"❌ Skipping row {i} due to error:", inner_e)

        # ✅ Final total calculation
        po.calculate_totals()
        messages.success(request, f"Purchase Order {po_no} created successfully!")
        return redirect('purchaseorder')

    context = {
        'indent': indent,
        'indent_items': indent_items,
        'garment': garments,
    }
    return render(request, 'fabzen_app/Purchase/PurchaseOrder/adding_purchase_ordercopy.html', context)




# def convert_to_po(request, pk):
#     indent = get_object_or_404(PurchaseIndent, pk=pk)

#     # Agar pehle se converted hai
#     existing_po = PurchaseOrder.objects.filter(indent=indent).first()
#     if existing_po:
#         messages.warning(request, f'This indent is already converted to PO ({existing_po.po_no}).')
#         return redirect('indent')
#         # return JsonResponse({
#         #     'status': 'error',
#         #     'message': f'This indent is already converted to PO ({existing_po.po_no}).'
#         # })

#     # Generate next PO number
#     last_po = PurchaseOrder.objects.order_by('-id').first()
#     next_no = 1
#     if last_po and last_po.po_no.startswith('PO-'):
#         try:
#             next_no = int(last_po.po_no.split('-')[-1]) + 1
#         except ValueError:
#             pass
#     po_no = f"PO-{next_no:04d}"

#     # Create new PO
#     po = PurchaseOrder.objects.create(
#         po_no=po_no,
#         po_date=date.today(),
#         indent=indent,
#         converted_status='Yes',
#         status="Open"
#     )

#     # Copy all indent items to PO items
#     indent_items = PurchaseIndentItem.objects.filter(indent=indent)
#     for item in indent_items:
#         PurchaseOrderItem.objects.create(
#             po=po,
#             garment=item.garment,
#             quantity=item.quantity,
#             uom=item.uom,
#             # remarks=item.remarks
#         )
#     po.calculate_totals()
#     # Update indent status
#     indent.status = "Close"
#     indent.save()

   
#     return redirect('add_purchase_order')
    

# --------------------------------------- Purchase Order ------------------     

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import PurchaseOrder, PurchaseOrderItem, Garment
from datetime import date
from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import date
from .models import PurchaseOrder, PurchaseOrderItem, Garment

from decimal import Decimal

@login_required(login_url='/')
def add_purchase_order(request):
    garment = Garment.objects.all()

    if request.method == "POST":
        try:
            po_no = request.POST.get('po_no')
            po_date = request.POST.get('po_date') or date.today()
            delivery_date = request.POST.get('delivery_date')
            payment_terms = request.POST.get('payment_terms')
            supplier_id = request.POST.get('supplier')
            terms = request.POST.get('terms')

            # ✅ convert supplier id to object (important)
            # supplier_obj = Supplier.objects.filter(id=supplier_id).first() if supplier_id else None

            # ✅ Check if PO number already exists
            if PurchaseOrder.objects.filter(po_no=po_no).exists():
                messages.warning(request, f"Purchase Order number '{po_no}' already exists.")
                return redirect('add_purchase_order')  # or re-render same form if you prefer



            po = PurchaseOrder.objects.create(
                po_no=po_no,
                po_date=po_date,
                delivery_date=delivery_date,
                payment_terms=payment_terms,
                supplier=supplier_id,
                termscondition=terms,
            )

            # get lists safely
            item_descriptions = request.POST.getlist('item_description[]')
            descriptions = request.POST.getlist('description[]')
            colors = request.POST.getlist('color[]')
            quantities = request.POST.getlist('quantity[]')
            units = request.POST.getlist('unit[]')
            rates = request.POST.getlist('price[]')
            discounts = request.POST.getlist('discount[]')
            amounts = request.POST.getlist('amount[]')

            num_rows = len(item_descriptions)

            for i in range(num_rows):
                try:
                    garment_id = item_descriptions[i]
                    if not garment_id:
                        continue

                    garment_obj = Garment.objects.filter(id=garment_id).first()

                    # ✅ use safe indexing with fallback values
                    desc = descriptions[i] if i < len(descriptions) else ""
                    color = colors[i] if i < len(colors) else ""
                    qty = Decimal(quantities[i]) if i < len(quantities) and quantities[i] else Decimal(0)
                    uom = units[i] if i < len(units) else ""
                    rate = Decimal(rates[i]) if i < len(rates) and rates[i] else Decimal(0)
                    discount = Decimal(discounts[i]) if i < len(discounts) and discounts[i] else Decimal(0)
                    amt = Decimal(amounts[i]) if i < len(amounts) and amounts[i] else Decimal(0)

                    PurchaseOrderItem.objects.create(
                        po=po,
                        garment=garment_obj,
                        description=desc,
                        color=color,
                        quantity=qty,
                        uom=uom,
                        rate=rate,
                        discount=discount,
                        amount=amt,
                    )

                except Exception as inner_e:
                    print(f"❌ Skipping row {i} due to error:", inner_e)

            po.calculate_totals()

            messages.success(request, f"Purchase Order {po_no} created successfully!")
            return redirect('purchaseorder')

        except Exception as e:
            print("Error creating PO:", e)
            messages.error(request, f"Error creating PO: {e}")

    return render(request, 'fabzen_app/Purchase/PurchaseOrder/adding_purchase_ordercopy.html', {'garment': garment})


@login_required(login_url='/')
def PurchaseOrderListView(request):
    garment = Garment.objects.all()
    pending = PurchaseIndent.objects.filter(status='Pending').count()
    approved = PurchaseIndent.objects.filter(status='Approved').count()
    rejected = PurchaseIndent.objects.filter(status='Rejected').count()
    converted = PurchaseIndent.objects.filter(status='Close').count()

    if request.method == "POST":
        # Get main fields
        indent_date = request.POST.get('indent_date')
        department = request.POST.get('department')
        priority = request.POST.get('priority')
        requested_by = request.POST.get('requested_by')
        required_date = request.POST.get('required_date')
        remarks = request.POST.get('purpose')

        # ✅ Generate unique indent number
        last_indent = PurchaseIndent.objects.order_by('-id').first()
        if last_indent:
            new_number = int(last_indent.indent_no.split('-')[-1]) + 1
        else:
            new_number = 1
        indent_no = f"PI-{new_number:04d}"

        # ✅ Create main PurchaseIndent record
        indent = PurchaseIndent.objects.create(
            indent_no=indent_no,
            department=department,
            indent_date=indent_date,
            required_date=required_date,
            priority=priority,
            requested_by=requested_by,
            remarks=remarks,
            status='Pending'
        )

        # ✅ Get list fields
        item_descriptions = request.POST.getlist('item_description[]')
        quantities = request.POST.getlist('quantity[]')
        units = request.POST.getlist('unit[]')
        item_remarks = request.POST.getlist('remarks[]')

        # ✅ Loop through all items
        for i in range(len(item_descriptions)):
            garment_id = item_descriptions[i]
            quantity = quantities[i]
            unit = units[i]
            remark = item_remarks[i]

            if garment_id and quantity:
                try:
                    garment_obj = Garment.objects.get(id=garment_id)
                except Garment.DoesNotExist:
                    continue

                PurchaseIndentItem.objects.create(
                    indent=indent,
                    garment=garment_obj,
                    quantity=quantity,
                    uom=unit,
                    remarks=remark
                )

        messages.success(request, f"Purchase Indent {indent.indent_no} created successfully!")
        return redirect('indent')

    context = {
        'garment': garment,
        'pending' : pending,
        'approved' : approved,
        'rejected' : rejected,
        'converted' : converted,
        
    }
    return render(request, 'fabzen_app/Purchase/PurchaseOrder/purchaseorder.html', context)





def purchaseorder_list(request):
    
    search_query = request.GET.get('search', '').strip()
    
    type = request.GET.get('type', '').strip()
    purchase_qs = PurchaseOrder.objects.all().order_by('-id')
    garment = Garment.objects.all()
    # ledger_group = LedgerGroup.objects.all().order_by('-id')

    if search_query:
        purchase_qs = purchase_qs.filter(po_no__icontains=search_query)
        
    
    # if type:
    #     purchase_qs = purchase_qs.filter(status__iexact=type)

    # --- Pagination logic ---
    page_number = request.GET.get('page', 1)  # Get ?page= from URL (default: 1)
    paginator = Paginator(purchase_qs, 10)     # Show 10 ledgers per page
  
    try:
        orders = paginator.page(page_number)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    context = {
        'orders': orders,
        'paginator': paginator,
        'is_paginated': True,  # Used by your template
        # 'ledger_group':ledger_group
        'garment':garment
    }

    return render(request, 'fabzen_app/Purchase/PurchaseOrder/partials/order_list.html', context)

    #     return redirect('indent')


def get_garment_description(request, garment_id):
    print("oooooooooooooooooooooooooooooooo",garment_id)
    garment = Garment.objects.filter(id=garment_id).first()
    print("garmentssssssssssssss",garment)
    if garment:
        return HttpResponse(garment.description)
    return HttpResponse("")


# def edit_purchase_order(request, pk):

#     purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
#     garment = Garment.objects.all()
#     context = {
#         'purchase_order': purchase_order,
#         'garment': garment,
#     }

#     return render(request, 'fabzen_app/Purchase/PurchaseOrder/edit_purchase_order.html', context)

from decimal import Decimal
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from datetime import date
@login_required(login_url='/')
def edit_purchase_order(request, pk):
    purchase_order = get_object_or_404(PurchaseOrder, pk=pk)
    garment = Garment.objects.all()

    if request.method == "POST":
        try:
            # 🧾 Basic fields
            po_no = request.POST.get('po_no')
            po_date = request.POST.get('po_date') or date.today()
            delivery_date = request.POST.get('delivery_date')
            payment_terms = request.POST.get('payment_terms')
            supplier = request.POST.get('supplier')
            terms = request.POST.get('terms')

            # ✅ Update main PO record
            purchase_order.po_no = po_no
            purchase_order.po_date = po_date
            purchase_order.delivery_date = delivery_date
            purchase_order.payment_terms = payment_terms
            purchase_order.supplier = supplier
            purchase_order.termscondition = terms
            purchase_order.save()

            # ✅ Delete old items to replace them cleanly
            purchase_order.items.all().delete()

            # 🧾 Get updated item fields
            item_descriptions = request.POST.getlist('item_description[]')
            descriptions = request.POST.getlist('description[]')
            colors = request.POST.getlist('color[]')
            quantities = request.POST.getlist('quantity[]')
            units = request.POST.getlist('unit[]')
            rates = request.POST.getlist('price[]')
            discounts = request.POST.getlist('discount[]')
            amounts = request.POST.getlist('amount[]')

            num_rows = len(item_descriptions)

            for i in range(num_rows):
                try:
                    garment_id = item_descriptions[i]
                    if not garment_id:
                        continue

                    garment_obj = Garment.objects.filter(id=garment_id).first()

                    # ✅ Safe conversion & indexing
                    desc = descriptions[i] if i < len(descriptions) else ""
                    color = colors[i] if i < len(colors) else ""
                    qty = Decimal(quantities[i]) if i < len(quantities) and quantities[i] else Decimal(0)
                    uom = units[i] if i < len(units) else ""
                    rate = Decimal(rates[i]) if i < len(rates) and rates[i] else Decimal(0)
                    discount = Decimal(discounts[i]) if i < len(discounts) and discounts[i] else Decimal(0)
                    amt = Decimal(amounts[i]) if i < len(amounts) and amounts[i] else Decimal(0)

                    PurchaseOrderItem.objects.create(
                        po=purchase_order,
                        garment=garment_obj,
                        description=desc,
                        color=color,
                        quantity=qty,
                        uom=uom,
                        rate=rate,
                        discount=discount,
                        amount=amt,
                    )
                except Exception as inner_e:
                    print(f"❌ Error updating item {i}: {inner_e}")

            # 🔄 Recalculate totals
            purchase_order.calculate_totals()

            messages.success(request, f"Purchase Order {po_no} updated successfully!")
            return redirect('purchaseorder')

        except Exception as e:
            print("❌ Error updating PO:", e)
            messages.error(request, f"Error updating PO: {e}")

    context = {
        'purchase_order': purchase_order,
        'garment': garment,
    }
    return render(request, 'fabzen_app/Purchase/PurchaseOrder/edit_purchase_ordercopy.html', context)

# --------------------------------------- END Purchase Order ------------------



# --------------------------------------- Receipt Note ------------------

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from datetime import date
from decimal import Decimal
from .models import PurchaseOrder, GoodsReceiveNote, GoodsReceiveNoteItem


def convert_po_to_grn(request, pk):
    """
    Convert Purchase Order to Goods Receive Note (GRN)
    """
    po = get_object_or_404(PurchaseOrder, pk=pk)

    try:
        # 🧾 Auto-generate GRN number (you can change logic as needed)
        latest_grn = GoodsReceiveNote.objects.order_by('-id').first()
        next_no = 1 if not latest_grn else int(latest_grn.grn_no.split('-')[-1]) + 1
        grn_no = f"GRN-{next_no:04d}"

        # 🧾 Create GRN header
        grn = GoodsReceiveNote.objects.create(
            grn_no=grn_no,
            grn_date=date.today(),
            purchase_order=po,
            supplier=po.supplier,
            status='Pending',
        )

        # 🧾 Copy PO items to GRN items
        for item in po.items.all():
            GoodsReceiveNoteItem.objects.create(
                grn=grn,
                garment=item.garment,
                quantity=item.quantity,
                uom=item.uom,
                rate=item.rate,
                amount=item.amount,
                remarks=item.description or '',
            )

        # 🔄 Recalculate totals
        grn.calculate_totals()

        # Optionally update PO status
        po.status = 'Close'  # or 'Completed' if everything received
        po.save()

        messages.success(request, f"Purchase Order {po.po_no} converted to GRN {grn.grn_no} successfully!")
        return redirect('receiptnote')  # change name to your GRN list view

    except Exception as e:
        print("Error converting PO to GRN:", e)
        messages.error(request, f"Error converting PO to GRN: {e}")
        return redirect('purchaseorder')



def ReceiptNoteListView(request):
    garment = Garment.objects.all()
    pending = PurchaseIndent.objects.filter(status='Pending').count()
    approved = PurchaseIndent.objects.filter(status='Approved').count()
    rejected = PurchaseIndent.objects.filter(status='Rejected').count()
    converted = PurchaseIndent.objects.filter(status='Close').count()

    context = {
        'garment': garment,
        'pending' : pending,
        'approved' : approved,
        'rejected' : rejected,
        'converted' : converted,
        
    }
    return render(request, 'fabzen_app/Purchase/ReceiptNote/receiptnote.html', context)





def receiptnote_list(request):
    
    search_query = request.GET.get('search', '').strip()
    
    type = request.GET.get('type', '').strip()
    purchase_qs = GoodsReceiveNote.objects.all().order_by('-id')
    garment = Garment.objects.all()
    # ledger_group = LedgerGroup.objects.all().order_by('-id')

    if search_query:
        purchase_qs = purchase_qs.filter(grn_no__icontains=search_query)
        
    
    # if type:
    #     purchase_qs = purchase_qs.filter(status__iexact=type)

    # --- Pagination logic ---
    page_number = request.GET.get('page', 1)  # Get ?page= from URL (default: 1)
    paginator = Paginator(purchase_qs, 10)     # Show 10 ledgers per page
  
    try:
        orders = paginator.page(page_number)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    context = {
        'orders': orders,
        'paginator': paginator,
        'is_paginated': True,  # Used by your template
        # 'ledger_group':ledger_group
        'garment':garment
    }

    return render(request, 'fabzen_app/Purchase/ReceiptNote/partials/grn_list.html', context)

    #     return redirect('indent')



def add_receipt_note(request):
    garment = Garment.objects.all()

    if request.method == "POST":
        try:
            po_no = request.POST.get('po_no')
            po_date = request.POST.get('po_date') or date.today()
            delivery_date = request.POST.get('delivery_date')
            payment_terms = request.POST.get('payment_terms')
            supplier_id = request.POST.get('supplier')
            terms = request.POST.get('terms')

            # ✅ convert supplier id to object (important)
            # supplier_obj = Supplier.objects.filter(id=supplier_id).first() if supplier_id else None

            po = GoodsReceiveNote.objects.create(
                grn_no=po_no,
                grn_date=po_date,
                # delivery_date=delivery_date,
                payment_terms=payment_terms,
                supplier=supplier_id,
                termscondition=terms,
            )

            # get lists safely
            item_descriptions = request.POST.getlist('item_description[]')
            descriptions = request.POST.getlist('description[]')
            colors = request.POST.getlist('color[]')
            quantities = request.POST.getlist('quantity[]')
            units = request.POST.getlist('unit[]')
            rates = request.POST.getlist('price[]')
            discounts = request.POST.getlist('discount[]')
            amounts = request.POST.getlist('amount[]')

            num_rows = len(item_descriptions)
            
            print(f"Processing {num_rows} rows of items")

            for i in range(num_rows):
                try:
                    garment_id = item_descriptions[i]
                    if not garment_id:
                        print(f"Skipping row {i}: Empty garment_id")
                        continue

                    garment_obj = Garment.objects.filter(id=garment_id).first()
                    if not garment_obj:
                        print(f"Skipping row {i}: Garment with ID {garment_id} not found")
                        continue

                    # ✅ use safe indexing with fallback values
                    desc = descriptions[i] if i < len(descriptions) else ""
                    color = colors[i] if i < len(colors) else ""
                    qty = Decimal(quantities[i]) if i < len(quantities) and quantities[i] else Decimal(0)
                    uom = units[i] if i < len(units) else ""
                    rate = Decimal(rates[i]) if i < len(rates) and rates[i] else Decimal(0)
                    discount = Decimal(discounts[i]) if i < len(discounts) and discounts[i] else Decimal(0)
                    amt = Decimal(amounts[i]) if i < len(amounts) and amounts[i] else Decimal(0)
                    
                    # Calculate amount if it's not provided
                    if amt == Decimal(0) and qty > Decimal(0) and rate > Decimal(0):
                        amt = qty * rate
                        if discount > Decimal(0):
                            amt = amt - (amt * discount / Decimal(100))
                    
                    print(f"Creating item: garment={garment_obj.id}, qty={qty}, rate={rate}, amt={amt}")
                    
                    item = GoodsReceiveNoteItem(
                        grn=po,
                        garment=garment_obj,
                        description=desc,
                        color=color,
                        quantity=qty,
                        uom=uom,
                        rate=rate,
                        discount=discount,
                        amount=amt,
                    )
                    item.save()

                    print(f"Item created successfully with ID: {item.id}")

                except Exception as inner_e:
                    print(f"❌ Skipping row {i} due to error:", inner_e)
                    import traceback
                    traceback.print_exc()

            po.calculate_totals()

            messages.success(request, f"Receipt Note {po_no} created successfully!")
            return redirect('receiptnote')

        except Exception as e:
            print("Error creating Receipt Note:", e)
            import traceback
            traceback.print_exc()
            messages.error(request, f"Error creating Receipt Note: {e}")

    return render(request, 'fabzen_app/Purchase/ReceiptNote/add_grn_note.html', {'garment': garment})



def edit_receipt_note(request, pk):
    receipt_note = get_object_or_404(GoodsReceiveNote, pk=pk)
    garment = Garment.objects.all()

    if request.method == "POST":
        try:
            # 🧾 Basic fields
            po_no = request.POST.get('GRN_no')
            po_date = request.POST.get('GRN_date') or date.today()
            delivery_date = request.POST.get('delivery_date')
            payment_terms = request.POST.get('payment_terms')
            supplier = request.POST.get('supplier')
            terms = request.POST.get('terms')

            # ✅ Update main PO record
            receipt_note.po_no = po_no
            receipt_note.po_date = po_date
            receipt_note.delivery_date = delivery_date
            receipt_note.payment_terms = payment_terms
            receipt_note.supplier = supplier
            receipt_note.termscondition = terms
            receipt_note.save()

            # ✅ Delete old items to replace them cleanly
            receipt_note.items.all().delete()

            # 🧾 Get updated item fields
            item_descriptions = request.POST.getlist('item_description[]')
            descriptions = request.POST.getlist('description[]')
            colors = request.POST.getlist('color[]')
            quantities = request.POST.getlist('quantity[]')
            units = request.POST.getlist('unit[]')
            rates = request.POST.getlist('price[]')
            discounts = request.POST.getlist('discount[]')
            amounts = request.POST.getlist('amount[]')

            num_rows = len(item_descriptions)

            for i in range(num_rows):
                try:
                    garment_id = item_descriptions[i]
                    if not garment_id:
                        continue

                    garment_obj = Garment.objects.filter(id=garment_id).first()

                    # ✅ Safe conversion & indexing
                    desc = descriptions[i] if i < len(descriptions) else ""
                    color = colors[i] if i < len(colors) else ""
                    qty = Decimal(quantities[i]) if i < len(quantities) and quantities[i] else Decimal(0)
                    uom = units[i] if i < len(units) else ""
                    rate = Decimal(rates[i]) if i < len(rates) and rates[i] else Decimal(0)
                    discount = Decimal(discounts[i]) if i < len(discounts) and discounts[i] else Decimal(0)
                    amt = Decimal(amounts[i]) if i < len(amounts) and amounts[i] else Decimal(0)

                    GoodsReceiveNoteItem.objects.create(
                        grn=receipt_note,
                        garment=garment_obj,
                        description=desc,
                        color=color,
                        quantity=qty,
                        uom=uom,
                        rate=rate,
                        discount=discount,
                        amount=amt,
                    )
                except Exception as inner_e:
                    print(f"❌ Error updating item {i}: {inner_e}")

            # 🔄 Recalculate totals
            receipt_note.calculate_totals()

            messages.success(request, f"Receipt Note {po_no} updated successfully!")
            return redirect('receiptnote')

        except Exception as e:
            print("❌ Error updating PO:", e)
            messages.error(request, f"Error updating PO: {e}")

    context = {
        'receipt_note': receipt_note,
        'garment': garment,
    }
    return render(request, 'fabzen_app/Purchase/ReceiptNote/edit_grn.html', context)

# --------------------------------------- END Receipt Note ------------------




# --------------------------------------- Grey Purchase ------------------



def convert_receipt_to_greypurchase(request, pk):
    """
    Convert GRN Order to Grey Purchase
    """
    po = get_object_or_404(GoodsReceiveNote, pk=pk)

    try:
        # 🧾 Auto-generate GRN number (you can change logic as needed)
        latest_grn = GreyPurchase.objects.order_by('-id').first()
        next_no = 1 if not latest_grn else int(latest_grn.gp_no.split('-')[-1]) + 1
        grn_no = f"BATCH-2025-{next_no:04d}"

        # 🧾 Create GRN header
        grn = GreyPurchase.objects.create(
            gp_no=grn_no,
            gp_date=date.today(),
            grn=po,
            supplier=po.supplier,
            status='Pending',
        )

        # 🧾 Copy PO items to GRN items
        for item in po.items.all():
            GreyPurchaseItem.objects.create(
                gp=grn,
                garment=item.garment,
                quantity=item.quantity,
                uom=item.uom,
                rate=item.rate,
                amount=item.amount,
                remarks=item.description or '',
            )

        # 🔄 Recalculate totals
        grn.calculate_totals()

        # Optionally update PO status
        po.status = 'Close'  # or 'Completed' if everything received
        po.save()

        messages.success(request, f"GRN {po.grn_no} converted to Grey Purchase {grn.gp_no} successfully!")

        return redirect('receiptnote')  # change name to your GRN list view

    except Exception as e:
        print("Error converting GRN to Grey Purchase:", e)
        messages.error(request, f"Error converting GRN to Grey Purchase: {e}")
        return redirect('receiptnote')


def GreyPurchaseListView(request):
    garment = Garment.objects.all()
    pending = PurchaseIndent.objects.filter(status='Pending').count()
    approved = PurchaseIndent.objects.filter(status='Approved').count()
    rejected = PurchaseIndent.objects.filter(status='Rejected').count()
    converted = PurchaseIndent.objects.filter(status='Close').count()

    context = {
        'garment': garment,
        'pending' : pending,
        'approved' : approved,
        'rejected' : rejected,
        'converted' : converted,
        
    }
    return render(request, 'fabzen_app/Purchase/GreyPurchase/greypurchase.html', context)



def grey_purchase_list(request):
    
    search_query = request.GET.get('search', '').strip()
    
    type = request.GET.get('type', '').strip()
    purchase_qs = GreyPurchase.objects.all().order_by('-id')
    garment = Garment.objects.all()
    # ledger_group = LedgerGroup.objects.all().order_by('-id')

    if search_query:
        purchase_qs = purchase_qs.filter(gp_no__icontains=search_query)
        
    
    # if type:
    #     purchase_qs = purchase_qs.filter(status__iexact=type)

    # --- Pagination logic ---
    page_number = request.GET.get('page', 1)  # Get ?page= from URL (default: 1)
    paginator = Paginator(purchase_qs, 10)     # Show 10 ledgers per page
  
    try:
        orders = paginator.page(page_number)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    context = {
        'orders': orders,
        'paginator': paginator,
        'is_paginated': True,  # Used by your template
        # 'ledger_group':ledger_group
        'garment':garment
    }

    return render(request, 'fabzen_app/Purchase/GreyPurchase/partials/greypurchase_list.html', context)

    #     return redirect('indent')


from decimal import Decimal
from datetime import date
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Garment, GreyPurchase, GreyPurchaseItem


def add_grey_purchase(request):
    garments = Garment.objects.all()

    if request.method == "POST":
        try:
            # ---------- HEADER DATA ----------
            gp_no = request.POST.get('gp_no')
            gp_date = request.POST.get('gp_date') or date.today()
            delivery_date = request.POST.get('delivery_date')
            payment_terms = request.POST.get('payment_terms')
            supplier = request.POST.get('supplier')
            terms = request.POST.get('terms')

            # ✅ Auto-generate number if not entered
            if not gp_no:
                latest_gp = GreyPurchase.objects.order_by('-id').first()
                next_no = 1 if not latest_gp else int(latest_gp.gp_no.split('-')[-1]) + 1
                gp_no = f"BATCH-2025-{next_no:04d}"

            # ---------- CREATE HEADER ----------
            gp = GreyPurchase.objects.create(
                gp_no=gp_no,
                gp_date=gp_date,
                delivery_date=delivery_date if delivery_date else None,
                payment_terms=payment_terms,
                supplier=supplier,
                termscondition=terms,
                status="Open"
            )

            # ---------- ITEM LISTS ----------
            item_descriptions = request.POST.getlist('item_description[]')
            descriptions = request.POST.getlist('description[]')
            colors = request.POST.getlist('color[]')
            quantities = request.POST.getlist('quantity[]')
            units = request.POST.getlist('unit[]')
            rates = request.POST.getlist('price[]')
            discounts = request.POST.getlist('discount[]')
            amounts = request.POST.getlist('amount[]')

            num_rows = len(item_descriptions)
            print(f"Processing {num_rows} Grey Purchase Items")

            # ---------- LOOP THROUGH ITEMS ----------
            for i in range(num_rows):
                try:
                    garment_id = item_descriptions[i]
                    if not garment_id:
                        print(f"Skipping row {i}: Empty garment_id")
                        continue

                    garment_obj = Garment.objects.filter(id=garment_id).first()
                    if not garment_obj:
                        print(f"Skipping row {i}: Garment with ID {garment_id} not found")
                        continue

                    desc = descriptions[i] if i < len(descriptions) else ""
                    color = colors[i] if i < len(colors) else ""
                    qty = Decimal(quantities[i]) if i < len(quantities) and quantities[i] else Decimal(0)
                    uom = units[i] if i < len(units) else ""
                    rate = Decimal(rates[i]) if i < len(rates) and rates[i] else Decimal(0)
                    discount = Decimal(discounts[i]) if i < len(discounts) and discounts[i] else Decimal(0)
                    amt = Decimal(amounts[i]) if i < len(amounts) and amounts[i] else Decimal(0)

                    # Auto calculate amount if not given
                    if amt == Decimal(0) and qty > Decimal(0) and rate > Decimal(0):
                        amt = qty * rate
                        if discount > Decimal(0):
                            amt -= (amt * discount / Decimal(100))

                    print(f"Creating GreyPurchaseItem: garment={garment_obj.id}, qty={qty}, rate={rate}, amt={amt}")

                    item = GreyPurchaseItem(
                        gp=gp,
                        garment=garment_obj,
                        description=desc,
                        color=color,
                        quantity=qty,
                        uom=uom,
                        rate=rate,
                        discount=discount,
                        amount=amt,
                    )
                    item.save()

                    print(f"Item created successfully with ID: {item.id}")

                except Exception as inner_e:
                    print(f"❌ Skipping row {i} due to error:", inner_e)
                    import traceback
                    traceback.print_exc()

            # ---------- UPDATE TOTALS ----------
            gp.calculate_totals()

            messages.success(request, f"Grey Purchase {gp.gp_no} created successfully!")
            return redirect('greypurchase')  # 🔁 change this to your correct URL name

        except Exception as e:
            print("Error creating Grey Purchase:", e)
            import traceback
            traceback.print_exc()
            messages.error(request, f"Error creating Grey Purchase: {e}")

    return render(request, 'fabzen_app/Purchase/GreyPurchase/add_grey_purchase.html', {'garments': garments})




# def edit_grey_purchase(request, pk):
#     grey_purchase = get_object_or_404(GreyPurchase, pk=pk)
#     garments = Garment.objects.all()

#     if request.method == "POST":
#         try:
#             # 🧾 Basic fields
#             po_no = request.POST.get('GRN_no')
#             po_date = request.POST.get('GRN_date') or date.today()
#             delivery_date = request.POST.get('delivery_date')
#             payment_terms = request.POST.get('payment_terms')
#             supplier = request.POST.get('supplier')
#             terms = request.POST.get('terms')

#             # ✅ Update main PO record
#             receipt_note.po_no = po_no
#             receipt_note.po_date = po_date
#             receipt_note.delivery_date = delivery_date
#             receipt_note.payment_terms = payment_terms
#             receipt_note.supplier = supplier
#             receipt_note.termscondition = terms
#             receipt_note.save()

#             # ✅ Delete old items to replace them cleanly
#             receipt_note.items.all().delete()

#             # 🧾 Get updated item fields
#             item_descriptions = request.POST.getlist('item_description[]')
#             descriptions = request.POST.getlist('description[]')
#             colors = request.POST.getlist('color[]')
#             quantities = request.POST.getlist('quantity[]')
#             units = request.POST.getlist('unit[]')
#             rates = request.POST.getlist('price[]')
#             discounts = request.POST.getlist('discount[]')
#             amounts = request.POST.getlist('amount[]')

#             num_rows = len(item_descriptions)

#             for i in range(num_rows):
#                 try:
#                     garment_id = item_descriptions[i]
#                     if not garment_id:
#                         continue

#                     garment_obj = Garment.objects.filter(id=garment_id).first()

#                     # ✅ Safe conversion & indexing
#                     desc = descriptions[i] if i < len(descriptions) else ""
#                     color = colors[i] if i < len(colors) else ""
#                     qty = Decimal(quantities[i]) if i < len(quantities) and quantities[i] else Decimal(0)
#                     uom = units[i] if i < len(units) else ""
#                     rate = Decimal(rates[i]) if i < len(rates) and rates[i] else Decimal(0)
#                     discount = Decimal(discounts[i]) if i < len(discounts) and discounts[i] else Decimal(0)
#                     amt = Decimal(amounts[i]) if i < len(amounts) and amounts[i] else Decimal(0)

#                     GoodsReceiveNoteItem.objects.create(
#                         grn=receipt_note,
#                         garment=garment_obj,
#                         description=desc,
#                         color=color,
#                         quantity=qty,
#                         uom=uom,
#                         rate=rate,
#                         discount=discount,
#                         amount=amt,
#                     )
#                 except Exception as inner_e:
#                     print(f"❌ Error updating item {i}: {inner_e}")

#             # 🔄 Recalculate totals
#             receipt_note.calculate_totals()

#             messages.success(request, f"Receipt Note {po_no} updated successfully!")
#             return redirect('receiptnote')

#         except Exception as e:
#             print("❌ Error updating PO:", e)
#             messages.error(request, f"Error updating PO: {e}")

#     context = {
#         'receipt_note': receipt_note,
#         'garment': garment,
#     }
#     return render(request, 'fabzen_app/Purchase/ReceiptNote/edit_grn.html', context)



from decimal import Decimal
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Garment, GreyPurchase, GreyPurchaseItem


def edit_grey_purchase(request, pk):
    grey_purchase = get_object_or_404(GreyPurchase, pk=pk)
    garments = Garment.objects.all()

    if request.method == "POST":
        try:
            # ---------- UPDATE HEADER ----------
            gp_no = request.POST.get('gp_no')
            gp_date = request.POST.get('gp_date') or date.today()
            # delivery_date = request.POST.get('delivery_date')
            payment_terms = request.POST.get('payment_terms')
            supplier = request.POST.get('supplier')
            terms = request.POST.get('terms')

            # ✅ Update main record
            grey_purchase.gp_no = gp_no
            grey_purchase.gp_date = gp_date
            # grey_purchase.delivery_date = delivery_date if delivery_date else None
            grey_purchase.payment_terms = payment_terms
            grey_purchase.supplier = supplier
            grey_purchase.termscondition = terms
            grey_purchase.save()

            # ---------- DELETE OLD ITEMS ----------
            grey_purchase.items.all().delete()

            # ---------- READ UPDATED ITEM LISTS ----------
            item_descriptions = request.POST.getlist('item_description[]')
            descriptions = request.POST.getlist('description[]')
            colors = request.POST.getlist('color[]')
            quantities = request.POST.getlist('quantity[]')
            units = request.POST.getlist('unit[]')
            rates = request.POST.getlist('price[]')
            discounts = request.POST.getlist('discount[]')
            amounts = request.POST.getlist('amount[]')

            num_rows = len(item_descriptions)
            print(f"Updating {num_rows} Grey Purchase Items for {grey_purchase.gp_no}")

            # ---------- LOOP AND ADD NEW ITEMS ----------
            for i in range(num_rows):
                try:
                    garment_id = item_descriptions[i]
                    if not garment_id:
                        continue

                    garment_obj = Garment.objects.filter(id=garment_id).first()
                    if not garment_obj:
                        continue

                    desc = descriptions[i] if i < len(descriptions) else ""
                    color = colors[i] if i < len(colors) else ""
                    qty = Decimal(quantities[i]) if i < len(quantities) and quantities[i] else Decimal(0)
                    uom = units[i] if i < len(units) else ""
                    rate = Decimal(rates[i]) if i < len(rates) and rates[i] else Decimal(0)
                    discount = Decimal(discounts[i]) if i < len(discounts) and discounts[i] else Decimal(0)
                    amt = Decimal(amounts[i]) if i < len(amounts) and amounts[i] else Decimal(0)

                    # Auto calculate if amount missing
                    if amt == Decimal(0) and qty > 0 and rate > 0:
                        amt = qty * rate
                        if discount > 0:
                            amt -= (amt * discount / Decimal(100))

                    GreyPurchaseItem.objects.create(
                        gp=grey_purchase,
                        garment=garment_obj,
                        description=desc,
                        color=color,
                        quantity=qty,
                        uom=uom,
                        rate=rate,
                        discount=discount,
                        amount=amt,
                    )
                except Exception as inner_e:
                    print(f"❌ Error adding item {i}: {inner_e}")

            # ---------- RECALCULATE TOTALS ----------
            grey_purchase.calculate_totals()

            messages.success(request, f"Grey Purchase {grey_purchase.gp_no} updated successfully!")
            return redirect('greypurchase')  # 🔁 update with your correct URL name

        except Exception as e:
            print("❌ Error updating Grey Purchase:", e)
            import traceback
            traceback.print_exc()
            messages.error(request, f"Error updating Grey Purchase: {e}")
    
    print("grey_purchase items:", grey_purchase)

    context = {
        'grey_purchase': grey_purchase,
        'garments': garments,
    }
    return render(request, 'fabzen_app/Purchase/GreyPurchase/edit_grey_purchase.html', context)

# --------------------------------------- END Grey Purchase ------------------



# ---------------------------------------  Purchase Return ------------------


def convert_greypurchase_to_purchasereturn(request, pk):
    """
    Convert Grey Purchase to Purchase Return
    """
    grey_purchase = get_object_or_404(GreyPurchase, pk=pk)
    print("grey_purchase:", grey_purchase)

    try:
        # 🧾 Auto-generate Purchase Return number
        latest_pr = PurchaseReturn.objects.order_by('-id').first()
        next_no = 1 if not latest_pr else int(latest_pr.pr_no.split('-')[-1]) + 1
        pr_no = f"PR-2025-{next_no:04d}"

        # 🧾 Create Purchase Return header
        purchase_return = PurchaseReturn.objects.create(
            pr_no=pr_no,
            pr_date=date.today(),
            supplier=grey_purchase.supplier,
            greypurchase=grey_purchase,  # if linked greypurchase exists
            status='Draft',
            reason=f"Auto-generated from Grey Purchase {grey_purchase.gp_no}"
        )

        # 🧾 Copy all GreyPurchase items → PurchaseReturn items
        for item in grey_purchase.items.all():
            PurchaseReturnItem.objects.create(
                pr=purchase_return,
                garment=item.garment,
                description=item.description or '',
                quantity=item.quantity,
                uom=item.uom,
                rate=item.rate,
                amount=item.amount,
                reason=f"Return from Grey Purchase {grey_purchase.gp_no}",
            )

        # 🔄 Recalculate totals
        purchase_return.calculate_totals()

        # ✅ Optionally update Grey Purchase status
        grey_purchase.status = 'Close'
        grey_purchase.save()

        messages.success(
            request,
            f"Grey Purchase {grey_purchase.gp_no} successfully converted to Purchase Return {purchase_return.pr_no}!"
        )
        return redirect('greypurchase')  # 🔁 replace with your actual Purchase Return list URL name

    except Exception as e:
        print("❌ Error converting Grey Purchase to Purchase Return:", e)
        import traceback
        traceback.print_exc()
        messages.error(request, f"Error converting Grey Purchase to Purchase Return: {e}")
        return redirect('greypurchase')  # fallback redirect



def PurchaseReturnListView(request):
    garment = Garment.objects.all()
    pending = PurchaseIndent.objects.filter(status='Pending').count()
    approved = PurchaseIndent.objects.filter(status='Approved').count()
    rejected = PurchaseIndent.objects.filter(status='Rejected').count()
    converted = PurchaseIndent.objects.filter(status='Close').count()

    context = {
        'garment': garment,
        'pending' : pending,
        'approved' : approved,
        'rejected' : rejected,
        'converted' : converted,
        
    }
    return render(request, 'fabzen_app/Purchase/PurchaseReturn/purchasereturn.html', context)




def purchasereturn_list(request):
    
    search_query = request.GET.get('search', '').strip()
    
    type = request.GET.get('type', '').strip()
    purchase_qs = PurchaseReturn.objects.all().order_by('-id')
    garment = Garment.objects.all()
    # ledger_group = LedgerGroup.objects.all().order_by('-id')

    if search_query:
        purchase_qs = purchase_qs.filter(pr_no__icontains=search_query)

    
    # if type:
    #     purchase_qs = purchase_qs.filter(status__iexact=type)

    # --- Pagination logic ---
    page_number = request.GET.get('page', 1)  # Get ?page= from URL (default: 1)
    paginator = Paginator(purchase_qs, 10)     # Show 10 ledgers per page
  
    try:
        orders = paginator.page(page_number)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
        orders = paginator.page(paginator.num_pages)
    context = {
        'orders': orders,
        'paginator': paginator,
        'is_paginated': True,  # Used by your template
        # 'ledger_group':ledger_group
        'garment':garment
    }

    return render(request, 'fabzen_app/Purchase/PurchaseReturn/partials/purchasereturn_list.html', context)

    #     return redirect('indent')



from decimal import Decimal
from datetime import date
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Garment, PurchaseReturn, PurchaseReturnItem
from decimal import Decimal
from datetime import date
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Garment, PurchaseReturn, PurchaseReturnItem


def add_purchase_return(request):
    garments = Garment.objects.all()

    if request.method == "POST":
        try:
            # ---------- HEADER DATA ----------
            pr_no = request.POST.get('pr_no')
            pr_date = request.POST.get('pr_date') or date.today()
            supplier = request.POST.get('supplier')
            reason = request.POST.get('reason')

            # ✅ Auto-generate number if not entered
            if not pr_no:
                latest_pr = PurchaseReturn.objects.order_by('-id').first()
                next_no = 1 if not latest_pr else int(latest_pr.pr_no.split('-')[-1]) + 1
                pr_no = f"PR-2025-{next_no:04d}"

            # ---------- CREATE HEADER ----------
            pr = PurchaseReturn.objects.create(
                pr_no=pr_no,
                pr_date=pr_date,
                supplier=supplier,
                reason=reason or '',
                status="Draft"
            )

            # ---------- ITEM LISTS ----------
            item_descriptions = request.POST.getlist('item_description[]')
            descriptions = request.POST.getlist('description[]')
            quantities = request.POST.getlist('quantity[]')
            units = request.POST.getlist('unit[]')
            rates = request.POST.getlist('price[]')
            amounts = request.POST.getlist('amount[]')
            reasons = request.POST.getlist('item_reason[]')

            num_rows = len(item_descriptions)
            print(f"Processing {num_rows} Purchase Return Items")

            # ---------- LOOP THROUGH ITEMS ----------
            for i in range(num_rows):
                try:
                    garment_id = item_descriptions[i]
                    if not garment_id:
                        print(f"Skipping row {i}: Empty garment_id")
                        continue

                    garment_obj = Garment.objects.filter(id=garment_id).first()
                    if not garment_obj:
                        print(f"Skipping row {i}: Garment with ID {garment_id} not found")
                        continue

                    desc = descriptions[i] if i < len(descriptions) else ""
                    qty = Decimal(quantities[i]) if i < len(quantities) and quantities[i] else Decimal(0)
                    uom = units[i] if i < len(units) else ""
                    rate = Decimal(rates[i]) if i < len(rates) and rates[i] else Decimal(0)
                    amt = Decimal(amounts[i]) if i < len(amounts) and amounts[i] else Decimal(0)
                    item_reason = reasons[i] if i < len(reasons) else ""

                    # Auto-calculate amount if not given
                    if amt == Decimal(0) and qty > Decimal(0) and rate > Decimal(0):
                        amt = qty * rate

                    print(f"Creating PurchaseReturnItem: garment={garment_obj.id}, qty={qty}, rate={rate}, amt={amt}")

                    item = PurchaseReturnItem.objects.create(
                        pr=pr,
                        garment=garment_obj,
                        description=desc,
                        quantity=qty,
                        uom=uom,
                        rate=rate,
                        amount=amt,
                        reason=item_reason or reason,
                    )

                    print(f"Item created successfully with ID: {item.id}")

                except Exception as inner_e:
                    print(f"❌ Skipping row {i} due to error:", inner_e)
                    import traceback
                    traceback.print_exc()

            # ---------- UPDATE TOTALS ----------
            pr.calculate_totals()

            messages.success(request, f"Purchase Return {pr.pr_no} created successfully!")
            return redirect('purchasereturn')  # 🔁 change to your actual Purchase Return list URL name

        except Exception as e:
            print("❌ Error creating Purchase Return:", e)
            import traceback
            traceback.print_exc()
            messages.error(request, f"Error creating Purchase Return: {e}")

    return render(request, 'fabzen_app/Purchase/PurchaseReturn/add_purchasereturn.html', {'garments': garments})






# def edit_purchase_return(request, pk):
#     purchase_return = get_object_or_404(PurchaseReturn, pk=pk)
#     garments = Garment.objects.all()

#     if request.method == "POST":
#         try:
#             # ---------- UPDATE HEADER ----------
#             gp_no = request.POST.get('gp_no')
#             gp_date = request.POST.get('gp_date') or date.today()
#             # delivery_date = request.POST.get('delivery_date')
#             payment_terms = request.POST.get('payment_terms')
#             supplier = request.POST.get('supplier')
#             terms = request.POST.get('terms')

#             # ✅ Update main record
#             grey_purchase.gp_no = gp_no
#             grey_purchase.gp_date = gp_date
#             # grey_purchase.delivery_date = delivery_date if delivery_date else None
#             grey_purchase.payment_terms = payment_terms
#             grey_purchase.supplier = supplier
#             grey_purchase.termscondition = terms
#             grey_purchase.save()

#             # ---------- DELETE OLD ITEMS ----------
#             grey_purchase.items.all().delete()

#             # ---------- READ UPDATED ITEM LISTS ----------
#             item_descriptions = request.POST.getlist('item_description[]')
#             descriptions = request.POST.getlist('description[]')
#             colors = request.POST.getlist('color[]')
#             quantities = request.POST.getlist('quantity[]')
#             units = request.POST.getlist('unit[]')
#             rates = request.POST.getlist('price[]')
#             discounts = request.POST.getlist('discount[]')
#             amounts = request.POST.getlist('amount[]')

#             num_rows = len(item_descriptions)
#             print(f"Updating {num_rows} Grey Purchase Items for {grey_purchase.gp_no}")

#             # ---------- LOOP AND ADD NEW ITEMS ----------
#             for i in range(num_rows):
#                 try:
#                     garment_id = item_descriptions[i]
#                     if not garment_id:
#                         continue

#                     garment_obj = Garment.objects.filter(id=garment_id).first()
#                     if not garment_obj:
#                         continue

#                     desc = descriptions[i] if i < len(descriptions) else ""
#                     color = colors[i] if i < len(colors) else ""
#                     qty = Decimal(quantities[i]) if i < len(quantities) and quantities[i] else Decimal(0)
#                     uom = units[i] if i < len(units) else ""
#                     rate = Decimal(rates[i]) if i < len(rates) and rates[i] else Decimal(0)
#                     discount = Decimal(discounts[i]) if i < len(discounts) and discounts[i] else Decimal(0)
#                     amt = Decimal(amounts[i]) if i < len(amounts) and amounts[i] else Decimal(0)

#                     # Auto calculate if amount missing
#                     if amt == Decimal(0) and qty > 0 and rate > 0:
#                         amt = qty * rate
#                         if discount > 0:
#                             amt -= (amt * discount / Decimal(100))

#                     GreyPurchaseItem.objects.create(
#                         gp=grey_purchase,
#                         garment=garment_obj,
#                         description=desc,
#                         color=color,
#                         quantity=qty,
#                         uom=uom,
#                         rate=rate,
#                         discount=discount,
#                         amount=amt,
#                     )
#                 except Exception as inner_e:
#                     print(f"❌ Error adding item {i}: {inner_e}")

#             # ---------- RECALCULATE TOTALS ----------
#             grey_purchase.calculate_totals()

#             messages.success(request, f"Grey Purchase {grey_purchase.gp_no} updated successfully!")
#             return redirect('greypurchase')  # 🔁 update with your correct URL name

#         except Exception as e:
#             print("❌ Error updating Grey Purchase:", e)
#             import traceback
#             traceback.print_exc()
#             messages.error(request, f"Error updating Grey Purchase: {e}")
    
#     print("grey_purchase items:", grey_purchase)

#     context = {
#         'grey_purchase': grey_purchase,
#         'garments': garments,
#     }
#     return render(request, 'fabzen_app/Purchase/PurchaseReturn/edit_purchasereturn.html', context)


from decimal import Decimal
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import PurchaseReturn, PurchaseReturnItem, Garment


# def edit_purchase_return(request, pk):
#     purchase_return = get_object_or_404(PurchaseReturn, pk=pk)
#     garments = Garment.objects.all()

#     if request.method == "POST":
#         print("POST data:", request.POST)
#         try:
#             # ---------- UPDATE HEADER ----------
#             pr_no = request.POST.get('pr_no')
#             pr_date = request.POST.get('pr_date') or date.today()
#             supplier = request.POST.get('supplier')
#             reason = request.POST.get('reason')

#             # ✅ Update main PurchaseReturn record
#             purchase_return.pr_no = pr_no
#             purchase_return.pr_date = pr_date
#             purchase_return.supplier = supplier
#             purchase_return.reason = reason
#             purchase_return.save()

#             # ---------- DELETE OLD ITEMS ----------
#             purchase_return.items.all().delete()

#             # ---------- READ UPDATED ITEM LISTS ----------
#             item_descriptions = request.POST.getlist('item_description[]')
#             descriptions = request.POST.getlist('description[]')
#             quantities = request.POST.getlist('quantity[]')
#             units = request.POST.getlist('unit[]')
#             rates = request.POST.getlist('price[]')
#             amounts = request.POST.getlist('amount[]')
#             reasons = request.POST.getlist('item_reason[]')

#             num_rows = len(item_descriptions)
#             print(f"Updating {num_rows} Purchase Return Items for {purchase_return.pr_no}")

#             # ---------- LOOP AND ADD NEW ITEMS ----------
#             for i in range(num_rows):
#                 try:
#                     garment_id = item_descriptions[i]
#                     if not garment_id:
#                         continue

#                     garment_obj = Garment.objects.filter(id=garment_id).first()
#                     if not garment_obj:
#                         continue

#                     desc = descriptions[i] if i < len(descriptions) else ""
#                     qty = Decimal(quantities[i]) if i < len(quantities) and quantities[i] else Decimal(0)
#                     uom = units[i] if i < len(units) else ""
#                     rate = Decimal(rates[i]) if i < len(rates) and rates[i] else Decimal(0)
#                     amt = Decimal(amounts[i]) if i < len(amounts) and amounts[i] else Decimal(0)
#                     item_reason = reasons[i] if i < len(reasons) else ""

#                     # Auto calculate if amount missing
#                     if amt == Decimal(0) and qty > 0 and rate > 0:
#                         amt = qty * rate

#                     PurchaseReturnItem.objects.create(
#                         pr=purchase_return,
#                         garment=garment_obj,
#                         description=desc,
#                         quantity=qty,
#                         uom=uom,
#                         rate=rate,
#                         amount=amt,
#                         reason=item_reason or reason,
#                     )
#                 except Exception as inner_e:
#                     print(f"❌ Error adding item {i}: {inner_e}")
#                     import traceback
#                     traceback.print_exc()

#             # ---------- RECALCULATE TOTALS ----------
#             purchase_return.calculate_totals()

#             messages.success(request, f"Purchase Return {purchase_return.pr_no} updated successfully!")
#             return redirect('purchasereturn')  # ✅ Update with your actual list view name

#         except Exception as e:
#             print("❌ Error updating Purchase Return:", e)
#             import traceback
#             traceback.print_exc()
#             messages.error(request, f"Error updating Purchase Return: {e}")

#     context = {
#         'purchase_return': purchase_return,
#         'garments': garments,
#     }
#     return render(request, 'fabzen_app/Purchase/PurchaseReturn/edit_purchasereturn.html', context)



from decimal import Decimal
from datetime import date
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import PurchaseReturn, PurchaseReturnItem, Garment


def edit_purchase_return(request, pk):
    purchase_return = get_object_or_404(PurchaseReturn, pk=pk)
    garments = Garment.objects.all()

    if request.method == "POST":
        print("POST data:", request.POST)
        try:
            # ---------- UPDATE HEADER ----------
            pr_no = request.POST.get('pr_no')
            pr_date = request.POST.get('pr_date') or date.today()
            supplier = request.POST.get('supplier')
            reason = request.POST.get('reason')

            purchase_return.pr_no = pr_no
            purchase_return.pr_date = pr_date
            purchase_return.supplier = supplier
            purchase_return.reason = reason
            purchase_return.save()

            # ---------- DELETE OLD ITEMS ----------
            purchase_return.items.all().delete()

            # ---------- READ UPDATED ITEM LISTS ----------
            item_descriptions = request.POST.getlist('item_description[]')
            descriptions = request.POST.getlist('description[]')
            quantities = request.POST.getlist('quantity[]')
            units = request.POST.getlist('unit[]')
            rates = request.POST.getlist('price[]')
            discounts = request.POST.getlist('discount[]')
            amounts = request.POST.getlist('amount[]')
            reasons = request.POST.getlist('item_reason[]')

            num_rows = len(item_descriptions)
            print(f"Updating {num_rows} Purchase Return Items for {purchase_return.pr_no}")

            # ---------- LOOP AND ADD NEW ITEMS ----------
            for i in range(num_rows):
                try:
                    garment_id = item_descriptions[i]
                    if not garment_id:
                        continue

                    garment_obj = Garment.objects.filter(id=garment_id).first()
                    if not garment_obj:
                        continue

                    desc = descriptions[i] if i < len(descriptions) else ""
                    qty = Decimal(quantities[i]) if i < len(quantities) and quantities[i] else Decimal(0)
                    uom = units[i] if i < len(units) else ""
                    rate = Decimal(rates[i]) if i < len(rates) and rates[i] else Decimal(0)
                    discount = Decimal(discounts[i]) if i < len(discounts) and discounts[i] else Decimal(0)
                    amt = Decimal(amounts[i]) if i < len(amounts) and amounts[i] else Decimal(0)
                    item_reason = reasons[i] if i < len(reasons) else ""

                    # Auto calculate amount if missing
                    if amt == Decimal(0) and qty > 0 and rate > 0:
                        amt = qty * rate
                        if discount > 0:
                            amt -= (amt * discount / Decimal(100))

                    PurchaseReturnItem.objects.create(
                        pr=purchase_return,
                        garment=garment_obj,
                        description=desc,
                        quantity=qty,
                        uom=uom,
                        rate=rate,
                        discount=discount,
                        amount=amt,
                        reason=item_reason or reason,
                    )
                except Exception as inner_e:
                    print(f"❌ Error adding item {i}: {inner_e}")
                    import traceback
                    traceback.print_exc()

            # ---------- RECALCULATE TOTALS ----------
            purchase_return.calculate_totals()

            messages.success(request, f"Purchase Return {purchase_return.pr_no} updated successfully!")
            return redirect('purchasereturn')  # Update with your actual list view name

        except Exception as e:
            print("❌ Error updating Purchase Return:", e)
            import traceback
            traceback.print_exc()
            messages.error(request, f"Error updating Purchase Return: {e}")

    context = {
        'purchase_return': purchase_return,
        'garments': garments,
    }
    return render(request, 'fabzen_app/Purchase/PurchaseReturn/edit_purchasereturn.html', context)

# --------------------------------------- END Purchase Return ------------------


def Modern(request):
    return render(request, 'fabzen_app/modern.html')    


from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from decimal import Decimal
from .models import PurchaseIndent, PurchaseIndentItem
from decimal import Decimal
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

def save_preclose_qty(request, pk):
    indent = get_object_or_404(PurchaseIndent, pk=pk)

    if request.method == "POST":
        for item in indent.items.all():
            field_name = f"preclose_qty_{item.id}"
            preclose_qty_value = request.POST.get(field_name)
            print(f"Received preclose_qty for item {item.id}: {preclose_qty_value}")

            if preclose_qty_value:
                try:
                    preclose_qty_value = Decimal(preclose_qty_value)
                except:
                    preclose_qty_value = Decimal('0')

                if preclose_qty_value > 0:
                    # ✅ ensure preclose_qty does not exceed pending
                    if preclose_qty_value > item.pending_qty:
                        messages.warning(
                            request,
                            f"⚠️ Preclose qty for {item.garment.garment_name} exceeds pending qty ({item.pending_qty})."
                        )
                        continue

                    # ✅ update the preclose_qty (add to existing value)
                    item.preclose_qty += preclose_qty_value
                    item.save()  # auto-updates pending_qty as per model.save()

        messages.success(request, "✅ Preclose quantities saved successfully.")
        return redirect('indent')

    return redirect('indent')





# ---------------------------------------------- USER MANAGEMENT --------------------------------
@login_required(login_url='/')
def Users(request):
    # return render(request, 'fabzen_app/UserManagement/user.html')
    return render(request, 'fabzen_app/UserManagement/user.html')


def user_list(request):
    search_query = request.GET.get('search', '').strip()
    company_code = request.session.get('active_company_id')
    print("company codess here", company_code)

    companies = Company.objects.filter(company_code=company_code)

    print("Matching Companies:", companies)

    
    user_qs = Client.objects.filter(
        created_by=request.user,
        company__company_code=company_code
    )
    print("user_qs:", user_qs)

    # if search_query:
    #     user_qs = user_qs.filter(username__icontains=search_query)

    context = {
        'user_qs': user_qs,
    }

    return render(request, 'fabzen_app/UserManagement/partials/user_list.html',context)    


# def add_user(request):
#     company = Company.objects.filter(status='active')
#     if request.method == "POST":
#         username = request.POST.get('username')
#         email = request.POST.get('email')
#         password = request.POST.get('password')
#         phone = request.POST.get('phone')
#         area = request.POST.get('area')
#         city = request.POST.get('city')

#         company_id = request.POST.get('company')

#         if CustomUser.objects.filter(username=username).exists():
#             messages.error(request, "Username already exists.")
#             return redirect('users')

#         user = CustomUser.objects.create_user(username=username, email=email, password=password)
#         if company_id:
#             company_obj = get_object_or_404(Company, id=company_id)
#             user.client.company = company_obj
#             user.save()

#         user.city = city
        
#         user.save()

#         messages.success(request, "User added successfully.")
#         return redirect('users')
#     context = {
#         'company': company,
#     }
#     return render(request, 'fabzen_app/UserManagement/add_user.html', context)

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CustomUser, Company
def add_user(request):
    company = Company.objects.filter(status='active')
    
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        area = request.POST.get('area')
        city = request.POST.get('city')

        # 👇 MULTIPLE company IDs
        company_ids = request.POST.getlist('company')
        print("company idssss",company_ids)

        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('users')

        # Create user
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password,
            role='client'
        )

        # Assign multiple companies
        if company_ids:
            for cid in company_ids:
                company_obj = get_object_or_404(Company, id=cid)
                user.client.company.add(company_obj)


        # Save other fields
        user.client.city = city
        user.client.created_by = request.user
        user.client.save()

        messages.success(request, "User added successfully.")
        return redirect('users')

    context = {
        'company': company,
        
    }
    return render(request, 'fabzen_app/UserManagement/add_user.html', context)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import CustomUser, Client, Company

def edit_user(request, pk):

    client = get_object_or_404(Client, pk=pk)
    user = client.user
    company = Company.objects.filter(status='active')

    if request.method == "POST":

        # Get input fields
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        phone = request.POST.get('phone')
        area = request.POST.get('area')
        city = request.POST.get('city')

        company_ids = request.POST.getlist('company')

        # ---------- UPDATE USER ----------
        user.username = username
        user.email = email
        
        if password.strip():  # Update only if new password entered
            user.set_password(password)

        user.save()

        # ---------- UPDATE CLIENT ----------
        client.phone = phone
        client.area = area
        client.city = city
        client.save()

        # ---------- UPDATE MANY2MANY COMPANIES ----------
        client.company.clear()         # remove old companies
        for cid in company_ids:
            company_obj = Company.objects.get(id=cid)
            client.company.add(company_obj)

        messages.success(request, "User updated successfully.")

        return redirect("users")   # your listing page

    # GET request - show edit form
    selected_company_ids = client.company.values_list('id', flat=True)

    context = {
        'client': client,
        'company': company,
        'selected_company_ids': list(selected_company_ids),
        'edit' : True
    }
    return render(request, 'fabzen_app/UserManagement/add_user.html', context)





from rest_framework import viewsets
from .models import Client
from .serializers import ClientSerializer

class ClientViewSet(viewsets.ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

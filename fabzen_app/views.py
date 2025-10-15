from django.shortcuts import render,redirect
from .models import Party
from .forms import PartyForm
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

import json
# Create your views here.


def home(request):
    return render(request, 'fabzen_app/dashboard.html')

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

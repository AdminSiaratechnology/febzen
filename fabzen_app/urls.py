from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='dashboard'),
    # ----------------------    PARTY     ----------------------------
    path("company/",views.company,name="company"),
    path('company/add/', views.add_company, name='add_company'),
    path('companylist/',views.company_list,name="company_list"),
    # ----------------------   END PARTY     ----------------------------


    # ----------------------    PARTY     ----------------------------
    path("party/",views.party,name="party"),
    path('partylist/',views.party_list,name="party_list"),
    path('party/add/', views.add_party, name='add_party'),
    path('party/edit/<int:id>/', views.edit_party, name='edit_party'),
    path('party/view/<int:id>/', views.view_party, name='view_party'),

    
    # --------------------      END PARTY   --------------------------

    
]

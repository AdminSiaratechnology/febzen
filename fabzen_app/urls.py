from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='dashboard'),
    # ----------------------    PARTY     ----------------------------
    path("company/",views.company,name="company"),
    path("add_company/",views.add_company,name="add_company"),
    path('companylist/',views.company_list,name="company_list"),
    path('companyedit/<int:pk>/',views.edit_company,name="edit_company"),
    path('company/toggle-status/<int:pk>/', views.toggle_company_status, name='toggle_company_status'),
    
    # ----------------------   END PARTY     ----------------------------

    # ----------------------    PARTY     ----------------------------
    path("party/",views.party,name="party"),
    path('partylist/',views.party_list,name="party_list"),
    path('party/add/', views.add_party, name='add_party'),
    path('party/edit/<int:id>/', views.edit_party, name='edit_party'),
    path('party/view/<int:id>/', views.view_party, name='view_party'),

    
    # --------------------      END PARTY   --------------------------

    
]

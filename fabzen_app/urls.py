from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='dashboard'),
    # ----------------------    PARTY     ----------------------------
    path("party/",views.party,name="party"),
    path('partylist/',views.party_list,name="party_list"),
    path('party/add/', views.add_party, name='add_party'),
    
    # --------------------      END PARTY   --------------------------

    
]

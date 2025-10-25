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
    
    
    # --------------------      Fabzen   --------------------------

    path('fabric/', views.FabricListView.as_view(), name='fabric'),
    path('fabriclist/',views.fabric_list,name="fabric_list"),
    path("create/fabric",views.create_fabric,name="create_Fabric"),
    path('fabric/edit/<int:pk>/', views.update_fabric, name='fabric_update'),

   # --------------------   End  Fabzen   --------------------------------


    # --------------------      Sizes   --------------------------

    path('size/', views.SizesListView, name='size'),
    path('sizelist/',views.size_list,name="size_list"),


    # --------------------      End Sizes   --------------------------

    # --------------------    Garments   --------------------------
    path('garments/', views.GarmentsListView, name='garments'),
    path('garments_list/',views.garments_list,name="garments_list"),
    path('garments/edit/<int:garment_id>/', views.edit_garment, name='edit_garment'),

    # --------------------      End Garments   --------------------------


    # --------------------      Processess   --------------------------

    path('processes/', views.ProcessesListView, name='processes'),
    path('process_list/',views.process_list,name="process_list"),
    path('processes/edit/<int:pk>/', views.edit_process, name='edit_process'),


    # --------------------      End Processess   --------------------------


    # --------------------      Machine   --------------------------


    path('machines/', views.MachineListView, name='machine'),
    path('machinesList/', views.machine_list, name='machine_list'),
    path('machine/edit/<int:pk>/', views.edit_machine, name='edit_machine'),



    # --------------------      End Machine  --------------------------

    
    # --------------------      Operators  --------------------------

    path('operator/', views.OperatorListView, name='operator'),
    path('operatorList/', views.operator_list, name='operator_list'),
    path('operator/edit/<int:pk>/', views.edit_operator, name='edit_operator'),

    # --------------------      End Operators  --------------------------


    
]

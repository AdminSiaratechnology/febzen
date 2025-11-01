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


    # --------------------       Bom & BOO  --------------------------

    path('BOM/', views.BomListView, name='bom'),
    # --------------------      End Bom & BOO  --------------------------


    # --------------------      Ledger  --------------------------

    path('ledger/', views.LedgerListView, name='ledger'),
    path('ledgerList/', views.ledger_list, name='ledger_list'),
    path('add_ledger_group/', views.add_ledger_group, name='add_ledger_group'),
    path('ledger/edit/<int:pk>/', views.edit_ledger, name='edit_ledger'),


    # --------------------      End Ledger  --------------------------



    # --------------------      Purchase  --------------------------

    path('indent/', views.IndentListView, name='indent'),
    path('indentList/', views.indent_list, name='indent_list'),
    path('indent/edit/<int:pk>/', views.edit_indent, name='edit_indent'),

    path('purchase-indent/convert-to-po/<int:pk>/', views.convert_to_po, name='convert_to_po'),


    # --------------------      End Purchase  --------------------------


    


    # --------------------     Purchase Order  --------------------------

    path('purchaseorder/', views.PurchaseOrderListView, name='purchaseorder'),
    path('AddPurchaseOrder/', views.add_purchase_order, name='add_purchase_order'),
    path('purchaseorderList/', views.purchaseorder_list, name='purchaseorder_list'),
    path('get-garment-description/<int:garment_id>/', views.get_garment_description, name='get_garment_description')




    # --------------------      End Purchase Order  --------------------------

    


    
]

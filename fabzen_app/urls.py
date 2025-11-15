from django.urls import path
from . import views

urlpatterns = [
   

    path('dashboard/', views.home, name='dashboard'),
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
    path('Addindent/', views.add_indent, name='add_indent'),
    path('indentList/', views.indent_list, name='indent_list'),
    path('indent/edit/<int:pk>/', views.edit_indent, name='edit_indent'),

    path('purchase-indent/convert-to-po/<int:pk>/', views.convert_to_po, name='convert_to_po'),
    path("modern/", views.Modern, name="modern"),
    path('save-preclose/<int:pk>/', views.save_preclose_qty, name='save_preclose_qty'),



    # --------------------      End Purchase  --------------------------


    


    # --------------------     Purchase Order  --------------------------

    path('purchaseorder/', views.PurchaseOrderListView, name='purchaseorder'),
    path('AddPurchaseOrder/', views.add_purchase_order, name='add_purchase_order'),
    path('purchaseorderList/', views.purchaseorder_list, name='purchaseorder_list'),
    path('purchaseorder/edit/<int:pk>/', views.edit_purchase_order, name='edit_purchase_order'),
    path('get-garment-description/<int:garment_id>/', views.get_garment_description, name='get_garment_description'),
    path('get-garment-details/<int:garment_id>/', views.get_garment_details, name='get_garment_details'),


    # --------------------      End Purchase Order  --------------------------





    # --------------------       Receipt Note  --------------------------
    path('purchaseorder/convert-to-grn/<int:pk>/', views.convert_po_to_grn, name='convert_po_to_grn'),

    path('receiptnote/', views.ReceiptNoteListView, name='receiptnote'),
    path('receiptNoteList/', views.receiptnote_list, name='receiptNoteList'),
    path('AddReceiptNote/', views.add_receipt_note, name='add_receipt_note'),
    path('receiptnote/edit/<int:pk>/', views.edit_receipt_note, name='edit_receipt_note'),

    # --------------------      End Receipt Note  --------------------------


    # --------------------       Grey Purchase  --------------------------
    path('greypurchase/convert-to-greypurchase/<int:pk>/', views.convert_receipt_to_greypurchase, name='convert_receipt_to_greypurchase'),


    path('greypurchase/', views.GreyPurchaseListView, name='greypurchase'),
    path('greyPurchaseList/', views.grey_purchase_list, name='greyPurchaseList'),
    path('AddGreyPurchase/', views.add_grey_purchase, name='add_grey_purchase'),
    path('greypurchase/edit/<int:pk>/', views.edit_grey_purchase, name='edit_grey_purchase'),

    # --------------------      End Grey Purchase  --------------------------

    # --------------------      Purchase Return  --------------------------

    path('purchasereturn/convert-to-purchasereturn/<int:pk>/', views.convert_greypurchase_to_purchasereturn, name='convert_greypurchase_to_purchasereturn'),
    path('purchasereturn/', views.PurchaseReturnListView, name='purchasereturn'),
    path('purchasereturnList/', views.purchasereturn_list, name='purchasereturnList'),
    path('AddPurchaseReturn/', views.add_purchase_return, name='add_purchase_return'),
    path('purchasereturn/edit/<int:pk>/', views.edit_purchase_return, name='edit_purchase_return'),


    # --------------------      End Purchase Return  --------------------------


    # --------------------     User Management  --------------------------

    path('users/', views.Users, name='users'),
    path('userList/', views.user_list, name='user_list'),
    path('addUser/', views.add_user, name='add_user'),


    # --------------------      End User Management  --------------------------


    

    


    
]

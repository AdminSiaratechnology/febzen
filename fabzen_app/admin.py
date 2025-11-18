from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# from .models import GreyPurchase, GreyPurchaseItem, Party,Company,CompanyBank,Fabric,Size,Garment,Process,Machine,Operator,Ledger,LedgerGroup,PurchaseIndent,PurchaseIndentItem,PurchaseOrder,PurchaseOrderItem,GoodsReceiveNote,GoodsReceiveNoteItem,PurchaseReturn,PurchaseReturnItem
from .models import (
    GreyPurchase,
    GreyPurchaseItem,
    Party,
    Company,
    CompanyBank,
    Fabric,
    Size,
    Garment,
    Process,
    Machine,
    Operator,
    Ledger,
    LedgerGroup,
    PurchaseIndent,
    PurchaseIndentItem,
    PurchaseOrder,
    PurchaseOrderItem,
    GoodsReceiveNote,
    GoodsReceiveNoteItem,
    PurchaseReturn,
    PurchaseReturnItem,
    CustomUser,
    Client,
    Admin

)




    
# Register your models here.

# ✅ Inline for GoodsReceiveNoteItem
class GoodsReceiveNoteItemInline(admin.TabularInline):
    model = GoodsReceiveNoteItem
    extra = 1  # Number of empty rows to display
    fields = ('garment', 'quantity', 'uom', 'rate', 'amount')  # Adjust fields as per your model
    readonly_fields = ('amount',)  # If amount is calculated automatically
    show_change_link = True  # Optional: allows link to edit item separately


class PurchaseReturnItemInline(admin.TabularInline):
    model = PurchaseReturnItem
    extra = 1
    fields = ('garment', 'quantity', 'uom', 'rate', 'amount')
    readonly_fields = ('amount',)
    show_change_link = True

# ✅ Inline for GreyPurchaseItem

class GreyPurchaseItemInline(admin.TabularInline):
    model = GreyPurchaseItem
    extra = 1
    fields = ('garment', 'quantity', 'uom', 'rate', 'amount')
    readonly_fields = ('amount',)
    show_change_link = True

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1
    fields = ('garment', 'description', 'quantity', 'uom', 'rate', 'discount', 'amount')
    readonly_fields = ('amount',)
    show_change_link = True

class PurchaseIndentItemInline(admin.TabularInline):
    model = PurchaseIndentItem
    extra = 1
    fields = ('garment', 'quantity', 'uom',  'pending_qty','converted_qty','preclose_qty')
    readonly_fields = ('converted_qty', 'pending_qty')
    show_change_link = True


class ClientInline(admin.TabularInline):
    model = Client
    extra = 0
    fk_name = 'user'
    fields = ('company','multiplePhones', 'contactPerson', 'country', 'state', 'city', 'pincode', 'limit', 'status', 'documents')
    readonly_fields = ('user',)
    show_change_link = True

class AdminInline(admin.TabularInline):
    model = Admin
    extra = 1
    fields = ('client',)
    show_change_link = True


admin.site.register(Party)
admin.site.register(Company)
admin.site.register(CompanyBank)
admin.site.register(Fabric)
admin.site.register(Size)
admin.site.register(Garment)
admin.site.register(Process)
admin.site.register(Machine)
admin.site.register(Operator)
admin.site.register(Ledger)
admin.site.register(LedgerGroup)
# admin.site.register(PurchaseIndent)
# admin.site.register(PurchaseIndentItem)
# admin.site.register(PurchaseOrder)
# admin.site.register(PurchaseOrderItem)

@admin.register(GoodsReceiveNote)
class GoodsReceiveNoteAdmin(admin.ModelAdmin):
    list_display = ('grn_no', 'supplier', 'grn_date', 'total_amount')  # Adjust fields
    inlines = [GoodsReceiveNoteItemInline]

@admin.register(GreyPurchase)
class GreyPurchaseAdmin(admin.ModelAdmin):
    list_display = ('gp_no', 'supplier', 'gp_date', 'total_amount', 'status')  # Adjust fields
    inlines = [GreyPurchaseItemInline]

@admin.register(PurchaseReturn)
class PurchaseReturnAdmin(admin.ModelAdmin):
    list_display = ('pr_no', 'supplier', 'pr_date', 'total_amount')  # Adjust fields
    inlines = [PurchaseReturnItemInline]

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('po_no', 'supplier', 'po_date', 'total_amount', 'status')  # Adjust fields
    inlines = [PurchaseOrderItemInline]

@admin.register(PurchaseIndent)
class PurchaseIndentAdmin(admin.ModelAdmin):
    list_display = ('indent_no', 'indent_date', 'status')  # Adjust fields
    inlines = [PurchaseIndentItemInline]    



@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email')
    inlines = [ClientInline,AdminInline]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("email",)}),
        ("Permissions", {
            "fields": (
                "role", "is_active", "is_staff", "is_superuser",
                "groups", "user_permissions"
            )
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "username", "email", "role",
                "password1", "password2",
                "is_staff", "is_active"
            ),
        }),
    )






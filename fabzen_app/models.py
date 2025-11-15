from django.db import models
from django.db.models import Max

from django.contrib.auth.models import AbstractUser

# Create your models here.

# accounts/models.py


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('client', 'Client'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(unique=True)

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']   # username still required for Django admin

    def __str__(self):
        return f"{self.email} ({self.role})"



class Company(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('deleted', 'Deleted'),
    ]
    company_name_street = models.CharField(max_length=100)
    company_name_print = models.CharField(max_length=100)
    address_line1 = models.TextField()
    address_line2 = models.TextField()
    address_line3 = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=100)
    default_currency = models.CharField(max_length=100,null=True,blank=True )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active'
    )


    # ---------------------------------- Contact Details -------------------

    telephone = models.CharField(max_length=15, null=True,blank=True)
    mobile_no = models.CharField(max_length=15, null=True,blank=True)
    fax_no =  models.CharField(max_length=15, null=True,blank=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)


    # -------------------------------------- Register Details -------------- 

    gst_no =  models.CharField(max_length=15, null=True,blank=True)
    pan_no =  models.CharField(max_length=15, null=True,blank=True)
    tan_no =  models.CharField(max_length=15, null=True,blank=True)
    msme_no =  models.CharField(max_length=15, null=True,blank=True)
    udyan_no =  models.CharField(max_length=15, null=True,blank=True)
 


class CompanyBank(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='banks')
    holder_name = models.CharField(max_length=100,null=True,blank=True)
    account_number = models.CharField(max_length=50,null=True,blank=True)
    ifsc_code = models.CharField(max_length=20,null=True,blank=True)
    swift_code = models.CharField(max_length=100,null=True,blank=True)
    micr_no = models.CharField(max_length=100,null=True,blank=True)
    bank_name = models.CharField(max_length=100,null=True,blank=True)
    branch = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return f"{self.bank_name} - {self.company.company_name_print}"

PARTY_TYPE_PREFIX = {
    'Supplier': 'SUP',
    'Customer': 'CUS',
    'Master': 'MAS',
    'Dyer': 'DYR',
    'Job Worker': 'JOW',
}



class Client(models.Model):
    STATUS_CHOICES = [
        ('active', 'active'),
        ('inactive', 'inactive'),
        ('delete', 'delete'),
        ('suspended', 'suspended'),
        ('hold', 'hold'),
    ]
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    company = models.ManyToManyField(Company, related_name='clients')
    multiplePhones = models.JSONField(default=list, blank=True)
    contactPerson = models.CharField(max_length=255, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    pincode = models.CharField(max_length=100, null=True, blank=True)
    limit = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='active')
    documents = models.FileField(upload_to='client_documents/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Client: {self.user}"


class Admin(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="admins"
    )

    def __str__(self):
        return f"Admin: {self.user.username}"


class Party(models.Model):
    PARTY_TYPE_CHOICES = [
        ('Supplier', 'Supplier'),
        ('Customer', 'Customer'),
        ('Master', 'Master'),
        ('Dyer', 'Dyer'),
        ('Job Worker', 'Job Worker'),
    ]

    code = models.CharField(max_length=100)
    party_name = models.CharField(max_length=100)
    party_type = models.CharField(max_length=50, choices=PARTY_TYPE_CHOICES)
    contact_person = models.CharField(max_length=100, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    gst_number = models.CharField(max_length=20, blank=True, null=True)
    pan_number = models.CharField(max_length=20, blank=True, null=True)
    rating = models.CharField(max_length=20, blank=True, null=True)
    outstanding = models.BigIntegerField(null=True,blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.code:
            prefix = PARTY_TYPE_PREFIX.get(self.party_type, 'OTH')

            # Find last code for this type
            last_code = Party.objects.filter(party_type=self.party_type)\
                                     .aggregate(Max('code'))['code__max']

            if last_code:
                # Extract number part and increment
                try:
                    last_number = int(last_code.split('-')[-1])
                except ValueError:
                    last_number = 0
                new_number = last_number + 1
            else:
                new_number = 1

            self.code = f"{prefix}-{new_number:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.party_name} ({self.party_type})"


class Fabric(models.Model):
    CATEGORY_CHOICES = [
        ('Synthetic', 'Synthetic'),
        ('Voile', 'Voile'),
        ('Poplin', 'Poplin'),
        ('Cambric', 'Cambric'),
        ('Knit', 'Knit'),
    ]

    code = models.CharField(max_length=20, unique=True, verbose_name="Code")
    quality_name = models.CharField(max_length=100, verbose_name="Quality Name")
    construction = models.CharField(max_length=50, verbose_name="Construction", null=True,blank=True)
    width = models.CharField(max_length=10, verbose_name="Width (inches)", null=True,blank=True)
    gsm = models.PositiveIntegerField(verbose_name="GSM", null=True,blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, verbose_name="Category")
    rate_per_meter = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Rate per Meter (₹)", null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Fabric"
        verbose_name_plural = "Fabrics"
        ordering = ['code']

    def __str__(self):
        return f"{self.quality_name} ({self.code})"
    


class Size(models.Model):
    CATEGORY_CHOICES = [
        ('shirts', 'Shirts/T-shirts'),
        ('pants', 'Pants/Trousers'),
        ('ladies', 'Ladies Wear'),
        ('kids', 'Kids Wear'),
    ]

    size_category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        verbose_name="Size Category"
    )

    size_label = models.CharField(
        max_length=50,
        verbose_name="Size Label",
        help_text="e.g., M (40)"
    )

    display_order = models.PositiveIntegerField(
        default=1,
        verbose_name="Display Order"
    )

    # Optional measurements
    chest = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Chest (cm)"
    )
    waist = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Waist (cm)"
    )
    length = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True, verbose_name="Length (cm)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order']
        verbose_name = "Size"
        verbose_name_plural = "Sizes"

    def __str__(self):
        return f"{self.get_size_category_display()} - {self.size_label}"






class Garment(models.Model):
    CATEGORY_CHOICES = [
        ('Shirts', 'Shirts'),
        ('Casual', 'Casual'),
        ('Pants', 'Pants'),
        ('Ethnic', 'Ethnic'),
        ('Ladies', 'Ladies'),
    ]

    garment_code = models.CharField(max_length=10, unique=True,)  # Auto generate mein aap custom kar sakte hain
    # garment_code = models.CharField(max_length=10, unique=True, editable=False)  # Auto generate mein aap custom kar sakte hain
    garment_name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    rate_per_piece = models.DecimalField(max_digits=10, decimal_places=2)
    avg_fabric_consumption = models.CharField(max_length=20, blank=True, null=True)  # Example: '2.2m'
    avg_production_time = models.CharField(max_length=20, blank=True, null=True)    # Example: '45 min'
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.garment_name} ({self.garment_code})"

    # def save(self, *args, **kwargs):
    #     # Auto-generate garment_code if empty, example: G-001, G-002, ...
    #     if not self.garment_code:
    #         last = Garment.objects.all().order_by('id').last()
    #         if last:
    #             last_code_num = int(last.garment_code.split('-')[-1])
    #             self.garment_code = f"G-{last_code_num + 1:03d}"
    #         else:
    #             self.garment_code = "G-001"
    #     super().save(*args, **kwargs)



class Process(models.Model):
    # Choices for Process Type
    PROCESS_TYPE_CHOICES = [
        ('Job Work', 'Job Work'),
        ('In-house', 'In-house'),
    ]

    # Choices for Unit
    UNIT_CHOICES = [
        ('Meter', 'Meter'),
        ('Piece', 'Piece'),
        ('Kg', 'Kg'),
    ]

    process_code = models.CharField(max_length=20, unique=True)
    # process_code = models.CharField(max_length=20, unique=True, editable=False)
    process_name = models.CharField(max_length=100)
    process_type = models.CharField(max_length=20, choices=PROCESS_TYPE_CHOICES)
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES)
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    average_time = models.CharField(max_length=50, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     # Auto-generate process_code like "P-001"
    #     if not self.process_code:
    #         last = Process.objects.order_by('-id').first()
    #         next_number = 1 if not last else last.id + 1
    #         self.process_code = f"P-{next_number:03d}"
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.process_code} - {self.process_name}"


class Operator(models.Model):
    DEPARTMENT_CHOICES = [
        ('Stitching', 'Stitching'),
        ('Cutting', 'Cutting'),
        ('Ironing', 'Ironing'),
        ('Packing', 'Packing'),
        ('Quality Control', 'Quality Control'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('leave', 'Leave'),
        
    ]

    operator_code = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=100)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES)
    mobile_number = models.CharField(max_length=15)
    skills = models.TextField(blank=True, null=True)
    date_of_joining = models.DateField()
    daily_wage = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    address = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50,choices=STATUS_CHOICES, default="active")
    

    def __str__(self):
        return f"{self.operator_code} - {self.full_name}"



class Machine(models.Model):
    MACHINE_TYPE_CHOICES = [
        ('Stitching', 'Stitching'),
        ('Cutting', 'Cutting'),
        ('Finishing', 'Finishing'),
        ('Ironing', 'Ironing'),
    ]

    status_choices = [
        ('Running', 'Running'),
        ('Idle', 'Idle'),
    ]

    machine_code = models.CharField(max_length=20, unique=True)
    machine_name = models.CharField(max_length=100)
    machine_type = models.CharField(max_length=50, choices=MACHINE_TYPE_CHOICES)
    brand = models.CharField(max_length=100, blank=True, null=True)
    capacity_per_day = models.CharField(max_length=50, blank=True, null=True)
    purchase_date = models.DateField(blank=True, null=True)
    # assigned_operator = models.CharField(max_length=100, blank=True, null=True)
    assigned_operator = models.ForeignKey(
        'Operator',
        on_delete=models.SET_NULL,   # When operator is deleted → keep machine record, but set null
        null=True,
        blank=True,
        related_name='machines',     # Allows reverse access like operator.machines.all()
    )
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100,choices=status_choices,default="Running")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.machine_name} ({self.machine_code})"



class LedgerGroup(models.Model):
    ledger_type = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
        ('Liability', 'Liability'),
        ('Asset', 'Asset')
    ]
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=50, choices=ledger_type)

    def __str__(self):
        return self.name
    

# class Ledger(models.Model):
#     LEDGER_GROUP_CHOICES = [
#         ('Direct Income', 'Direct Income'),
#         ('Indirect Income', 'Indirect Income'),
#         ('Direct Expenses', 'Direct Expenses'),
#         ('Indirect Expenses', 'Indirect Expenses'),
#         ('Miscellaneous Expenses', 'Miscellaneous Expenses'),
#         ('Bank Accounts', 'Bank Accounts'),
#         ('Cash', 'Cash'),
#         ('Duties & Taxes', 'Duties & Taxes'),
#     ]

#     BALANCE_TYPE_CHOICES = [
#         ('Debit', 'Debit'),
#         ('Credit', 'Credit'),
#     ]

#     ledger_code = models.CharField(max_length=20, unique=True)
#     ledger_name = models.CharField(max_length=100)
#     ledger_group = models.CharField(max_length=50, choices=LEDGER_GROUP_CHOICES)
#     opening_balance = models.BigIntegerField(default=0)
#     balance_type = models.CharField(max_length=10, choices=BALANCE_TYPE_CHOICES)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"{self.ledger_code} - {self.ledger_name}"


class Ledger(models.Model):
    BALANCE_TYPE_CHOICES = [
        ('Debit', 'Debit'),
        ('Credit', 'Credit'),
    ]

    ledger_code = models.CharField(max_length=20, unique=True)
    ledger_name = models.CharField(max_length=100)

    # 🔹 Changed this line — now it's a ForeignKey
    ledger_group = models.ForeignKey(
        LedgerGroup,
        on_delete=models.CASCADE,
        related_name="ledgers"
    )

    opening_balance = models.BigIntegerField(default=0)
    balance_type = models.CharField(max_length=10, choices=BALANCE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ledger_code} - {self.ledger_name}"
    


class PurchaseIndent(models.Model):
    indent_no = models.CharField(max_length=50, unique=True)
    # requested_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    indent_date = models.DateField(auto_now_add=False)
    required_date = models.DateField(auto_now_add=False,null=True,blank=True)
    requested_by = models.CharField(max_length=100, blank=True, null=True)
    priority = models.CharField(max_length=20,choices=[('High', 'High'),('Medium', 'Medium'), ('Low', 'Low')])
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending', 'Pending'),
            ('Approved', 'Approved'),
            ('Rejected', 'Rejected'),
            ('Close', 'Close'),
        ],
        default='Pending'
    )
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.indent_no}"

    def all_items_closed(self):
        """
        Returns True if no item has pending_qty > 0
        """
        return not self.items.filter(pending_qty__gt=0).exists()
    
from decimal import Decimal
class PurchaseIndentItem(models.Model):
    indent = models.ForeignKey(PurchaseIndent, on_delete=models.CASCADE, related_name='items')
    # item_name = models.CharField(max_length=150)
    garment = models.ForeignKey(Garment, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    uom = models.CharField(max_length=20, verbose_name="Unit of Measure", blank=True, null=True)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    # 👇 ye do naye fields add karo
    converted_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # kitna qty PO me gaya
    preclose_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)    # manually closed qty
    pending_qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)     # kitna qty bacha hai
    

    def save(self, *args, **kwargs):
        """
        Jab bhi save hoga to pending_qty auto update hoga
        pending_qty = total quantity - (converted_qty + preclose_qty)
        """
        total_closed = (self.converted_qty or Decimal('0')) + (self.preclose_qty or Decimal('0'))
        self.pending_qty = (self.quantity or Decimal('0')) - total_closed
        if self.pending_qty < 0:
            self.pending_qty = Decimal('0')
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.garment.garment_name} - {self.quantity}"
    
    def all_items_closed(self):
        """
        Return True if *all* items of this indent have pending_qty = 0
        """
        # agar koi item hai jiska pending_qty > 0 hai, toh False
        return not self.items.filter(pending_qty__gt=0).exists()



from datetime import date



# class PurchaseOrder(models.Model):
#     STATUS_CHOICES = [
#         ('Open', 'Open'),
#         ('Partial', 'Partial'),
#         ('Completed', 'Completed'),
#         ('Cancelled', 'Cancelled'),
#     ]
#     payment_terms = [
#         ('Immediate', 'Immediate'),
#         ('30 Days', '30 Days'),
#         ('60 Days', '60 Days'),
       
#     ]

#     po_no = models.CharField(max_length=20, unique=True)
#     po_date = models.DateField(default=date.today)
#     indent = models.ForeignKey('PurchaseIndent', on_delete=models.SET_NULL, null=True, blank=True)
#     # supplier = models.ForeignKey('Supplier', on_delete=models.SET_NULL, null=True, blank=True)
#     delivery_date = models.DateField(null=True, blank=True)
#     payment_terms = models.CharField(max_length=20, choices=payment_terms, default='Immediate')
#     supplier = models.CharField(max_length=100,null=True,blank=True)
#     total_qty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
#     total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
#     received_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
#     termscondition = models.TextField(blank=True, null=True)

#     def __str__(self):
#         return f"{self.po_no}"

#     def calculate_totals(self):
#         """Recalculate total quantity and amount from items."""
#         total_qty = sum(item.quantity for item in self.items.all())
#         total_amt = sum(item.amount for item in self.items.all())
#         self.total_qty = total_qty
#         self.total_amount = total_amt
#         self.save()


# class PurchaseOrderItem(models.Model):
#     po = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
#     garment = models.ForeignKey('Garment', on_delete=models.SET_NULL, null=True)
#     description = models.CharField(max_length=255, blank=True, null=True)
#     color = models.CharField(max_length=100, blank=True, null=True)
#     quantity = models.DecimalField(max_digits=12, decimal_places=2)
#     uom = models.CharField(max_length=50)
#     rate = models.DecimalField(max_digits=12, decimal_places=2,default=0)
#     discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
#     amount = models.DecimalField(max_digits=15, decimal_places=2, editable=False)

    

#     def save(self, *args, **kwargs):
#         self.amount = self.quantity * self.rate
#         super().save(*args, **kwargs)

 


class PurchaseOrder(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Partial', 'Partial'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Close', 'Close'),
    ]

    converted_FROM_INDENT = [
        ('Yes', 'Yes'), 
        ('No', 'No'),
    ]

    PAYMENT_TERMS = [
        ('Immediate', 'Immediate'),
        ('30 Days', '30 Days'),
        ('60 Days', '60 Days'),
    ]

    po_no = models.CharField(max_length=20, unique=True)
    po_date = models.DateField(default=date.today)
    indent = models.ForeignKey('PurchaseIndent', on_delete=models.SET_NULL, null=True, blank=True)

    # ✅ Suggestion: Keep supplier as ForeignKey for better data integrity
    # If you don’t have a Supplier model yet, your CharField version is fine temporarily
    supplier = models.CharField(max_length=100, null=True, blank=True)

    delivery_date = models.DateField(null=True, blank=True)
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS, default='Immediate')

    total_qty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    received_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    converted_status = models.CharField(max_length=20, choices=converted_FROM_INDENT, default='No')
    termscondition = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-po_date']  # ✅ Latest PO appears first in list view
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"

    def __str__(self):
        return f"{self.po_no}"

    def calculate_totals(self):
        """Recalculate total quantity and amount from items."""
        total_qty = sum(item.quantity for item in self.items.all())
        total_amt = sum(item.amount for item in self.items.all())
        self.total_qty = total_qty
        self.total_amount = total_amt
        self.save()

class PurchaseOrderItem(models.Model):
    po = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    garment = models.ForeignKey('Garment', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)

    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    uom = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, editable=False)

    def save(self, *args, **kwargs):
        # ✅ Discount support added
        if self.discount > 0:
            discounted_rate = self.rate - (self.rate * self.discount / 100)
            self.amount = self.quantity * discounted_rate
        else:
            self.amount = self.quantity * self.rate

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.garment or 'Item'} ({self.quantity} {self.uom})"



# 📦 2️⃣ GOODS RECEIVE NOTE
class GoodsReceiveNote(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Received', 'Received'),
        ('Rejected', 'Rejected'),
    ]

    PAYMENT_TERMS = [  # ✅ Add this line
        ('Immediate', 'Immediate'),
        ('30 Days', '30 Days'),
        ('60 Days', '60 Days'),
    ]

    grn_no = models.CharField(max_length=20, unique=True)
    grn_date = models.DateField(default=date.today)
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS, default='Immediate')
    purchase_order = models.ForeignKey('PurchaseOrder', on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.CharField(max_length=100, null=True, blank=True)
    total_qty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    termscondition = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-grn_date']
        verbose_name = "Goods Receive Note"
        verbose_name_plural = "Goods Receive Notes"

    def __str__(self):
        return f"{self.grn_no}"

    def calculate_totals(self):
        total_qty = sum(item.quantity for item in self.items.all())
        total_amt = sum(item.amount for item in self.items.all())
        self.total_qty = total_qty
        self.total_amount = total_amt
        self.save()


class GoodsReceiveNoteItem(models.Model):
    grn = models.ForeignKey(GoodsReceiveNote, related_name='items', on_delete=models.CASCADE)
    garment = models.ForeignKey('Garment', on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    uom = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    remarks = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.garment or 'Item'} ({self.quantity} {self.uom})"



# 🧵 1️⃣ GREY PURCHASE
class GreyPurchase(models.Model):
    STATUS_CHOICES = [
        ('Open', 'Open'),
        ('Partial', 'Partial'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
        ('Close', 'Close'),
    ]

    PAYMENT_TERMS = [
        ('Immediate', 'Immediate'),
        ('30 Days', '30 Days'),
        ('60 Days', '60 Days'),
    ]

    gp_no = models.CharField(max_length=20, unique=True)
    gp_date = models.DateField(default=date.today)
    grn = models.ForeignKey('GoodsReceiveNote', on_delete=models.SET_NULL, null=True, blank=True)
    supplier = models.CharField(max_length=100, null=True, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS, default='Immediate')

    total_qty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    received_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    termscondition = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-gp_date']
        verbose_name = "Grey Purchase"
        verbose_name_plural = "Grey Purchases"

    def __str__(self):
        return f"{self.gp_no}"

    def calculate_totals(self):
        total_qty = sum(item.quantity for item in self.items.all())
        total_amt = sum(item.amount for item in self.items.all())
        self.total_qty = total_qty
        self.total_amount = total_amt
        self.save()


class GreyPurchaseItem(models.Model):
    gp = models.ForeignKey(GreyPurchase, related_name='items', on_delete=models.CASCADE)
    garment = models.ForeignKey('Garment', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    color = models.CharField(max_length=100, blank=True, null=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    uom = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    remarks = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.discount > 0:
            discounted_rate = self.rate - (self.rate * self.discount / 100)
            self.amount = self.quantity * discounted_rate
        else:
            self.amount = self.quantity * self.rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.garment or 'Item'} ({self.quantity} {self.uom})"



# 🔁 3️⃣ PURCHASE RETURN
class PurchaseReturn(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Returned', 'Returned'),
        ('Cancelled', 'Cancelled'),
    ]

    PAYMENT_TERMS = [
        ('Immediate', 'Immediate'),
        ('30 Days', '30 Days'),
        ('60 Days', '60 Days'),
    ]

    pr_no = models.CharField(max_length=20, unique=True)
    pr_date = models.DateField(default=date.today)
    greypurchase = models.ForeignKey(GreyPurchase, on_delete=models.SET_NULL, null=True, blank=True)
    payment_terms = models.CharField(max_length=20, choices=PAYMENT_TERMS, default='Immediate')
    supplier = models.CharField(max_length=100, null=True, blank=True)
    total_qty = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    reason = models.TextField(blank=True, null=True)
    termscondition = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-pr_date']
        verbose_name = "Purchase Return"
        verbose_name_plural = "Purchase Returns"

    def __str__(self):
        return f"{self.pr_no}"

    def calculate_totals(self):
        total_qty = sum(item.quantity for item in self.items.all())
        total_amt = sum(item.amount for item in self.items.all())
        self.total_qty = total_qty
        self.total_amount = total_amt
        self.save()


class PurchaseReturnItem(models.Model):
    pr = models.ForeignKey(PurchaseReturn, related_name='items', on_delete=models.CASCADE)
    garment = models.ForeignKey('Garment', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.CharField(max_length=255, blank=True, null=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    uom = models.CharField(max_length=50)
    rate = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=15, decimal_places=2, editable=False)
    reason = models.CharField(max_length=255, blank=True, null=True)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        self.amount = self.quantity * self.rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.garment or 'Item'} ({self.quantity} {self.uom})"

from django.db import models
from django.db.models import Max

# Create your models here.


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
    default_currency = models.CharField(max_length=100)
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
    assigned_operator = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=100,choices=status_choices,default="Running")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.machine_name} ({self.machine_code})"


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






class Ledger(models.Model):
    LEDGER_GROUP_CHOICES = [
        ('Direct Income', 'Direct Income'),
        ('Indirect Income', 'Indirect Income'),
        ('Direct Expenses', 'Direct Expenses'),
        ('Indirect Expenses', 'Indirect Expenses'),
        ('Miscellaneous Expenses', 'Miscellaneous Expenses'),
        ('Bank Accounts', 'Bank Accounts'),
        ('Cash', 'Cash'),
        ('Duties & Taxes', 'Duties & Taxes'),
    ]

    BALANCE_TYPE_CHOICES = [
        ('Debit', 'Debit'),
        ('Credit', 'Credit'),
    ]

    ledger_code = models.CharField(max_length=20, unique=True)
    ledger_name = models.CharField(max_length=100)
    ledger_group = models.CharField(max_length=50, choices=LEDGER_GROUP_CHOICES)
    opening_balance = models.BigIntegerField(default=0)
    balance_type = models.CharField(max_length=10, choices=BALANCE_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ledger_code} - {self.ledger_name}"

from django.db import models
from django.db.models import Max

# Create your models here.

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

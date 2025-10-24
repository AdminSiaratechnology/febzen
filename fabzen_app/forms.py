from django import forms
from .models import Party

class PartyForm(forms.ModelForm):
    class Meta:
        model = Party
        fields = [
            'party_name',
            'party_type',
            'contact_person',
            'mobile',
            'address',
            'city',
            'state',
            'pincode',
            'gst_number',
            'pan_number',
        ]
        widgets = {
            'party_name': forms.TextInput(attrs={'class': 'form-control'}),
            'party_type': forms.Select(attrs={'class': 'form-select'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-control'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'gst_number': forms.TextInput(attrs={'class': 'form-control'}),
            'pan_number': forms.TextInput(attrs={'class': 'form-control'}),
        }






from django import forms
from .models import Fabric

# class FabricForm(forms.ModelForm):
#     class Meta:
#         model = Fabric
#         fields = ['code', 'quality_name', 'construction', 'width', 'gsm', 'category', 'rate_per_meter']
#         widgets = {
#             'category': forms.Select(attrs={'class': 'form-select'}),
#             'quality_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'construction': forms.TextInput(attrs={'class': 'form-control'}),
#             'width': forms.TextInput(attrs={'class': 'form-control'}),
#             'gsm': forms.NumberInput(attrs={'class': 'form-control'}),
#             'rate_per_meter': forms.NumberInput(attrs={'class': 'form-control'}),
#             'code': forms.TextInput(attrs={'class': 'form-control'}),
# }


class FabricForm(forms.ModelForm):
    class Meta:
        model = Fabric
        fields = ['quality_name', 'construction', 'width', 'gsm', 'category', 'rate_per_meter', 'description']




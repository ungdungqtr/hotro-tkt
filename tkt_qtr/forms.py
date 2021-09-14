from django import forms
from .models import CanBo, NNT

class CanBoForm(forms.ModelForm):
    class Meta:
        model  = CanBo
        fields = ['ten_cb', 'gioi_tinh', 'ngach_cb', 'chuc_vu']

class NNTForm(forms.ModelForm):
    class Meta:
        model = NNT
        fields = ['mst', 'ten_nnt', 'dia_chi', 'cqt']

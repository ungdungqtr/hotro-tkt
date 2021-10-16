from django import forms
from .models import *

class CanBoForm(forms.ModelForm):

    class Meta:
        model  = CanBo
        fields = ['ten_cb', 'gioi_tinh', 'chuc_vu']

class NNTForm(forms.ModelForm):

    class Meta:
        model = NNT
        fields = ['mst', 'ten_nnt', 'dia_chi', 'cqt']

class LdPheDuyetForm(forms.ModelForm):
    
    class Meta:
        model = LdPheDuyet
        fields = ['ld_gt', 'ld_ten', 'ld_cv']

class CanCuForm(forms.ModelForm):
    
    class Meta:
        model = CanCu
        fields = ['so_qd', 'ten_qd', 'ngay_qd']

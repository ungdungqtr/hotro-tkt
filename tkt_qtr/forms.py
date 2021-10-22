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
    
    def clean_mst(self):
        data = self.cleaned_data.get("mst")
        if not data:
            raise forms.ValidationError("Vui lòng điền thông tin")
        return data
    def clean_ten_nnt(self):
        data = self.cleaned_data.get("ten_nnt")
        if not data:
            raise forms.ValidationError("Vui lòng điền thông tin")
        return data
    def clean_dia_chi(self):
        data = self.cleaned_data.get("dia_chi")
        if not data:
            raise forms.ValidationError(("Vui lòng điền thông tin"))
        return data
    def clean_cqt(self):
        data = self.cleaned_data.get("cqt")
        if not data:
            raise forms.ValidationError("Vui lòng điền thông tin")
        return data

class NNTSearchForm(forms.ModelForm):
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

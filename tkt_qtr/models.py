from django.db import models

# Create your models here.
class CanBo(models.Model):
    ten_cb = models.CharField(max_length=30, default='')
    gioi_tinh = models.CharField(max_length=3, default='')
    chuc_vu = models.CharField(max_length=30, default='')
    doan_tkt = models.CharField(max_length=30, default='')

class NNT(models.Model):
    mst = models.CharField(max_length=14, unique=True, blank=True, null=True)
    ten_nnt = models.CharField(max_length=120, blank=True, null=True)
    dia_chi = models.CharField(max_length=255, blank=True, null=True)
    cqt = models.CharField(max_length=50, blank=True, null=True)

class CanCu(models.Model):
    so_qd= models.CharField(max_length=25, default='')
    ten_qd = models.CharField(max_length=255, default='')
    ngay_qd = models.DateField()
    
class LdPheDuyet(models.Model):
    ld_gt= models.CharField(max_length=3, default='')
    ld_ten = models.CharField(max_length=30, default='')
    ld_cv = models.CharField(max_length=20, default='')
  

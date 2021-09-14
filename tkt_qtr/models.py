from django.db import models

# Create your models here.
class CanBo(models.Model):
    ten_cb = models.CharField(max_length=30, blank=True, null=True)
    ngach_cb = models.CharField(max_length=30, blank=True, null=True)
    gioi_tinh = models.CharField(max_length=3, default='', blank=True, null=True)
    chuc_vu = models.CharField(max_length=20, default='', blank=True, null=True)

class NNT(models.Model):
    mst = models.CharField(max_length=14, unique=True, null=True, blank=True)
    ten_nnt = models.CharField(max_length=120, null=True, blank=True)
    dia_chi = models.CharField(max_length=255, default='', null=True, blank=True)
    cqt = models.CharField(max_length=50, default='', blank=True, null=True)


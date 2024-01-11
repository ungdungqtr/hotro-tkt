from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CanBo(models.Model):
    ten_cb = models.CharField(max_length=30, default='')
    gioi_tinh = models.CharField(max_length=3, default='')
    chuc_vu = models.CharField(max_length=30, default='')

    class Meta:
        permissions = (
            ('canbo_view', 'CanBo View'),
            ('canbo_add', 'CanBo Add'),
            ('canbo_edit', 'CanBo Edit'),
            ('canbo_delete', 'CanBo Delete'),
        )

class NNT(models.Model):
    mst = models.CharField(max_length=14, unique=True, blank=True, null=True)
    ten_nnt = models.CharField(max_length=120, blank=True, null=True)
    dia_chi = models.CharField(max_length=255, blank=True, null=True)
    cqt = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        permissions = (
            ('nnt_view', 'NNT View'),
            ('nnt_add', 'NNT Add'),
            ('nnt_edit', 'NNT Edit'),
            ('nnt_delete', 'NNT Delete'),
        )

class CanCu(models.Model):
    ten_cc= models.CharField(max_length=255, default='')
    so_qd= models.CharField(max_length=25, default='')
    ten_qd = models.CharField(max_length=255, default='')
    ngay_qd = models.DateField()

    class Meta:
        permissions = (
            ('cancu_view', 'CanCu View'),
            ('cancu_add', 'CanCu Add'),
            ('cancu_edit', 'CanCu Edit'),
            ('cancu_delete', 'CanCu Delete'),
        )
    
class LdPheDuyet(models.Model):
    ld_gt= models.CharField(max_length=3, default='')
    ld_ten = models.CharField(max_length=30, default='')
    ld_cv = models.CharField(max_length=20, default='')

    class Meta:
        permissions = (
            ('ld_view', 'LdPheDuyet View'),
            ('ld_add', 'LdPheDuyet Add'),
            ('ld_edit', 'LdPheDuyet Edit'),
            ('ld_delete', 'LdPheDuyet Delete'),
        )

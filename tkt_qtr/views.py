from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.urls import reverse

from .forms import *
from . import process_data

import os
from zipfile import ZipFile
# import uuid
import csv
from datetime import datetime

ky_ten = {
    'PHÓ CỤC TRƯỞNG' : 'KT.CỤC TRƯỞNG',
    'CỤC TRƯỞNG': 'CỤC TRƯỞNG'
}

# Create your views here.
def thiet_lap_chung(request):    
    cancu = CanCu.objects.all()
    ld_phe_duyet = LdPheDuyet.objects.all()
    context = {
        'cancu': cancu,
        'ld_phe_duyet': ld_phe_duyet
    }
    return render(request, 'tkt_qtr/thiet_lap_chung.html', context=context)

def cap_nhat_qd(request):
    id_1 = request.GET.get('id', None)
    so_qd_1 = request.GET.get('so_qd', None)
    ten_qd_1 = request.GET.get('ten_qd', None)
    ngay_qd_1 = request.GET.get('ngay_qd', None)

    obj = CanCu.objects.get(id=id_1)
    obj.so_qd = so_qd_1
    obj.ten_qd = ten_qd_1
    obj.ngay_qd = ngay_qd_1
    obj.save()
    
    qd = {'id': obj.id, 'so_qd': obj.so_qd, 'ten_qd': obj.ten_qd, 'ngay_qd': obj.ngay_qd}
    return JsonResponse({'qd': qd})

def cap_nhat_ld(request):
    id_1 = request.GET.get('id', None)
    ld_ten_1 = request.GET.get('ld_ten', None)
    obj_1 = CanBo.objects.get(ten_cb=ld_ten_1)

    obj = LdPheDuyet.objects.get(id=id_1)
    obj.ld_gt = obj_1.gioi_tinh
    obj.ld_ten = obj_1.ten_cb
    obj.ld_cv = obj_1.chuc_vu
    obj.save()
    ld = {'id': obj.id, 'ld_gt': obj.ld_gt, 'ld_ten': obj.ld_ten,'ld_cv': obj.ld_cv}

    return JsonResponse({'ld': ld})

def import_thiet_lap(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = os.path.join(settings.MEDIA_ROOT, filename)
        read_csv_setting(settings.MEDIA_ROOT, filename)
        # dba = NNT.objects.all()
        # return render(request, 'tkt_qtr/dba_nnt.html', {'dba': dba})
        return HttpResponseRedirect(reverse('tkt:thiet_lap_chung'))
    return render(request, 'tkt_qtr/import_thiet_lap_chung.html')

def read_csv_setting(MEDIA_ROOT, filename):
    uploaded_file_url = os.path.join(MEDIA_ROOT, filename)
    print(uploaded_file_url)
    print(filename)
    # reading csv file
    with open(uploaded_file_url, 'r', encoding="utf8") as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        
        # extracting field names through first row
        fields = next(csvreader)
        if filename == 'QD.csv':
            print(filename)
            # extracting each data row one by one, then update database
            for row in csvreader:
                obj = CanCu.objects.create(
                    so_qd = row[1],
                    ten_qd = row[2],
                    ngay_qd = row[3],
                )
        elif filename == 'LD.csv':
            print(filename)
            for row in csvreader:
                obj = LdPheDuyet.objects.create(
                    ld_ten = row[1],
                    ld_cv = row[2],
                    ld_gt = row[3],
                ) 

def lap_qd_ttra(request):
    noi_nhan = {
        'Cục Thuế tỉnh Quảng Trị': 'Phòng KK&KTT',
        'CCT KV Đông Hà - Cam Lộ': 'CCT KV Đông Hà - Cam Lộ',
        'CCT KV Triệu Hải': 'CCT KV Triệu Hải',
        'CCT KV Vĩnh Linh - Gio Linh': 'CCT KV Vĩnh Linh - Gio Linh',
        'CCT huyện Đakrông': 'CCT huyện Đakrông',
        'CCT huyện Hướng Hóa': 'CCT huyện Hướng Hóa',
        'CCT huyện Cồn Cỏ': 'CCT huyện Cồn Cỏ'
    }
    qd_tkt_tct = CanCu.objects.get(id=1)
    ld_cuc = LdPheDuyet.objects.get(id=1)
    ld_phong = LdPheDuyet.objects.get(id=2)
    context = {
        'ld_cuc': ld_cuc,
        'ld_phong': ld_phong
    }
    if request.method == 'POST':
        mst = request.POST['mst']
        nnt = NNT.objects.get(mst=mst)
        ngay_thang = request.POST['ngay_thang'].split("/")
        ngay_ktra = request.POST['ngay_ktra'].split("/")
        thanh_vien = request.POST.getlist('thanh_vien', None)
        cv = ['Trưởng đoàn']
        cv.extend(["Thành viên"] * (len(thanh_vien)-1))
        doan_ttra = {
            "<ten_cb>" : [(CanBo.objects.get(ten_cb=tv).gioi_tinh + ": " + tv) for tv in thanh_vien],
            "<ngach_cb>" : [CanBo.objects.get(ten_cb=tv).ngach_cb for tv in thanh_vien],
            "<cv_doan>" : cv
        }
        tt_qd = { 
            '<qd_tkt_tct>': 'Quyết định số '+ qd_tkt_tct.so_qd,
            '<qd_tkt_tct_ngay_ban_hanh>': qd_tkt_tct.ngay_qd.strftime(" ngày %d tháng %m") + " năm " + qd_tkt_tct.ngay_qd.strftime("%Y"),
            '<nam_kh_tkt>': datetime.now().strftime("%Y"),
            '<ngay_thang>' : "ngày      tháng " + leading_zero(ngay_thang[0], 3) + " năm " + ngay_thang[1],
            '<ten_dv>' : nnt.ten_nnt,# nnt(mst)['ten_nnt'],
            '<mst>' : mst,
            '<dia_chi>' : nnt.dia_chi,# nnt(mst)['dia_chi'],
            "<sl_cb>" : f"{len(thanh_vien):02d}",
            '<truong_doan_ttr>': thanh_vien[0],
            "<cb_cv>" : CanBo.objects.get(ten_cb=thanh_vien[0]).gioi_tinh + ": " + thanh_vien[0] + " - " + CanBo.objects.get(ten_cb=thanh_vien[0]).chuc_vu if thanh_vien else "",
            '<so_nam_ktra>' : leading_zero(request.POST['so_nam_ktra'], 10),
            '<nam_ktra>' : request.POST['nam_ktra'],
            '<so_ngay_ktra>' : f"{int(request.POST['so_ngay_ktra']):02d}",         
            '<ngay_ktra>' : "ngày " + ngay_ktra[0] + " tháng " + leading_zero(ngay_ktra[1], 3) + " năm " + ngay_ktra[2],
            '<ng_giam_sat>' : ld_phong.ld_gt.lower() + " " + ld_phong.ld_ten,
            '<Ng_giam_sat>' : ld_phong.ld_gt + " " + ld_phong.ld_ten,
            '<ng_giam_sat_cv>' : ld_phong.ld_cv, 
            '<LD_PHONG>' : ld_phong.ld_cv.upper(),
            '<ld_phong>' : ld_phong.ld_cv,
            '<ld_phong_ten>' : ld_phong.ld_ten,
            '<LD_CUC>' : ld_cuc.ld_cv.upper() if ld_cuc.ld_cv != 'Cục trưởng' else '',
            '<ld_cuc_ten>' : ld_cuc.ld_ten,
            '<hinh_thuc_ky>' : ky_ten[ld_cuc.ld_cv.upper()],
            '<noi_nhan>': noi_nhan[nnt.cqt],
        }        
        QD = process_data.lap_qd_ttra(tt_qd, doan_ttra)
        QD.empty_media()
        file_path = [QD.to_trinh(), QD.qd_ttra(), QD.kh_ttra(), QD.qd_gsat(), QD.kh_gsat()]
        zip_path = os.path.join(settings.STATICFILES_DIRS[0], "media_store", mst + "_QD_ttra.zip")
        # writing files to a zipfile
        with ZipFile(zip_path,'w') as zip:
            # writing each file one by one
            for path in file_path:
                zip.write(path, os.path.basename(path))
        # Full path of file
        if os.path.exists(zip_path):
            with open(zip_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/force_download")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(zip_path)
                return response
        # If file is not exists
        raise Http404
    
    return render(request, 'tkt_qtr/lap_qd_ttra.html', context=context)

# Lập quyết định kiểm tra
def lap_qd_ktra(request):
    qd_tkt_tct = CanCu.objects.get(id=1)
    ld_cuc = LdPheDuyet.objects.get(id=1)
    ld_phong = LdPheDuyet.objects.get(id=2)
    context = {
        'ld_cuc': ld_cuc,
        'ld_phong': ld_phong
    }
    if request.method == 'POST':
        mst = request.POST['mst']
        nnt = NNT.objects.get(mst=mst)
        ngay_thang = request.POST['ngay_thang'].split("/")
        ngay_ktra = request.POST['ngay_ktra'].split("/")     
        thanh_vien = request.POST.getlist('thanh_vien', None)
        cv = ['Trưởng đoàn']
        cv.extend(["Thành viên"] * (len(thanh_vien)-1))
        doan_ktra = {
            "<ten_cb>" : [(CanBo.objects.get(ten_cb=tv).gioi_tinh + ": " + tv) for tv in thanh_vien],
            "<ngach_cb>" : [CanBo.objects.get(ten_cb=tv).ngach_cb for tv in thanh_vien],
            "<cv_doan>" : cv
        }
        tt_qd = { 
            '<ngay_thang>' : "ngày      tháng " + leading_zero(ngay_thang[0], 3) + " năm " + ngay_thang[1],
            '<qd_tkt_tct>': 'Quyết định số '+ qd_tkt_tct.so_qd,
            '<qd_tkt_tct_ngay_ban_hanh>': qd_tkt_tct.ngay_qd.strftime(" ngày %d tháng %m") + " năm " + qd_tkt_tct.ngay_qd.strftime("%Y"),
            '<nam_kh_tkt>': datetime.now().strftime("%Y"),
            '<ten_dv>' : nnt.ten_nnt,# nnt(mst)['ten_nnt'],
            '<mst>' : mst,
            '<dia_chi>' : nnt.dia_chi,# nnt(mst)['dia_chi'],
            "<sl_cb>" : f"{len(thanh_vien):02d}",
            "<cb_cv>" : CanBo.objects.get(ten_cb=thanh_vien[0]).gioi_tinh + ": " + thanh_vien[0] + " - " + CanBo.objects.get(ten_cb=thanh_vien[0]).chuc_vu if thanh_vien else "",
            '<so_nam_ktra>' : leading_zero(request.POST['so_nam_ktra'], 10),
            '<nam_ktra>' : request.POST['nam_ktra'],
            '<so_ngay_ktra>' : f"{int(request.POST['so_ngay_ktra']):02d}",         
            '<ngay_ktra>' : "ngày " + ngay_ktra[0] + " tháng " + leading_zero(ngay_ktra[1], 3) + " năm " + ngay_ktra[2],
            '<ng_giam_sat>' : ld_phong.ld_gt.lower() + " " + ld_phong.ld_ten,
            '<Ng_giam_sat>' : ld_phong.ld_gt + " " + ld_phong.ld_ten,
            '<ng_giam_sat_cv>' : ld_phong.ld_cv, 
            '<LD_PHONG>' : ld_phong.ld_cv.upper(),
            '<ld_phong>' : ld_phong.ld_cv,
            '<ld_phong_ten>' : ld_phong.ld_ten,
            '<LD_CUC>' : ld_cuc.ld_cv.upper() if ld_cuc.ld_cv != 'Cục trưởng' else '',
            '<ld_cuc_ten>' : ld_cuc.ld_ten,
            '<hinh_thuc_ky>' : ky_ten[ld_cuc.ld_cv.upper()],
            # '<noi_nhan>': noi_nhan[nnt.cqt],
        }
        QD = process_data.lap_qd_ktra(tt_qd, doan_ktra)
        QD.empty_media()
        file_path = [QD.to_trinh(), QD.qd_ktra(), QD.qd_gsat()]
        zip_path = os.path.join(settings.STATICFILES_DIRS[0], "media_store", mst + "_QD_ktra.zip")
        # writing files to a zipfile
        with ZipFile(zip_path,'w') as zip:
            # writing each file one by one
            for path in file_path:
                zip.write(path, os.path.basename(path))
        # Full path of file
        if os.path.exists(zip_path):
            with open(zip_path, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/force_download")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(zip_path)
                return response
        # If file is not exists
        raise Http404
    return render(request, 'tkt_qtr/lap_qd_ktra.html', context=context)

def leading_zero(s, max):
    s = int(s)
    return ('0' + str(s)) if s < max else str(s)

def nnt_thong_tin(request):
    mst = request.GET.get('mst', None)
    try:
        obj = NNT.objects.get(mst=mst)
        nnt = {'ten_nnt': obj.ten_nnt, 'dia_chi': obj.dia_chi}
    except ObjectDoesNotExist:
        nnt = {}
    return JsonResponse(nnt)

def cb_thong_tin(request):
    ten_cb = request.GET.get('ten_cb', None)
    try:
        obj = CanBo.objects.get(ten_cb=ten_cb)
        cb = {'chuc_vu': obj.chuc_vu, 'gioi_tinh': obj.gioi_tinh, 'ngach_cb': obj.ngach_cb}
    except ObjectDoesNotExist:
        cb = {}
    return JsonResponse(cb)

def mst_autocomplete(request):
    if 'term' in request.GET:
        mst_filter = NNT.objects.filter(mst__icontains=request.GET.get('term', None))
        ma_so = list()
        for nnt in mst_filter:
            ma_so.append(nnt.mst)
        # titles = [product.title for product in qs]
        return JsonResponse(ma_so, safe=False)
    return render(request, 'tkt_qtr/lap_qd_ktra.html')

def cb_ten_autocomplete(request):
    if 'term' in request.GET:
        ten_cb_filter = CanBo.objects.filter(ten_cb__icontains=request.GET.get('term', None))
        ten = list()
        for cb in ten_cb_filter:
            ten.append(cb.ten_cb)
        # titles = [product.title for product in qs]
        return JsonResponse(ten, safe=False)
    return render(request, 'tkt_qtr/lap_qd_ktra.html')

# Quản lý cán bộ

def qly_cb(request):
    can_bo = CanBo.objects.all()
    return render(request, 'tkt_qtr/qly_cb.html', {'can_bo': can_bo})

def them_moi_cb(request):
    gioi_tinh_1 = request.GET.get('gioi_tinh', None)
    ten_cb_1 = request.GET.get('ten_cb', None)
    ngach_cb_1 = request.GET.get('ngach_cb', None)
    chuc_vu_1 = request.GET.get('chuc_vu', None)

    obj = CanBo.objects.create(
        gioi_tinh = gioi_tinh_1,
        ten_cb = ten_cb_1,
        ngach_cb = ngach_cb_1,
        chuc_vu = chuc_vu_1
    )

    user = {'id': obj.id, 'ten_cb': obj.ten_cb, 'gioi_tinh': obj.gioi_tinh, 'ngach_cb': obj.ngach_cb, 'chuc_vu': obj.chuc_vu}

    return JsonResponse({'user': user})

def cap_nhat_thong_tin(request):
    id_1 = request.GET.get('id', None)
    gioi_tinh_1 = request.GET.get('gioi_tinh', None)
    ten_cb_1 = request.GET.get('ten_cb', None)
    ngach_cb_1 = request.GET.get('ngach_cb', None)
    chuc_vu_1 = request.GET.get('chuc_vu', None)

    obj = CanBo.objects.get(id=id_1)
    obj.ten_cb = ten_cb_1
    obj.gioi_tinh = gioi_tinh_1
    obj.ngach_cb = ngach_cb_1
    obj.chuc_vu = chuc_vu_1
    obj.save()

    user = {'id': obj.id, 'ten_cb': obj.ten_cb, 'gioi_tinh': obj.gioi_tinh, 'ngach_cb': obj.ngach_cb, 'chuc_vu': obj.chuc_vu}

    return JsonResponse({'user': user})

def xoa_cb(request):
    id_1 = request.GET.get('id', None)
    CanBo.objects.get(id=id_1).delete()
    return JsonResponse({'delete': True})

# Danh bạ NNT

def dba_nnt(request):
    dba = NNT.objects.all()
    return render(request, 'tkt_qtr/dba_nnt.html', {'dba': dba})

def them_moi_nnt(request):
    mst_1 = request.GET.get('mst', None)
    ten_nnt_1 = request.GET.get('ten_nnt', None)
    dia_chi_1 = request.GET.get('dia_chi', None)
    cqt_1 = request.GET.get('cqt', None)

    obj = NNT.objects.create(
        mst = mst_1,
        ten_nnt = ten_nnt_1,
        dia_chi = dia_chi_1,
        cqt = cqt_1
    )

    nnt = {'id': obj.id, 'mst': obj.mst, 'ten_nnt': obj.ten_nnt, 'dia_chi': obj.dia_chi, 'cqt': obj.cqt}

    return JsonResponse({'nnt': nnt})

def cap_nhat_nnt(request):
    id_1 = request.GET.get('id', None)
    ten_nnt_1 = request.GET.get('ten_nnt', None)
    dia_chi_1 = request.GET.get('dia_chi', None)
    cqt_1 = request.GET.get('cqt', None)

    obj = NNT.objects.get(id=id_1)
    obj.ten_nnt = ten_nnt_1
    obj.dia_chi = dia_chi_1
    obj.cqt = cqt_1
    obj.save()

    nnt = {'id': obj.id, 'mst': obj.mst, 'ten_nnt': obj.ten_nnt, 'dia_chi': obj.dia_chi, 'cqt': obj.cqt}
    
    return JsonResponse({'nnt': nnt})

def xoa_nnt(request):
    id_1 = request.GET.get('id', None)
    NNT.objects.get(id=id_1).delete()
    data = {'delete': True}

    return JsonResponse(data)

def import_nnt(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = os.path.join(settings.MEDIA_ROOT, filename)
        read_csv_nnt(uploaded_file_url)
        # dba = NNT.objects.all()
        # return render(request, 'tkt_qtr/dba_nnt.html', {'dba': dba})
        return HttpResponseRedirect(reverse('tkt:dba_nnt'))
    return render(request, 'tkt_qtr/import_nnt.html')

def read_csv_nnt(uploaded_file_url):
    # reading csv file
    with open(uploaded_file_url, 'r', encoding="utf8") as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        
        # extracting field names through first row
        fields = next(csvreader)
    
        # extracting each data row one by one, then update database
        for row in csvreader:
            obj = NNT.objects.create(
                mst = row[1],
                ten_nnt = row[2],
                dia_chi = row[3],
                cqt = row[4]
            )

    
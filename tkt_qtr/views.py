from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
import json

from .forms import *
from . import process_data

import os
from zipfile import ZipFile
import uuid


# Create your views here.
def index(request):
    return render(request, 'tkt_qtr/base.html')

# Lập quyết định kiểm tra
def lap_qd_ktra(request):
    ky_ten = {
        'PHÓ CỤC TRƯỞNG' : 'KT.CỤC TRƯỞNG',
        'CỤC TRƯỞNG': 'CỤC TRƯỞNG'
    }
    noi_nhan = {
        'Cục Thuế tỉnh Quảng Trị': 'Phòng KK&KTT',
        'CCT KV Đông Hà - Cam Lộ': 'CCT KV Đông Hà - Cam Lộ',
        'CCT KV Triệu Hải': 'CCT KV Triệu Hải',
        'CCT KV Vĩnh Linh - Gio Linh': 'CCT KV Vĩnh Linh - Gio Linh',
        'CCT huyện Đakrông': 'CCT huyện Đakrông',
        'CCT huyện Hướng Hóa': 'CCT huyện Hướng Hóa',
        'CCT huyện Cồn Cỏ': 'CCT huyện Cồn Cỏ'
    }
    if request.method == 'POST':
        # query mst
        mst = request.POST['mst']
        nnt = NNT.objects.get(mst=mst)
        # query ng_giam_sat
        ng_giam_sat = request.POST['ng_giam_sat']
        gsat = CanBo.objects.get(ten_cb=ng_giam_sat)
        # query ten_ld_to_trinh
        ten_ld_to_trinh =request.POST['ten_ld_to_trinh']
        ky_ttr = CanBo.objects.get(ten_cb=ten_ld_to_trinh)
        # query ten_ld_qd
        ten_ld_qd = request.POST['ten_ld_qd']
        ky_qd = CanBo.objects.get(ten_cb=ten_ld_qd)

        nt = request.POST['ngay_thang'].split("/")
        nkt = request.POST['ngay_ktra'].split("/")              
        thanh_vien = request.POST.getlist('thanh_vien', None)
        cv = ['Trưởng đoàn']
        cv.extend(["Thành viên"] * (len(thanh_vien)-1))
        doan_ktra = {
            "<ten_cb>" : [(CanBo.objects.get(ten_cb=tv).gioi_tinh + ": " + tv) for tv in thanh_vien],
            "<ngach_cb>" : [CanBo.objects.get(ten_cb=tv).ngach_cb for tv in thanh_vien],
            "<cv_doan>" : cv
        }
        tt_qd = { 
            '<ngay_thang>' : "ngày      tháng " + leading_zero(nt[0], 3) + " năm " + nt[1],
            '<nam>':nt[1],
            '<so_qd>' : request.POST['so_qd'],
            '<ten_dv>' : nnt.ten_nnt,# nnt(mst)['ten_nnt'],
            '<mst>' : mst,
            '<dia_chi>' : nnt.dia_chi,# nnt(mst)['dia_chi'],
            "<sl_cb>" : f"{len(thanh_vien):02d}",
            "<cb_cv>" : CanBo.objects.get(ten_cb=thanh_vien[0]).gioi_tinh + ": " + thanh_vien[0] + " - " + CanBo.objects.get(ten_cb=thanh_vien[0]).chuc_vu if thanh_vien else "",
            '<so_nam_ktra>' : leading_zero(request.POST['so_nam_ktra'], 10),
            '<nam_ktra>' : request.POST['nam_ktra'],
            '<so_ngay_ktra>' : f"{int(request.POST['so_ngay_ktra']):02d}",         
            '<ngay_ktra>' : "ngày " + nkt[0] + " tháng " + leading_zero(nkt[1], 3) + " năm " + nkt[2],
            '<ng_giam_sat>' : gsat.gioi_tinh.lower() + " " + ng_giam_sat,
            '<Ng_giam_sat>' : gsat.gioi_tinh + " " + ng_giam_sat,
            '<ng_giam_sat_cv>' : gsat.chuc_vu, 
            '<ld_to_trinh>' : ky_ttr.chuc_vu.upper(),
            '<ten_ld_to_trinh>' : ten_ld_to_trinh,
            '<lq_qd>' : ky_qd.chuc_vu.upper() if ky_qd.chuc_vu != 'Cục trưởng' else '',
            '<ten_ld_qd>' : ten_ld_qd,
            '<hinh_thuc_ky>' : ky_ten[ky_qd.chuc_vu.upper()],
            # '<noi_nhan>': noi_nhan[nnt.cqt],
        }
        QD = process_data.lap_qd_ktra(tt_qd, doan_ktra)
        file_path = [QD.to_trinh(), QD.qd_ktra(), QD.qd_gsat()]
        zip_path = os.path.join(settings.STATICFILES_DIRS[0], "media_store/" + tt_qd["<mst>"] + "-" + str(uuid.uuid4()) + ".zip")
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
    return render(request, 'tkt_qtr/lap_qd_ktra.html')

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
    
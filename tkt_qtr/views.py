from django.shortcuts import render
from django.http import JsonResponse, HttpResponse, Http404, HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.files.storage import FileSystemStorage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.urls import reverse
import pandas as pd

from django.contrib.auth.decorators import login_required, permission_required

from .forms import *
from . import process_data

import os
from zipfile import ZipFile
import csv
from datetime import datetime

ky_ten = {
    'PHÓ CỤC TRƯỞNG' : 'KT.CỤC TRƯỞNG',
    'CỤC TRƯỞNG': 'CỤC TRƯỞNG'
}


# Thiết lập chung
#########################################################################################
#########################################################################################
#########################################################################################
@login_required


def thiet_lap_chung(request):    
    cancu = CanCu.objects.all()
    ld_phe_duyet = LdPheDuyet.objects.all()
    context = {
        'cancu': cancu,
        'ld_phe_duyet': ld_phe_duyet
    }
    return render(request, 'tkt_qtr/thiet_lap_chung.html', context=context)

@permission_required('tkt_qtr.cancu_edit')
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

@permission_required('tkt_qtr.ld_edit')
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
    print(ld)

    return JsonResponse({'ld': ld})

def redirect_url(filename):
    if 'CB' in filename:
        return 'tkt:qly_cb'
    elif 'NNT' in filename:
        return 'tkt:dba_nnt'
    elif ('QD' in filename) | ('LD' in filename):
        return 'tkt:thiet_lap_chung'
    else:
        return 'home:base'

def import_data(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = os.path.join(settings.MEDIA_ROOT, filename)
        read_csv_setting(settings.MEDIA_ROOT, filename)
        return HttpResponseRedirect(reverse(redirect_url(filename)))
    return render(request, 'tkt_qtr/import_data.html')

def read_csv_setting(MEDIA_ROOT, filename):
    uploaded_file_url = os.path.join(MEDIA_ROOT, filename)
    # reading csv file
    with open(uploaded_file_url, 'r', encoding="utf8") as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        # extracting field names through first row
        fields = next(csvreader)
        if 'CB' in filename:
            CanBo.objects.all().delete()
            # extracting each data row one by one, then update database
            for row in csvreader:
                obj = CanBo.objects.create(
                    ten_cb = row[1],
                    gioi_tinh = row[2],
                    chuc_vu = row[3]
                )
        if 'NNT' in filename:
            NNT.objects.all().delete()
            for row in csvreader:
                obj = NNT.objects.create(
                    mst = row[1],
                    ten_nnt = row[2],
                    dia_chi = row[3],
                    cqt = row[4],
                )
        if 'QD' in filename:
            # CanCu.objects.all().delete()
            for row in csvreader:
                obj = CanCu.objects.create(
                    so_qd = row[1],
                    ten_qd = row[2],
                    ngay_qd = row[3],
                )
        if 'LD' in filename:
            LdPheDuyet.objects.all().delete()
            for row in csvreader:
                obj = LdPheDuyet.objects.create(
                    ld_ten = row[1],
                    ld_cv = row[2],
                    ld_gt = row[3],
                ) 

# Lập quyết định kiểm tra
#########################################################################################
#########################################################################################
#########################################################################################
@login_required

def lap_qd_ktra(request):
    # Căn cứ
    qd_tkt_tct = CanCu.objects.filter(ten_qd__contains='Kế hoạch thanh tra, kiểm tra năm')[0]
    luat_qlt = CanCu.objects.filter(ten_qd__contains='Luật quản lý Thuế')[0]
    quy_trinh_ktra = CanCu.objects.filter(ten_qd__contains='Quy trình thanh tra')[0]
    # Lãnh đạo phê duyệt
    ld_cuc = LdPheDuyet.objects.filter(ld_cv__contains='Cục')[0]
    ld_phong = LdPheDuyet.objects.filter(ld_cv__contains='phòng')[0]
    context = {
        'ld_cuc': ld_cuc,
        'ld_phong': ld_phong
    }
    if request.method == 'POST':
        mst = request.POST['mst']
        nnt = NNT.objects.get(mst=mst)
        # ngay_thang = request.POST['ngay_thang'].split("/")
        thang = leading_zero(request.POST['ngay_thang_1'], 3)
        nam = ngay_thang = request.POST['ngay_thang_2']
        trinh_ky =   request.POST['trinh_ky'].split("/")   
        ngay_ktra = request.POST['ngay_ktra'].split("/")  
        thanh_vien = request.POST.getlist('thanh_vien', None)
        cv = ['Trưởng đoàn']
        cv.extend(["Thành viên"] * (len(thanh_vien)-1))
        doan_ktra = {
            "<ten_cb>" : [(CanBo.objects.get(ten_cb=tv).gioi_tinh + ": " + tv) for tv in thanh_vien],
            "<ngach_cb>" : [CanBo.objects.get(ten_cb=tv).chuc_vu for tv in thanh_vien],
            "<cv_doan>" : cv
        }
        truong_doan = CanBo.objects.get(ten_cb=thanh_vien[0])
        tt_qd = { 
            '<trinh_ky>' : "ngày " + f"{int(trinh_ky[0]):02d}" + " tháng " + leading_zero(trinh_ky[1], 3) + " năm " + trinh_ky[2],
            '<ngay_thang>' : "ngày      tháng " + thang + " năm " + nam,
            '<qd_tkt_tct>': "Quyết định số " + qd_tkt_tct.so_qd,
            # '<qd_tkt_tct_ngay_ban_hanh>': qd_tkt_tct.ngay_qd.strftime(" ngày %d tháng %m") + " năm " + qd_tkt_tct.ngay_qd.strftime("%Y"),
            '<luat_qlt_ngay>': luat_qlt.ngay_qd.strftime("ngày %d tháng %m") + " năm " + luat_qlt.ngay_qd.strftime("%Y"),
            '<quy_trinh_ktra>': "Quyết định số " + quy_trinh_ktra.so_qd + quy_trinh_ktra.ngay_qd.strftime(" ngày %d tháng %m") + " năm " + quy_trinh_ktra.ngay_qd.strftime("%Y"),
            '<nam_kh_tkt>': datetime.now().strftime("%Y"),
            '<ten_dv>' : nnt.ten_nnt,# nnt(mst)['ten_nnt'],
            '<mst>' : mst,
            '<dia_chi>' : nnt.dia_chi,# nnt(mst)['dia_chi'],
            "<sl_cb>" : f"{len(thanh_vien):02d}",
            "<cb_cv>" : truong_doan.gioi_tinh.lower() + " " + thanh_vien[0] + " - " + truong_doan.chuc_vu,
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
        file_path = [QD.to_trinh(), QD.qd_ktra(), QD.qd_gsat(), QD.kh_gsat()]
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
        cb = {'chuc_vu': obj.chuc_vu, 'gioi_tinh': obj.gioi_tinh}
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

# Lập quyết định thanh tra
#########################################################################################
#########################################################################################
#########################################################################################
@login_required

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
    # Căn cứ
    qd_tkt_tct = CanCu.objects.filter(ten_qd__contains='Kế hoạch thanh tra, kiểm tra năm')[0]
    luat_qlt = CanCu.objects.filter(ten_qd__contains='Luật quản lý Thuế')[0]
    luat_ttra = CanCu.objects.filter(ten_qd__contains='Luật Thanh tra')[0]
    quy_trinh_ttra = CanCu.objects.filter(ten_qd__contains='Quy trình thanh tra')[0]
    bsung_qtrinh_ttra = CanCu.objects.filter(ten_qd__contains='Sửa đổi, bổ sung quy trình thanh tra')[0]
    # Lãnh đạo phê duyệt
    ld_cuc = LdPheDuyet.objects.filter(ld_cv__contains='Cục')[0]
    ld_phong = LdPheDuyet.objects.filter(ld_cv__contains='phòng')[0]
    context = {
        'ld_cuc': ld_cuc,
        'ld_phong': ld_phong
    }
    if request.method == 'POST':
        mst = request.POST['mst']
        nnt = NNT.objects.get(mst=mst)
        thang = leading_zero(request.POST['ngay_thang_1'], 3)
        nam = ngay_thang = request.POST['ngay_thang_2']
        trinh_ky =   request.POST['trinh_ky'].split("/")
        ngay_ktra = request.POST['ngay_ktra'].split("/")
        thanh_vien = request.POST.getlist('thanh_vien', None)
        cv = ['Trưởng đoàn']
        cv.extend(["Thành viên"] * (len(thanh_vien)-1))
        truong_doan = CanBo.objects.get(ten_cb=thanh_vien[0])
        doan_ttra = {
            "<ten_cb>" : [(CanBo.objects.get(ten_cb=tv).gioi_tinh + ": " + tv) for tv in thanh_vien],
            "<ngach_cb>" : [CanBo.objects.get(ten_cb=tv).chuc_vu for tv in thanh_vien],
            "<cv_doan>" : cv
        }
        tt_qd = { 
            '<trinh_ky>' : "ngày " + f"{int(trinh_ky[0]):02d}" + " tháng " + leading_zero(trinh_ky[1], 3) + " năm " + trinh_ky[2],
            '<qd_tkt_tct>': "Quyết định số " + qd_tkt_tct.so_qd,
            '<qd_tkt_tct_ngay_ban_hanh>': qd_tkt_tct.ngay_qd.strftime("ngày %d tháng %m") + " năm " + qd_tkt_tct.ngay_qd.strftime("%Y"),
            '<nam_kh_tkt>': datetime.now().strftime("%Y"),
            '<quy_trinh_ttra>': "Quyết định số " + quy_trinh_ttra.so_qd + quy_trinh_ttra.ngay_qd.strftime(" ngày %d tháng %m") + " năm " + quy_trinh_ttra.ngay_qd.strftime("%Y"),
            '<quy_trinh_ttra_rut_gon>': "Quyết định số " + quy_trinh_ttra.so_qd + quy_trinh_ttra.ngay_qd.strftime(" ngày %d/%m/%Y"),
            '<bsung_qtrinh_ttra>': "Quyết định số " + bsung_qtrinh_ttra.so_qd + bsung_qtrinh_ttra.ngay_qd.strftime(" ngày %d tháng %m") + " năm " + bsung_qtrinh_ttra.ngay_qd.strftime("%Y"),
            '<bsung_qtrinh_ttra_rut_gon>': "Quyết định số " + bsung_qtrinh_ttra.so_qd + bsung_qtrinh_ttra.ngay_qd.strftime(" ngày %d/%m/%Y"),
            '<luat_qlt_ngay>': luat_qlt.ngay_qd.strftime("ngày %d tháng %m") + " năm " + luat_qlt.ngay_qd.strftime("%Y"),
            '<luat_ttra>': luat_ttra.ngay_qd.strftime("ngày %d tháng %m") + " năm " + luat_ttra.ngay_qd.strftime("%Y"),
            '<ngay_thang>' : "ngày      tháng " + thang + " năm " + nam,
            '<ten_dv>' : nnt.ten_nnt,# nnt(mst)['ten_nnt'],
            '<mst>' : mst,
            '<dia_chi>' : nnt.dia_chi,# nnt(mst)['dia_chi'],
            "<sl_cb>" : f"{len(thanh_vien):02d}",
            '<truong_doan_ttr>': thanh_vien[0],
            "<cb_cv>" : truong_doan.gioi_tinh.lower() + " " + thanh_vien[0] + " - " + truong_doan.chuc_vu,
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

# Lập quyết định kiểm tra trước hoàn thuế GTGT
#########################################################################################
#########################################################################################
#########################################################################################
@login_required

def lap_qd_ktra_trc_hoan(request):
    # Căn cứ
    qd_tkt_tct = CanCu.objects.filter(ten_qd__contains='Kế hoạch thanh tra, kiểm tra năm')[0]
    luat_qlt = CanCu.objects.filter(ten_qd__contains='Luật quản lý Thuế')[0]
    # Lãnh đạo phê duyệt
    ld_cuc = LdPheDuyet.objects.filter(ld_cv__contains='Cục')[0]
    ld_phong = LdPheDuyet.objects.filter(ld_cv__contains='phòng')[0]
    context = {
        'ld_cuc': ld_cuc,
        'ld_phong': ld_phong
    }
    if request.method == 'POST':
        mst = request.POST['mst']
        nnt = NNT.objects.get(mst=mst)
        thang = leading_zero(request.POST['ngay_thang_1'], 3)
        nam = ngay_thang = request.POST['ngay_thang_2']
        trinh_ky =   request.POST['trinh_ky'].split("/")
        ngay_ktra = request.POST['ngay_ktra'].split("/")
        thanh_vien = request.POST.getlist('thanh_vien', None)
        kk_theo = request.POST['kk_theo']
        tgian = request.POST.getlist('tgian', None)
        cv = ['Trưởng đoàn']
        cv.extend(["Thành viên"] * (len(thanh_vien)-1))
        truong_doan = CanBo.objects.get(ten_cb=thanh_vien[0])
        doan_ktra = {
            "<ten_cb>" : [(CanBo.objects.get(ten_cb=tv).gioi_tinh + ": " + tv) for tv in thanh_vien],
            "<cv_cb>" : [CanBo.objects.get(ten_cb=tv).chuc_vu for tv in thanh_vien],
            "<cv_doan>" : cv
        }
        tt_qd = { 
            '<trinh_ky>' : "ngày " + f"{int(trinh_ky[0]):02d}" + " tháng " + leading_zero(trinh_ky[1], 3) + " năm " + trinh_ky[2],
            '<luat_qlt_ngay>': luat_qlt.ngay_qd.strftime("ngày %d tháng %m") + " năm " + luat_qlt.ngay_qd.strftime("%Y"),
            '<ngay_thang>' : "ngày      tháng " + thang + " năm " + nam,
            '<hs_hoan_so>' : request.POST['hs_hoan_so'],
            '<hs_hoan_ngay>' : request.POST['hs_hoan_ngay'],
            '<ky_hoan_thue>' : kk_theo + " " + tgian[0] + " đến " + kk_theo + " " + tgian[1],
            '<hoan_tien>' : request.POST['hoan_tien'],
            '<th_hoan>': request.POST['th_hoan'],
            '<dia_diem_ktra>' : request.POST['dia_diem_ktra'],
            '<ten_dv>' : nnt.ten_nnt,
            '<mst>' : mst,
            '<dia_chi>' : nnt.dia_chi,
            "<sl_cb>" : f"{len(thanh_vien):02d}",
            "<cb_cv>" : truong_doan.gioi_tinh.lower() + " " + thanh_vien[0] + " - " + truong_doan.chuc_vu,
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
        }       
        QD = process_data.lap_qd_ktra_hoan_gtgt(tt_qd, doan_ktra)
        QD.empty_media()
        file_path = [QD.to_trinh(), QD.qd_ktra(), QD.qd_gsat(), QD.kh_gsat()]
        zip_path = os.path.join(settings.STATICFILES_DIRS[0], "media_store", mst + "_QD_ktra_hoan_gtgt.zip")
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
    return render(request, 'tkt_qtr/lap_qd_ktra_trc_hoan.html', context=context)

# Lập quyết định kiểm tra giải thể
#########################################################################################
#########################################################################################
#########################################################################################
@login_required

def lap_qd_ktra_giai_the(request):
    # Căn cứ
    qd_tkt_tct = CanCu.objects.filter(ten_qd__contains='Kế hoạch thanh tra, kiểm tra năm')[0]
    luat_qlt = CanCu.objects.filter(ten_qd__contains='Luật quản lý Thuế')[0]
    quy_trinh_ktra = CanCu.objects.filter(ten_qd__contains='Phê duyệt quy trình kiểm tra')[0]
    # Lãnh đạo phê duyệt
    ld_cuc = LdPheDuyet.objects.filter(ld_cv__contains='Cục')[0]
    ld_phong = LdPheDuyet.objects.filter(ld_cv__contains='phòng')[0]
    context = {
        'ld_cuc': ld_cuc,
        'ld_phong': ld_phong
    }
    if request.method == 'POST':
        mst = request.POST['mst']
        nnt = NNT.objects.get(mst=mst)
        thang = leading_zero(request.POST['ngay_thang_1'], 3)
        nam = ngay_thang = request.POST['ngay_thang_2']
        trinh_ky =   request.POST['trinh_ky'].split("/")
        ngay_ktra = request.POST['ngay_ktra'].split("/")
        thanh_vien = request.POST.getlist('thanh_vien', None)
        cv = ['Trưởng đoàn']
        cv.extend(["Thành viên"] * (len(thanh_vien)-1))
        truong_doan = CanBo.objects.get(ten_cb=thanh_vien[0])
        doan_ktra = {
            "<ten_cb>" : [(CanBo.objects.get(ten_cb=tv).gioi_tinh + ": " + tv) for tv in thanh_vien],
            "<cv_cb>" : [CanBo.objects.get(ten_cb=tv).chuc_vu for tv in thanh_vien],
            "<cv_doan>" : cv
        }
        tt_qd = { 
            '<trinh_ky>' : "ngày " + f"{int(trinh_ky[0]):02d}" + " tháng " + leading_zero(trinh_ky[1], 3) + " năm " + trinh_ky[2],
            '<luat_qlt_ngay>': luat_qlt.ngay_qd.strftime("ngày %d tháng %m") + " năm " + luat_qlt.ngay_qd.strftime("%Y"),
            '<quy_trinh_ktra>': "Quyết định số " + quy_trinh_ktra.so_qd + quy_trinh_ktra.ngay_qd.strftime(" ngày %d/%m/%Y"),
            '<ngay_thang>' : "ngày      tháng " + thang + " năm " + nam,
            "<phieu_xly_ngay>": request.POST['phieu_xly_ngay'],
            '<ten_dv>' : nnt.ten_nnt,
            '<mst>' : mst,
            '<dia_chi>' : nnt.dia_chi,
            '<nam_ktra>' : request.POST['nam_ktra'],
            "<sl_cb>" : f"{len(thanh_vien):02d}",
            "<cb_cv>" : truong_doan.gioi_tinh.lower() + " " + thanh_vien[0] + " - " + truong_doan.chuc_vu,
            '<so_ngay_ktra>' : f"{int(request.POST['so_ngay_ktra']):02d}",         
            '<ngay_ktra>' : "ngày " + ngay_ktra[0] + " tháng " + leading_zero(ngay_ktra[1], 3) + " năm " + ngay_ktra[2],
            '<dia_diem_ktra>': request.POST['dia_diem_ktra'],
            '<ng_giam_sat>' : ld_phong.ld_gt.lower() + " " + ld_phong.ld_ten,
            '<Ng_giam_sat>' : ld_phong.ld_gt + " " + ld_phong.ld_ten,
            '<ng_giam_sat_cv>' : ld_phong.ld_cv, 
            '<LD_PHONG>' : ld_phong.ld_cv.upper(),
            '<ld_phong>' : ld_phong.ld_cv,
            '<ld_phong_ten>' : ld_phong.ld_ten,
            '<LD_CUC>' : ld_cuc.ld_cv.upper() if ld_cuc.ld_cv != 'Cục trưởng' else '',
            '<ld_cuc_ten>' : ld_cuc.ld_ten,
            '<hinh_thuc_ky>' : ky_ten[ld_cuc.ld_cv.upper()],
        }       
        QD = process_data.lap_qd_ktra_giai_the(tt_qd, doan_ktra)
        QD.empty_media()
        file_path = [QD.to_trinh(), QD.qd_ktra(), QD.qd_gsat(), QD.kh_gsat()]
        zip_path = os.path.join(settings.STATICFILES_DIRS[0], "media_store", mst + "_QD_ktra_giai_the.zip")
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
    return render(request, 'tkt_qtr/lap_qd_ktra_giai_the.html', context=context)

# Lập quyết định kiểm tra đột xuất
#########################################################################################
#########################################################################################
#########################################################################################
@login_required

def lap_qd_ktra_dot_xuat(request):
    # Căn cứ
    qd_tkt_tct = CanCu.objects.filter(ten_qd__contains='Kế hoạch thanh tra, kiểm tra năm')[0]
    luat_qlt = CanCu.objects.filter(ten_qd__contains='Luật quản lý Thuế')[0]
    quy_trinh_ktra = CanCu.objects.filter(ten_qd__contains='Phê duyệt quy trình kiểm tra')[0]
    # Lãnh đạo phê duyệt
    ld_cuc = LdPheDuyet.objects.filter(ld_cv__contains='Cục')[0]
    ld_phong = LdPheDuyet.objects.filter(ld_cv__contains='phòng')[0]
    context = {
        'ld_cuc': ld_cuc,
        'ld_phong': ld_phong
    }
    if request.method == 'POST':
        mst = request.POST['mst']
        nnt = NNT.objects.get(mst=mst)
        # ngay_thang = request.POST['ngay_thang'].split("/")
        thang = leading_zero(request.POST['ngay_thang_1'], 3)
        nam = ngay_thang = request.POST['ngay_thang_2']
        trinh_ky =   request.POST['trinh_ky'].split("/")   
        ngay_ktra = request.POST['ngay_ktra'].split("/")  
        thanh_vien = request.POST.getlist('thanh_vien', None)
        cv = ['Trưởng đoàn']
        cv.extend(["Thành viên"] * (len(thanh_vien)-1))
        doan_ktra = {
            "<ten_cb>" : [(CanBo.objects.get(ten_cb=tv).gioi_tinh + ": " + tv) for tv in thanh_vien],
            "<ngach_cb>" : [CanBo.objects.get(ten_cb=tv).chuc_vu for tv in thanh_vien],
            "<cv_doan>" : cv
        }
        truong_doan = CanBo.objects.get(ten_cb=thanh_vien[0])
        tt_qd = { 
            '<trinh_ky>' : "ngày " + f"{int(trinh_ky[0]):02d}" + " tháng " + leading_zero(trinh_ky[1], 3) + " năm " + trinh_ky[2],
            '<can_cu>': request.POST['can_cu'],
            '<ngay_thang>' : "ngày      tháng " + thang + " năm " + nam,
            '<qd_tkt_tct>': "Quyết định số " + qd_tkt_tct.so_qd,
            '<luat_qlt_ngay>': luat_qlt.ngay_qd.strftime("ngày %d tháng %m") + " năm " + luat_qlt.ngay_qd.strftime("%Y"),
            '<quy_trinh_ktra>': "Quyết định số " + quy_trinh_ktra.so_qd + quy_trinh_ktra.ngay_qd.strftime(" ngày %d tháng %m") + " năm " + quy_trinh_ktra.ngay_qd.strftime("%Y"),
            '<nam_kh_tkt>': datetime.now().strftime("%Y"),
            '<ten_dv>' : nnt.ten_nnt,# nnt(mst)['ten_nnt'],
            '<mst>' : mst,
            '<dia_chi>' : nnt.dia_chi,# nnt(mst)['dia_chi'],
            "<sl_cb>" : f"{len(thanh_vien):02d}",
            "<cb_cv>" : truong_doan.gioi_tinh.lower() + " " + thanh_vien[0] + " - " + truong_doan.chuc_vu,
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
        QD = process_data.lap_qd_ktra_dot_xuat(tt_qd, doan_ktra)
        QD.empty_media()
        file_path = [QD.to_trinh(), QD.qd_ktra(), QD.qd_gsat(), QD.kh_gsat()]
        zip_path = os.path.join(settings.STATICFILES_DIRS[0], "media_store", mst + "_QD_ktra_dot_xuat.zip")
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
    return render(request, 'tkt_qtr/lap_qd_ktra_dot_xuat.html', context=context)

# Lập quyết định thanh tra đột xuất
#########################################################################################
#########################################################################################
#########################################################################################
@login_required

def lap_qd_ttra_dot_xuat(request):
    noi_nhan = {
        'Cục Thuế tỉnh Quảng Trị': 'Phòng KK&KTT',
        'CCT KV Đông Hà - Cam Lộ': 'CCT KV Đông Hà - Cam Lộ',
        'CCT KV Triệu Hải': 'CCT KV Triệu Hải',
        'CCT KV Vĩnh Linh - Gio Linh': 'CCT KV Vĩnh Linh - Gio Linh',
        'CCT huyện Đakrông': 'CCT huyện Đakrông',
        'CCT huyện Hướng Hóa': 'CCT huyện Hướng Hóa',
        'CCT huyện Cồn Cỏ': 'CCT huyện Cồn Cỏ'
    }
    # Căn cứ
    qd_tkt_tct = CanCu.objects.filter(ten_qd__contains='Kế hoạch thanh tra, kiểm tra năm')[0]
    luat_qlt = CanCu.objects.filter(ten_qd__contains='Luật quản lý Thuế')[0]
    luat_ttra = CanCu.objects.filter(ten_qd__contains='Luật Thanh tra')[0]
    quy_trinh_ttra = CanCu.objects.filter(ten_qd__contains='Quy trình thanh tra')[0]
    bsung_qtrinh_ttra = CanCu.objects.filter(ten_qd__contains='Sửa đổi, bổ sung quy trình thanh tra')[0]
    # Lãnh đạo phê duyệt
    ld_cuc = LdPheDuyet.objects.filter(ld_cv__contains='Cục')[0]
    ld_phong = LdPheDuyet.objects.filter(ld_cv__contains='phòng')[0]
    context = {
        'ld_cuc': ld_cuc,
        'ld_phong': ld_phong
    }
    if request.method == 'POST':
        mst = request.POST['mst']
        nnt = NNT.objects.get(mst=mst)
        thang = leading_zero(request.POST['ngay_thang_1'], 3)
        nam = ngay_thang = request.POST['ngay_thang_2']
        trinh_ky =   request.POST['trinh_ky'].split("/")
        ngay_ktra = request.POST['ngay_ktra'].split("/")
        thanh_vien = request.POST.getlist('thanh_vien', None)
        cv = ['Trưởng đoàn']
        cv.extend(["Thành viên"] * (len(thanh_vien)-1))
        truong_doan = CanBo.objects.get(ten_cb=thanh_vien[0])
        doan_ttra = {
            "<ten_cb>" : [(CanBo.objects.get(ten_cb=tv).gioi_tinh + ": " + tv) for tv in thanh_vien],
            "<ngach_cb>" : [CanBo.objects.get(ten_cb=tv).chuc_vu for tv in thanh_vien],
            "<cv_doan>" : cv
        }
        tt_qd = { 
            '<trinh_ky>' : "ngày " + f"{int(trinh_ky[0]):02d}" + " tháng " + leading_zero(trinh_ky[1], 3) + " năm " + trinh_ky[2],
            '<can_cu>': request.POST['can_cu'],
            '<qd_tkt_tct>': "Quyết định số " + qd_tkt_tct.so_qd,
            '<qd_tkt_tct_ngay_ban_hanh>': qd_tkt_tct.ngay_qd.strftime("ngày %d tháng %m") + " năm " + qd_tkt_tct.ngay_qd.strftime("%Y"),
            '<nam_kh_tkt>': datetime.now().strftime("%Y"),
            '<quy_trinh_ttra>': "Quyết định số " + quy_trinh_ttra.so_qd + quy_trinh_ttra.ngay_qd.strftime(" ngày %d tháng %m") + " năm " + quy_trinh_ttra.ngay_qd.strftime("%Y"),
            '<quy_trinh_ttra_rut_gon>': "Quyết định số " + quy_trinh_ttra.so_qd + quy_trinh_ttra.ngay_qd.strftime(" ngày %d/%m/%Y"),
            '<bsung_qtrinh_ttra>': "Quyết định số " + bsung_qtrinh_ttra.so_qd + bsung_qtrinh_ttra.ngay_qd.strftime(" ngày %d tháng %m") + " năm " + bsung_qtrinh_ttra.ngay_qd.strftime("%Y"),
            '<bsung_qtrinh_ttra_rut_gon>': "Quyết định số " + bsung_qtrinh_ttra.so_qd + bsung_qtrinh_ttra.ngay_qd.strftime(" ngày %d/%m/%Y"),
            '<luat_qlt_ngay>': luat_qlt.ngay_qd.strftime("ngày %d tháng %m") + " năm " + luat_qlt.ngay_qd.strftime("%Y"),
            '<luat_ttra>': luat_ttra.ngay_qd.strftime("ngày %d tháng %m") + " năm " + luat_ttra.ngay_qd.strftime("%Y"),
            '<ngay_thang>' : "ngày      tháng " + thang + " năm " + nam,
            '<ten_dv>' : nnt.ten_nnt,# nnt(mst)['ten_nnt'],
            '<mst>' : mst,
            '<dia_chi>' : nnt.dia_chi,# nnt(mst)['dia_chi'],
            "<sl_cb>" : f"{len(thanh_vien):02d}",
            '<truong_doan_ttr>': thanh_vien[0],
            "<cb_cv>" : truong_doan.gioi_tinh.lower() + " " + thanh_vien[0] + " - " + truong_doan.chuc_vu,
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
        QD = process_data.lap_qd_ttra_dot_xuat(tt_qd, doan_ttra)
        QD.empty_media()
        file_path = [QD.to_trinh(), QD.qd_ttra(), QD.kh_ttra(), QD.qd_gsat(), QD.kh_gsat()]
        zip_path = os.path.join(settings.STATICFILES_DIRS[0], "media_store", mst + "_QD_ttra_dot_xuat.zip")
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
    
    return render(request, 'tkt_qtr/lap_qd_ttra_dot_xuat.html', context=context)

# Quản lý cán bộ
#########################################################################################
#########################################################################################
#########################################################################################
@login_required

# @permission_required('tkt.canbo_view', raise_exception=True)
def qly_cb(request):
    can_bo = CanBo.objects.all()
    page = request.GET.get('page', 1)

    paginator = Paginator(can_bo, 10)

    try:
        can_bo = paginator.page(page)
    except PageNotAnInteger:
        can_bo = paginator.page(1)
    except EmptyPage:
        can_bo = paginator.page(paginator.num_pages)

    return render(request, 'tkt_qtr/qly_cb.html', {'can_bo': can_bo})

@permission_required('tkt_qtr.canbo_add')
def them_moi_cb(request):
    gioi_tinh_1 = request.GET.get('gioi_tinh', None)
    ten_cb_1 = request.GET.get('ten_cb', None)
    chuc_vu_1 = request.GET.get('chuc_vu', None)

    obj = CanBo.objects.create(
        gioi_tinh = gioi_tinh_1,
        ten_cb = ten_cb_1,
        chuc_vu = chuc_vu_1,
    )

    user = {'id': obj.id, 'ten_cb': obj.ten_cb, 'gioi_tinh': obj.gioi_tinh, 'chuc_vu': obj.chuc_vu}

    return JsonResponse({'user': user})

@permission_required('tkt_qtr.canbo_edit')
def cap_nhat_thong_tin(request):
    id_1 = request.GET.get('id', None)
    gioi_tinh_1 = request.GET.get('gioi_tinh', None)
    ten_cb_1 = request.GET.get('ten_cb', None)
    chuc_vu_1 = request.GET.get('chuc_vu', None)

    obj = CanBo.objects.get(id=id_1)
    obj.ten_cb = ten_cb_1
    obj.gioi_tinh = gioi_tinh_1
    obj.chuc_vu = chuc_vu_1
    obj.save()

    user = {'id': obj.id, 'ten_cb': obj.ten_cb, 'gioi_tinh': obj.gioi_tinh, 'chuc_vu': obj.chuc_vu}

    return JsonResponse({'user': user})

@permission_required('tkt_qtr.canbo_delete')
def xoa_cb(request):
    id_1 = request.GET.get('id', None)
    CanBo.objects.get(id=id_1).delete()
    return JsonResponse({'delete': True})

# Danh bạ NNT
#########################################################################################
#########################################################################################
#########################################################################################
@login_required

def dba_nnt(request):
    dba = NNT.objects.all()

    return render(request, 'tkt_qtr/dba_nnt.html', {'dba': dba})

@permission_required('tkt_qtr.nnt_add')
def them_moi_nnt(request):
    mst_1 = request.GET.get('mst', None)
    try:
        search = NNT.objects.get(mst=mst_1)
    except ObjectDoesNotExist:
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
    else:
        return JsonResponse({})

@permission_required('tkt_qtr.nnt_edit')
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

@permission_required('tkt_qtr.nnt_delete')
def xoa_nnt(request):
    id_1 = request.GET.get('id', None)
    NNT.objects.get(id=id_1).delete()
    data = {'delete': True}

    return JsonResponse(data)

def upload_nnt(request):
    errors = []
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = os.path.join(settings.MEDIA_ROOT, filename)

        df = pd.read_excel(uploaded_file_url, converters={'Mã số thuế':str})
        for row in range(df.shape[0]):
            if pd.isnull(df.iloc[row, :]).any():
                errors.append(f"Điền đầy đủ thông tin NNT tại dòng dữ liệu thứ {row+1}")
        if errors:
            return render(request, 'tkt_qtr/upload_nnt.html', {'errors':errors})
        else:
            mst_exist = []
            for row in range(df.shape[0]):
                mst = df.iloc[row]['Mã số thuế']
                try:
                    search = NNT.objects.get(mst=mst)
                except ObjectDoesNotExist:
                    obj = NNT.objects.create(
                        mst = mst,
                        ten_nnt = df.iloc[row]['Tên NNT'],
                        dia_chi = df.iloc[row]['Địa chỉ'],
                        cqt = df.iloc[row]['CQT quản lý']
                    )
                    # print(mst)
                else:
                    mst_exist.append(mst)
            if mst_exist:
                return render(request, 'tkt_qtr/upload_nnt.html', {'mst_exist':mst_exist})
            else:
                return HttpResponseRedirect(reverse('tkt:dba_nnt'))
    return render(request, 'tkt_qtr/upload_nnt.html')


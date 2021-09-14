import os
import pandas as pd
import json
from datetime import datetime
import time

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.http import Http404

from . import xmhd, kt_npt
from . import process_data
# Create your views here.
def index(request):
    return render(request, 'apps/base.html')

def upload_file_url(myfile):
    fs = FileSystemStorage()
    filename = fs.save(myfile.name, myfile)
    uploaded_file_url = os.path.join(settings.MEDIA_ROOT, filename)
    return uploaded_file_url
    
################################# ỨNG DỤNG LẬP PHIẾU XÁC MINH HÓA ĐƠN #################################
# Mô tả ứng dụng:Cán bộ lập bảng kê hóa đơn cần xác minh theo mẫu cho sẵn, ứng dụng kết xuất theo mẫu #
# xác minh hóa đơn theo từng đơn vị                                                                   #
# Thời gian hoàn thành: 3/2020                                                                        #
# Thời gian triển khai: 6/2021                                                                        #
# Nhóm tác giả: Nguyễn Đăng Nhật Tâm, ?, ?                                #
#######################################################################################################

def xmhd_upload(request):
    if request.method == 'POST' and request.FILES['myfile']:
        myfile = request.FILES['myfile']
        """ fs = FileSystemStorage()
        filename = fs.save(myfile.name, myfile)
        uploaded_file_url = os.path.join(settings.MEDIA_ROOT, filename)
        request.session['uploaded_file_url'] = uploaded_file_url """
        request.session['uploaded_file_url'] = upload_file_url(myfile)
        errors = process_data.xmhd(request.session['uploaded_file_url']).check_data_valid()
        if errors == True:
            return HttpResponseRedirect(reverse('apps:xmhd_index'))
        else:
            return render(request, 'apps/xmhd_upload.html', {'errors':errors})   
    return render(request, 'apps/xmhd_upload.html')

def xmhd_index(request):
    uploaded_file_url = request.session['uploaded_file_url']
    index = process_data.xmhd(uploaded_file_url)
    grp = index.grp_data()
    dvmh = index.dvmh()
    dvbh = {}
    for k, v in grp:
        v = v.sort_values(by='ngay').reset_index(drop=True)
        for i in range(len(v)):
            # Convert datetime to string => do to_join đã đổi datime thành miliseconds
            v.ngay[i] = v.ngay[i].strftime("%d/%m/%Y")  
            # Định dạng số với dấu chấm (format number with commas)
            v.doanh_so[i] = "{:,}".format(v.doanh_so[i]).replace(",",".")
            if pd.isnull(v.mau[i]):
                v.mau[i] = ''
        # convert dataframe to html table
        json_records = v.to_json(orient ='records')
        data = [] 
        data = json.loads(json_records) 
        dvbh.update({k: data})
    if request.method == 'POST':
        kyten = {
            'cbxm': request.POST['cbxm'].title(),
            'tp': request.POST['tp'].title(),
            'lanhdao': request.POST['lanhdao']
            }
        download_file_url = index.export_excel(kyten=kyten, grp=grp, dvmh=dvmh)
        # Full path of file
        if os.path.exists(download_file_url):
            with open(download_file_url, 'rb') as fh:
                response = HttpResponse(fh.read(), content_type="application/force_download")
                response['Content-Disposition'] = 'inline; filename=' + os.path.basename(download_file_url)
                return response
        # If file is not exists
        raise Http404
    return render(request, 'apps/xmhd_index.html', {
        'dvmh': dvmh,
        'dvbh': dvbh,
        })

############################# ỨNG DỤNG KIỂM TRA THÔNG TIN NGƯỜI PHỤ THUỘC #############################
# Mô tả ứng dụng:Từ thông tin PL03 tờ khai QTT của tổ chức, ứng dụng kiểm tra, đối chiếu thông tin về #
# MST ngày sinh, mối quan hệ với NNT và thời gian đăng ký giảm trừ gia cảnh giữa tờ khai của đơn vị   #
# với dữ liệu hệ thống TMS                                                                            #
# Thời gian thực hiện: 5/2020                                                                         #
# Thời gian triển khai: 6/2020                                                                        #
# Nhóm tác giả: Nguyễn Đăng Nhật Tâm, Hoàng Anh Như Ngọc, Trần Kim Chi                                #
#######################################################################################################

def ktnpt_upload(request):
    if request.method == 'POST' and request.FILES['myfile1'] and request.FILES['myfile2']:
        # save upload excel file
        myfile1 = request.FILES['myfile1']
        request.session['uploaded_file_url_1'] = upload_file_url(myfile1)
        
        # save upload xml file
        myfile2 = request.FILES['myfile2']
        request.session['uploaded_file_url_2'] = upload_file_url(myfile2)
        # print(request.session['uploaded_file_url_1']) # xml file
        # print(request.session['uploaded_file_url_2']) #exxcel file
        # return HttpResponseRedirect(reverse('apps:ktnpt_result'))
        errors = process_data.kt_npt([request.session['uploaded_file_url_1'],request.session['uploaded_file_url_2']]).ktra_cqt()
        if errors == True:
            return HttpResponseRedirect(reverse('apps:ktnpt_result'))
        else:
            return render(request, 'apps/ktnpt_upload.html', {'errors':errors}) 
    return render(request, 'apps/ktnpt_upload.html')

def ktnpt_result(request):
    path = []
    path.append(request.session['uploaded_file_url_1'])
    path.append(request.session['uploaded_file_url_2'])
    compare = process_data.kt_npt(path)
    result = compare.kq_ktra()

    result['birth_date'] = result['birth_date'].dt.strftime('%d/%m/%Y')
    result['month_start'] = result['month_start'].dt.strftime('%m/%Y')
    result['month_end'] = result['month_end'].dt.strftime('%m/%Y')
    # convert dataframe to html table
    json_records = result.reset_index().to_json(orient ='records')
    data = []
    data = json.loads(json_records)
    context = {'d': data}
    # Cơ quan chi trả
    cqct = compare.thong_tin_cqct()
    return render(request, 'apps/ktnpt_result.html', {'context': context, 'cqct': cqct})
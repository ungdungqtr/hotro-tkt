from django.conf import settings
import os
import pandas as pd
import xlsxwriter
import datetime
import uuid
from pathlib import Path

# Xu lu du lieu
#path = 'D:\\python\\XMHD\\XMHD.xlsx'

header = ['mau', 'ky_hieu', 'so', 'ngay', 'ten', 'mst', 'doanh_so', 'thue_suat', 'thue_gtgt']
#raw_data = pd.read_excel(path, sheet_name='Sheet1', converter={'mst': str})
ct = 'CỤC THUẾ TỈNH QUẢNG TRỊ'
xmac = 'PHIẾU YÊU CẦU XÁC MINH NỘI DUNG KINH TẾ CỦA ẤN CHỈ'
x = datetime.datetime.now()
location = 'Quảng Trị, ngày ' + \
            x.strftime("%d") + ' tháng ' + x.strftime("%m") + \
            ' năm ' + x.strftime("%Y")
"""path = os.path.join(os.path.abspath(os.getcwd()),
                    '\\app\\static\\xlsx\\chi tiet.xlsx')"""


class process_data:
    def __init__(self, path):
        self.path = path
        # self.raw_data = pd.read_excel(self.path, sheet_name='BangKeHD', converter={'mst': str})
        self.raw_data = pd.read_excel(self.path, sheet_name='BangKeHD')
        data = self.raw_data.iloc[7:, 1:10]
        data.columns = header
        self.data = data.reset_index(drop=True)    

    def check_data_valid(self):
        data = self.data
        errors = []
        if pd.isnull(self.raw_data.iloc[0, 2]) or pd.isnull(self.raw_data.iloc[1, 2]):
            errors.append('Thiếu thông tin MST và Tên đơn vị mua hàng')
        for row in range(data.shape[0]):
            if pd.isnull(data.iloc[row, 1:]).any():
                errors.append(f"Điền đầy đủ thông tin tại dòng dữ liệu thứ {row+1} của Bảng kê hóa đơn")
            if not pd.isnull(data['ngay'][row]):
                if not isinstance(data['ngay'][row], datetime.datetime):
                    errors.append(f"Kiểm tra định dạng ngày tháng tại dòng dữ liệu thứ {row+1} của Bảng kê hóa đơn")
                # try:
                    # data['ngay'][row] = datetime.datetime.strptime(data['ngay'][row], '%d/%m/%Y')
                # except ValueError or TypeError: 
                    # errors.append(f"Vui lòng kiểm tra định dạng ngày tháng tại dòng dữ liệu thứ {row+1} của Bảng kê hóa đơn")
        return errors if errors else True

    def dvmh(self):
        raw_data = self.raw_data
        ten_dv_mua = raw_data.iloc[0, 2]
        mst_dv_mua = raw_data.iloc[1, 2]
        return {'ten_dv_mua': ten_dv_mua, 'mst_dv_mua': mst_dv_mua}
        
    def grp_data(self):
        data = self.data
        data['mst'] = data['mst'].astype(str)
        return data.groupby(['mst'])

    def export_excel(self, kyten, grp, dvmh):
        sending_path = settings.MEDIA_ROOT
        line = os.path.join(settings.STATICFILES_DIRS[0], 'images\line.png')
        filename = 'Phieu-xmhd-' + str(uuid.uuid4()) + '.xlsx'
        
        wb = xlsxwriter.Workbook(os.path.join(sending_path, filename), {'string_to_number': True})
        row = 11
        col = 0
        font_name = 'Times New Roman'
        font_size = 10
        date_format = wb.add_format({'num_format': 'dd/mm/yyyy', 'font': font_name, 'size': font_size,
                                     'valign': 'vcenter', 'align': 'center', 'border': 1
                                     })
        num_format = wb.add_format({'num_format': '#,##0', 'font': font_name, 'size': font_size,
                                    'valign': 'vcenter', 'align': 'center', 'border': 1
                                    })
        tct_format = wb.add_format({'font': font_name, 'size': 12, 'align': 'center'
                                    })
        ct_format = wb.add_format({'font': font_name, 'size': 13, 'align': 'center', 'bold': True
                                   })
        chxh_format = wb.add_format({'font': font_name, 'size': 12, 'align': 'center', 'bold': True
                                     })
        phieu_xm_format = wb.add_format({'font': font_name, 'size': 14, 'align': 'center', 'bold': True
                                         })
        bang_format = wb.add_format({'font': font_name, 'size': 10, 'border': 1, 'text_wrap': True,
                                     'valign': 'vcenter', 'align': 'center'
                                     })
        bang_format_1 = wb.add_format({'font': font_name, 'size': 10, 'border': 1, 'text_wrap': True,
                                       'valign': 'vcenter'
                                       })
        dv_format = wb.add_format({'font': font_name, 'size': 13
                                   })
        header_format = wb.add_format({'font': font_name, 'size': 10, 'border': 1, 'bold': True,
                                       'valign': 'vcenter', 'align': 'center', 'text_wrap': True
                                       })
        qtri_format = wb.add_format({'font': font_name, 'size': 13, 'italic': True, 'align': 'center'
                                     })
        sign_format = wb.add_format({'font': font_name, 'size': 13, 'bold': True, 'align': 'center'
                                     })

        for k, v in grp:
            # row = row + 11
            v = v.sort_values(by='ngay').reset_index(drop=True)

            ten_dv_ban = v['ten'].to_list()[0]
            #l = len(v['ten'].to_list())
            # SHEET FORMAT
            ws = wb.add_worksheet(k)
            ws.set_column(0, 0, 5)      # Số TT
            ws.set_column(1, 1, 10.5)   # Ký hiệu mẫu ấn chỉ
            ws.set_column(2, 2, 8.5)    # Ký hiệu hóa đơn
            ws.set_column(3, 3, 6)      # Hóa đơn số
            ws.set_column(4, 4, 35)     # Đơn vị bán hàng
            ws.set_column(5, 5, 12.5)   # Mã số thuế
            ws.set_column(6, 6, 9)      # Số tiền thuế GTGT
            ws.set_column(7, 7, 8.5)    # Ngày lập hóa đơn
            ws.set_column(8, 8, 7)      # Đơn vị mua hàng
            ws.set_column(10, 10, 7)    # Số tiền thuế GTGT
            ws.set_column(12, 12, 5)    # Vi phạm
            ws.set_landscape()
            ws.set_paper(9)             # A4
            ws.set_margins(0.3, 0.3, 0.3, 0.3)
  
            ws.merge_range(0, 0, 0, 3, 'TỔNG CỤC THUẾ', tct_format)
            ws.merge_range(1, 0, 1, 3, ct, ct_format)
            ws.insert_image('A3', line, {'x_offset': 40})
            ws.write(0, 6, 'CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM', chxh_format)
            ws.write(1, 6, 'Độc lập - Tự do - Hạnh phúc', chxh_format)
            ws.insert_image('F3', line, {'x_offset': 45, 'x_scale': 1.2})
            ws.merge_range(2, 0, 2, 3, 'Số: .........../XMAC', tct_format)
            ws.merge_range(3, 0, 3, 12, xmac, phieu_xm_format)
            ws.merge_range(4, 0, 4, 12, 'Kính gửi:   ', ct_format)
            ws.write(6, 0, 'Đơn vị bán hàng: ' + ten_dv_ban, dv_format)
            ws.write(6, 8, 'Mã số thuế: ' +
                     str(v['mst'].to_list()[0]), dv_format)
            ws.write(7, 0, 'Đơn vị mua hàng: ' + dvmh['ten_dv_mua'], dv_format)
            ws.write(7, 8, 'Mã số thuế: ' + str(dvmh['mst_dv_mua']), dv_format)
            # HEADER TABLE
            ws.merge_range(9, 0, 10, 0, 'Số TT', header_format)
            ws.merge_range(9, 1, 10, 1, 'Ký hiệu mẫu ấn chỉ', header_format)
            ws.merge_range(9, 2, 10, 2, 'Ký hiệu hóa đơn', header_format)
            ws.merge_range(9, 3, 10, 3, 'Hóa đơn số', header_format)
            ws.merge_range(
                9, 4, 9, 7, 'NỘI DUNG LIÊN 2 HÓA ĐƠN',  header_format)
            ws.merge_range(
                9, 8, 9, 11, 'NỘI DUNG LIÊN 1 HÓA ĐƠN',  header_format)
            ws.merge_range(9, 12, 10, 12, 'Vi phạm',  header_format)
            for c in [4, 8]:
                if c == 4:
                    ws.write(10, c, 'Đơn vị bán hàng', header_format)
                else:
                    ws.write(10, c, 'Đơn vị mua hàng', header_format)
                ws.write(10, c + 1, 'Mã số thuế', header_format)
                ws.write(10, c + 2, 'Số tiền thuế GTGT', header_format)
                ws.write(10, c + 3, 'Ngày lập hóa đơn', header_format)
            # DS HÓA ĐƠN
            for i in range(v.shape[0]):
                ws.write(row, col,    i+1,                      bang_format)
                # ws.write(row, col + 1, v['mau'].to_list()[i],    bang_format)
                # Trường hợp cột mẫu ấn chỉ k có dữ liệu
                # Người dùng điền "KXD" để tránh lỗi cell k có dữ liệu
                if pd.isna(v['mau'][i]):
                    ws.write(row, col + 1, '', bang_format)
                else:
                    ws.write(row, col + 1, v['mau'].to_list()[i], bang_format)
                ws.write(row, col + 2, v['ky_hieu'].to_list()[i], bang_format)
                ws.write(row, col + 3, v['so'].to_list()[i],     bang_format)
                ws.write(row, col + 4, v['ten'].to_list()[i],    bang_format_1)
                ws.write(row, col + 5, k,                        bang_format) #mst
                ws.write(row, col + 6, v['thue_gtgt'].to_list()[i], num_format)
                ws.write(row, col + 7, v['ngay'].to_list()[i], date_format)
                for j in range(1, 6):
                    ws.write(row, col+7+j, None, bang_format)
                row += 1

            ws.merge_range(row, 1, row, 12,
                           'Nếu có sự chênh lệch về nội dung trên các ấn chỉ, đề nghị đơn vị sao y bản chính gửi kèm theo kết quả xác minh.', dv_format)
            ws.set_row(row, 25)
            ws.merge_range(row + 1, 1, row + 1, 12,
                           'Nội dung ghi thêm:…………………………………………………………………………………………………', dv_format)
            # KÝ TÊN
            row = row + 3
            ws.write(row, 4, location, qtri_format)
            ws.write(row, 10, '........., ngày       tháng       năm', qtri_format)
            ws.merge_range(row + 1, 0, row + 1, 2,
                           'Cán bộ yều cầu xác minh', sign_format)
            ws.write(row + 1, 4, 'TUQ. CỤC TRƯỞNG', sign_format)
            ws.write(row + 2, 4, 'TRƯỞNG PHÒNG TT-KT', sign_format)
            ws.write(row + 1, 6, 'Cán bộ xác minh', sign_format)
            ws.write(row + 1, 10, 'Thủ trưởng đơn vị trả lời xác minh', sign_format)
            ws.merge_range(row + 6, 0, row + 6, 2, kyten['cbxm'], sign_format)
            ws.write(row + 6, 4, kyten['tp'], sign_format)
            # RESET ROW
            row = 11

        wb.close()
        return os.path.join(sending_path, filename)

 
""" data = process_data('D:\\python\\demo\\XMHD_errors.xlsx')
errors = data.check_data_valid()
print(errors) """


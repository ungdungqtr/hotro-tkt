import os
from django.conf import settings
from datetime import datetime
from docx import Document

def ghi_du_lieu_table(document, data):
    for k, v in data.items():
        for table in document.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        inline = paragraph.runs
                        for j in range(len(inline)):
                            if k in inline[j].text:
                                inline[j].text = inline[j].text.replace(
                                    k, v)

def ghi_du_lieu_para(document, data):
    for k, v in data.items():
        for paragraph in document.paragraphs:
            inline = paragraph.runs
            for j in range(len(inline)):
                if k in inline[j].text:
                    inline[j].text = inline[j].text.replace(k, v)

def del_row(table, row_start_del, row_count):
    # Xóa các hàng không có dữ liệu
    for row in table.rows[row_start_del + 1:row_count]:
        tbl = table._tbl
        tr = row._tr
        tbl.remove(tr)

def ghi_du_lieu_cell(row, text, text_replace):
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                inline = paragraph.runs
                for j in range(len(inline)):
                    if text in inline[j].text:
                        inline[j].text = inline[j].text.replace(
                            text, text_replace)

def vi_tri_bang(document, repalce_text):
    # document = Document(path)
    i = 0
    for paragraph in document.paragraphs:
        inline = paragraph.runs
        for j in range(len(inline)):
            if repalce_text in inline[j].text:
                return i
        i = i + 1

class lap_qd_ktra:
    def __init__(self, tt_qd, doan_ktra):
        self.tt_qd = tt_qd
        self.doan_ktra = doan_ktra

    def to_trinh(self):
        document = Document(os.path.join(settings.STATICFILES_DIRS[0], "media/to_trinh.docx"))
        # document = Document("D:\\Python\\qd_tkt\\mysite\\static\\media\\to_trinh.docx")
        ghi_du_lieu_para(document, self.tt_qd)
        filename = self.tt_qd["<mst>"] + "_To_trinh.docx"
        path = os.path.join(settings.STATICFILES_DIRS[0], "media_store/" + filename)   
        # path = os.path.join("D:\Python\qd_tkt\mysite\media", filename)      
        document.save(path)
        return path
    
    def qd_gsat(self):
        document = Document(os.path.join(settings.STATICFILES_DIRS[0], "media/qd_giam_sat.docx"))
        # document = Document("D:\\Python\\qd_tkt\\mysite\\static\\media\\qd_giam_sat.docx")
        ghi_du_lieu_para(document, self.tt_qd)
        filename = self.tt_qd["<mst>"] + "_QD_giam_sat.docx"
        path = os.path.join(settings.STATICFILES_DIRS[0], "media_store/" + filename)   
        # path = os.path.join("D:\Python\qd_tkt\mysite\media", filename)     
        document.save(path)
        return path

    def qd_ktra(self):
        document = Document(os.path.join(settings.STATICFILES_DIRS[0], "media/qd_ktra.docx"))
        # document = Document("D:\\Python\\qd_tkt\\mysite\\static\\media\\qd_ktra.docx")
        ghi_du_lieu_para(document, self.tt_qd)
        # ghi dữ liệu thành phần đoàn
        doc_table = Document(os.path.join(settings.STATICFILES_DIRS[0], "media/doan_ktra_table.docx"))
        # doc_table = Document("D:\\Python\\qd_tkt\\mysite\\static\\media\\doan_ktra_table.docx")
        table = doc_table.tables[0]
        # del_row(table, len(doan_ktra['<ten_cb>']), len(table.rows))
        for i in range(len(self.doan_ktra['<ten_cb>'])):
            row = table.rows[i]
            for k,v in self.doan_ktra.items():
                ghi_du_lieu_cell(row, k, v[i])
        # Xóa các hàng không có dữ liệu
        del_row(table, len(self.doan_ktra['<ten_cb>']) - 1, len(table.rows))
        # doc_table.save("doan_ktra.docx")
        # tb = Document("doan_ktra.docx")
        # template = tb.tables[0]
        tbl = table._tbl
        # tbl = template._tbl
        # Tìm vị trí '[*]' (vị trí đánh dấu)
        # Copy bảng thành viên vào vị trí đánh dấu
        loc = vi_tri_bang(document, '[*]')
        # template = tb.tables[0]
        # tbl = template._tbl
        p = document.paragraphs[loc]._p
        p.addnext(tbl)
        filename = self.tt_qd["<mst>"] + "_QD_kiem_tra.docx"
        path = os.path.join(settings.STATICFILES_DIRS[0], "media_store/" + filename)
        # path = os.path.join("D:\Python\qd_tkt\mysite\media", filename)
        document.save(path)
        return path
    
    def empty_media(self):
        media = os.path.join(settings.STATICFILES_DIRS[0], "media_store")
        for file in os.listdir(media):
            path = media + "/" + file
            os.remove(path)


""" tt_qd = {
    "<ngay_thang>": "ngày      tháng 3 năm 2021", # nhập tháng
    "<so_qd>": "2271/QĐ-TCT của Tổng cục Thuế về việc phê duyệt kế hoạch thanh tra, kiểm tra thuế tại doanh nghiệp năm 2021", # nhập số QĐ
    "<ten_dv>" : "Công Ty TNHH Xây Dựng Thủy Điện Đakrông", # lấy từ dữ liệu
    "<mst>" : "3200172428", # nhập
    "<dia_chi>" : "Xã Gio Châu, huyện Gio Linh, tỉnh Quảng Trị", # lấy từ dữ liệu  
    "<sl_cb>" : "03", # đếm số lượng cán bộ
    "<cb_cv>" : "Ông: Phạm Văn Vui – Phó trưởng phòng", # giới tính : tên - chức vụ (nếu có)
    "<so_nam_ktra>" : "01", # nhập
    "<nam_ktra>" : "2020", # tùy số lượng năm kiểm tra
    "<so_ngay_ktra>" : "05", # nhập
    "<ngay_ktra>" : "ngày 02 tháng 3 năm 2021", # nhập
    "<ng_giam_sat>" : "Ông Nguyễn Tiền Hải", # nhập
    "<ng_giam_sat_cv>" : "Phó Trưởng phòng", # lấy từ dữ liệu
    "<ld_to_trinh>" : "phó trưởng phòng".upper(), # chọn ['phó trưởng phòng', 'trưởng phòng']
    "<ten_ld_to_trinh>" : "nguyễn tiền hải".title (), # nhập
    "<hinh_thuc_ky>" : "KT.CỤC TRƯỞNG", # chọn
    "<lq_qd>" : "PHÓ CỤC TRƯỞNG",
    "<ten_ld_qd>" : "dương quốc hoàn".title(), # nhập
}
doan_ktra = {
    "<ten_cb>" : ['Ông: Phạm Văn Vui', 'Bà: Nguyễn Thị Thanh Huyền', "Bà: Hà Thị Thanh Thủy"],
    "<ngach_cb>" : ['Kiểm soát viên thuế', 'Kiểm tra viên thuế', 'Kiểm soát viên thuế'],
    "<cv_doan>" : ['Trưởng đoàn', 'Thành viên', 'Thành viên'],
} """

# ac = lap_qd_ktra(tt_qd, doan_ktra)
# p = ac.qd_ktra()
# print(p)





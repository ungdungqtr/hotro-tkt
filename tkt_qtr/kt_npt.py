import pandas as pd
import xml.dom.minidom as mnd
from datetime import datetime
ten_qh = {1: 'Con', 2: 'Vợ/Chồng', 3: 'Cha/Mẹ', 4: 'Khác'}


class kt_npt:
    def __init__(self, path):
        self.excel_path = path[0]
        self.xml_path = path[1]
        self.doc = mnd.parse(self.xml_path)
        
    def thong_tin_cqct(self):
        # self.doc = mnd.parse(self.xml_path)
        cqct = self.doc.getElementsByTagName('tenNNT')[0].firstChild.nodeValue
        mst  = self.doc.getElementsByTagName('mst')[0].firstChild.nodeValue
        kyKK = self.doc.getElementsByTagName('kyKKhai')[0].firstChild.nodeValue
        kk_tu_thang = self.doc.getElementsByTagName('kyKKhaiTuThang')[0].firstChild.nodeValue
        kk_den_thang = self.doc.getElementsByTagName('kyKKhaiDenThang')[0].firstChild.nodeValue
        return {"cqct": cqct, "mst": mst, "kyKK": kyKK, "kk_tu_thang": kk_tu_thang, "kk_den_thang": kk_den_thang}

    def PL_03(self):
        # self.doc = mnd.parse(self.xml_path)
        PL03 = self.doc.getElementsByTagName('BKeTTinNPT')
        NNT, MST_NNT, NPT, birth_date, MST_NPT, relationship, month_start, month_end = [], [], [], [], [], [], [], []
        kyKK = self.doc.getElementsByTagName('kyKKhai')[0].firstChild.nodeValue
        for id in PL03:
            NNT.append(id.getElementsByTagName('ct07')[0].firstChild.nodeValue)
            MST_NNT.append(id.getElementsByTagName(
                'ct08')[0].firstChild.nodeValue)
            NPT.append(id.getElementsByTagName('ct09')[0].firstChild.nodeValue)
            birth_date.append(datetime.strptime(id.getElementsByTagName(
                'ct10')[0].firstChild.nodeValue, '%Y-%m-%d'))
            MST_NPT.append(id.getElementsByTagName(
                'ct11')[0].firstChild.nodeValue)
            relationship.append(id.getElementsByTagName(
                'ct14_ma')[0].firstChild.nodeValue)
            month_start.append(datetime.strptime(
                id.getElementsByTagName('ct21')[0].firstChild.nodeValue, '%m/%Y'))
            month_end.append(datetime.strptime(id.getElementsByTagName(
                'ct22')[0].firstChild.nodeValue, '%m/%Y'))
        NPT_XML = pd.DataFrame([NNT, MST_NNT, NPT, birth_date, MST_NPT, relationship, month_start, month_end],
                               index=['NNT', 'MST_NNT', 'NPT', 'birth_date', 'MST_NPT', 'relationship', 'month_start', 'month_end']).T
        NPT_XML = pd.DataFrame([NNT, MST_NNT, NPT, birth_date, MST_NPT, relationship, month_start, month_end],
                               index=['NNT', 'MST_NNT', 'NPT', 'birth_date', 'MST_NPT', 'relationship', 'month_start', 'month_end']).T

        NPT_TMS = pd.read_excel(self.excel_path, converters={'MST NPT': str, 'MST NNT': str,
                                                             'Từ tháng': str, 'Đến tháng': str})
        NPT_TMS['Đến tháng'] = NPT_TMS['Đến tháng'].fillna('12.' + kyKK)
        NPT_TMS['Ngày sinh'] = NPT_TMS['Ngày sinh'].fillna(datetime.strptime('01/01/1900', '%d/%m/%Y'))
        return NPT_XML, NPT_TMS

    # Lọc thông tin NPT phù hợp với tờ khai (MST NNT, MST NPT thuộc thời gian kê khai giảm trừ)
    def kt_tg_kk(self, start_time_1, end_time_1, sub_df):
        drop_row = []
        for i in range(len(sub_df)):
            start_time_2 = datetime.strptime(sub_df['Từ tháng'][i], '%m.%Y')
            end_time_2 = datetime.strptime(sub_df['Đến tháng'][i], '%m.%Y')
            end_time = min(end_time_1, end_time_2)
            start_time = max(start_time_1, start_time_2)
            if end_time < start_time:
                drop_row.append(i)
                # sub_df = sub_df.drop(sub_df.index[i])
            #overlap = overlap + (end_time.month - start_time.month + 1 if end_time > start_time else 0)
        if drop_row:
            sub_df = sub_df.drop(sub_df.index[drop_row])
        return sub_df.reset_index()

    def ktra_thong_tin(self, feature, sub_df):
        if len(sub_df.drop_duplicates()) > 1:
            return False
        else:
            return True if (feature == sub_df[0]) else False

    def tg_giam_tru(self, start_time_1, end_time_1, sub_df):
        overlap = 0
        #err = 1
        for i in range(len(sub_df)):
            start_time_2 = datetime.strptime(sub_df['Từ tháng'][i], '%m.%Y')
            end_time_2 = datetime.strptime(sub_df['Đến tháng'][i], '%m.%Y')
            end_time = min(end_time_1, end_time_2)
            start_time = max(start_time_1, start_time_2)
            overlap += end_time.month - start_time.month + 1
        return str(overlap) + ' tháng'

    def tg_giam_tru_kk(self, sub_df):
        range_time = []
        for i in range(len(sub_df)):
            range_time.append(
                (sub_df['Từ tháng'][i] + ' - ' + sub_df['Đến tháng'][i]).replace('.', '/'))
        return range_time

    def trung_giam_tru(self, sub_df):
        return True if len(sub_df) > 1 else False

    def lech_giam_tru(self, start_time_1, end_time_1, sub_df):
        is_overlap = False
        for i in range(len(sub_df)):
            start_time_2 = datetime.strptime(sub_df['Từ tháng'][i], '%m.%Y')
            end_time_2 = datetime.strptime(sub_df['Đến tháng'][i], '%m.%Y')
            end_time = min(end_time_1, end_time_2)
            start_time = max(start_time_1, start_time_2)
            if not((end_time_1 == end_time) & (start_time_1 == start_time)):
                is_overlap = True
        return is_overlap

    def ngay_sinh_to_str(self, sub_df):
        s = []
        for i in sub_df.drop_duplicates():
            if i.year == 1900:
                s.append('Không có thông tin')
            else:
                s.append(i.strftime('%d/%m/%Y'))
        return '\n'.join(s)

    def rls_to_str(self, sub_df):
        return '; '.join([i for i in sub_df.drop_duplicates()])

    def time_to_str(self, sub_df):
        s = []
        for i in range(len(sub_df)):
            start_time = sub_df['Từ tháng'][i][0:2] + \
                "/" + sub_df['Từ tháng'][i][3:7]
            end_time = sub_df['Đến tháng'][i][0:2] + \
                "/" + sub_df['Đến tháng'][i][3:7]
            s.append(start_time + " - " + end_time)
        return '\n'.join(s) if len(s) > 1 else s

    def age(self, born):
        today = datetime.now()
        return str(today.year - born[0].year - ((today.month, today.day) < (born[0].month, born[0].day)))

    def kq_ktra(self):
        NPT_XML, NPT_TMS = self.PL_03()
        giam_tru, giam_tru_kk, thong_tin, ngay_sinh, quan_he, tuoi = [], [], [], [], [], []
        for i in range(len(NPT_XML)):
            # Lọc theo MST
            sub_df = NPT_TMS.loc[(NPT_TMS['MST NPT'] == NPT_XML['MST_NPT'][i]) & (
                NPT_TMS['MST NNT'] == NPT_XML['MST_NNT'][i])].reset_index()
            err = []
            if sub_df.empty:
                err.append('MST không được đăng ký')
                giam_tru.append('')
                giam_tru_kk.append('')
                ngay_sinh.append('')
                quan_he.append('')
                tuoi.append('')
            else:
                # Lọc theo thời gian giảm trừ
                giam_tru_kk.append(self.tg_giam_tru_kk(sub_df))
                if not self.ktra_thong_tin(NPT_XML['birth_date'][i], sub_df['Ngày sinh']):
                    err.append('- Sai ngày sinh')
                    tuoi.append('')
                else:
                    tuoi.append(self.age(sub_df['Ngày sinh']))
                if not self.ktra_thong_tin(ten_qh[int(NPT_XML['relationship'][i])], sub_df['Quan hệ đối với ĐTNT']):
                    err.append('- Sai mối quan hệ')
                elif NPT_XML['relationship'][i] == '01' and int(self.age(sub_df['Ngày sinh'])) > 22:
                    err.append('- Lưu ý: NPT đã hết tuổi giảm trừ')
                    print('OK')
                ngay_sinh.append(self.ngay_sinh_to_str(sub_df['Ngày sinh']))
                quan_he.append(self.rls_to_str(sub_df['Quan hệ đối với ĐTNT']))
                sub_df = self.kt_tg_kk(NPT_XML['month_start'][i], NPT_XML['month_end'][i], sub_df)
                if sub_df.empty:
                    err.append('- Sai thời gian giảm trừ')
                    giam_tru.append('0')
                else:
                    giam_tru.append(self.tg_giam_tru(
                        NPT_XML['month_start'][i], NPT_XML['month_end'][i], sub_df))
                    if self.lech_giam_tru(NPT_XML['month_start'][i], NPT_XML['month_end'][i], sub_df):
                        err.append('- Lệch hoặc trùng thời gian giảm trừ')
            thong_tin.append(err)
        NPT_XML['tg_giam_tru'] = giam_tru
        NPT_XML['giam_tru_kk'] = giam_tru_kk
        NPT_XML['ktra_loi'] = thong_tin
        NPT_XML['ngay_sinh'] = ngay_sinh
        NPT_XML['quan_he'] = quan_he
        NPT_XML['tuoi'] = tuoi
        return NPT_XML

"""a = kt_npt(['ETAX11320200033382538.xml', 'TH NPT.xlsx']).kq_ktra()
print(a.head(15))"""
""" path = ['export.xlsx', 'MAG.xml']
kt = kt_npt(path)
xml = kt.kq_ktra()
xml.to_excel('kq.xlsx') """

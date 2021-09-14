from django.urls import path, include
from . import views

app_name = 'tkt'
urlpatterns = [
    path('', views.index, name = 'tkt_base'),
    # Lập quyết định kiểm tra
    path('lap_qd_ktra/', views.lap_qd_ktra, name = 'lap_qd_ktra'),
    path('lap_qd_ktra/mst_autocomplete/', views.mst_autocomplete, name = 'mst_autocomplete'),
    path('lap_qd_ktra/cb_ten_autocomplete/', views.cb_ten_autocomplete, name = 'cb_ten_autocomplete'),
    path('lap_qd_ktra/nnt_thong_tin/', views.nnt_thong_tin, name = 'nnt_thong_tin'),
    path('lap_qd_ktra/cb_thong_tin/', views.cb_thong_tin, name = 'cb_thong_tin'),
    # Quản lý cán bộ
    path('qly_cb/', views.qly_cb, name = 'qly_cb'),
    path('qly_cb/them_moi_cb', views.them_moi_cb, name = 'them_moi_cb'),
    path('qly_cb/xoa_cb', views.xoa_cb, name = 'xoa_cb'),
    path('qly_cb/cap_nhat_thong_tin', views.cap_nhat_thong_tin, name = 'cap_nhat_thong_tin'),
    # Danh bạ NNT
    path('dba_nnt/', views.dba_nnt, name = 'dba_nnt'),
    path('dba_nnt/them_moi_nnt', views.them_moi_nnt, name = 'them_moi_nnt'),
    path('dba_nnt/xoa_nnt', views.xoa_nnt, name = 'xoa_nnt'),
    path('dba_nnt/cap_nhat_nnt', views.cap_nhat_nnt, name = 'cap_nhat_nnt')
]
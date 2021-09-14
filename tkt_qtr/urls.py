from django.urls import path, include
from . import views

app_name = 'apps'
urlpatterns = [
    path('', views.index, name='apps_base'),
    path('apps/xmhd_upload/', views.xmhd_upload, name='xmhd_upload'),       # upload bảng kê hóa đơn
    path('apps/xmhd_index/', views.xmhd_index, name='xmhd_index'),          # chi tiết BKHD theo từng đơn vị
    path('apps/ktnpt_upload', views.ktnpt_upload, name='ktnpt_upload'),     # upload đối chiếu NPT  
    path('apps/ktnpt_result', views.ktnpt_result, name='ktnpt_result'),     # kết quả đối chiếu NPT            
]

from django.urls import path

from . import views

app_name = 'trigger3'

urlpatterns = [
    path('createpesanansumberdaya', views.createPesananSD, name='CreatePesananSumberDaya'),
    path('readpesanansumberdaya', views.readPesanan, name='ReadPesananSumberDaya'),
    path('readpesanansumberdaya/detail/<int:idPesanan>', views.detailPesanan, name='DetailPesanan'),
    path('readpesanansumberdaya/riwayatstatus/<int:idPesanan>',views.riwayatStatus,name='RiwayatStatus'),
    path('readpesanansumberdaya/updatepesanan/<int:idPesanan>', views.updatePesanan, name='UpdatePesanan'),
    path('SupplierReadPesanan',views.SupplierReadPesanan,name='SupplierReadPesanan'),
    path('SupplierReadPesanan/detail/<int:idPesanan>',views.detailPesananSupplier,name='DetailPesananSupplier'),
    path('SupplierReadPesanan/riwayatstatus/<int:idPesanan>',views.riwayatStatusSupplier,name='RiwayatStatusSupplier'),
    path('createstockfaskes',views.createStockFaskes, name='CreateStockFaskes'),
    path('liststockfaskes',views.listStockFaskes, name='ListStockFaskes'),
    path('liststockfaskes/updatestock/<str:kodeFaskes>/<str:namaFaskes>/<str:namaItem>', views.updateStockFaskes, name='UpdateStockFaskes'),
    path('liststockfaskespetugas',views.ListStockFaskesPetugas,name='ListStockFaskesPetugas')
]
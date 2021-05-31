from django.urls import path

from . import views

app_name = 'pengguna'

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('registerSupplier', views.registerSupplier, name='registerSupplier'),
    path('registerPetugasFaskes', views.registerPetugasFaskes ,name='registerPetugasFaskes'),
    path('registerPetugasDistribusi', views.registerPetugasDistribusi, name='registerPetugasDistribusi'),
    path('registerAdminSatgas', views.registerAdminSatgas, name='registerAdminSatgas')
]
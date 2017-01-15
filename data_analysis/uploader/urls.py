from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^upload/(?P<pk>\d+)/$', views.upload_file, name='file_upload'),
    url(r'^upload/(?P<pk>\d+)delete/$', views.delete_file, name='file_delete'),
    url(r'^upload/(?P<pk>\d+)/populate/$', views.populate_fields, name='populate_fields'),
]

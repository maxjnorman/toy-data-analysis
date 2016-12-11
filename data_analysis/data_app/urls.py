from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.table_list, name='table_list'),
    url(r'^table/(?P<pk>\d+)/$', views.table_detail, name='table_detail'),
    url(r'^table/create/$', views.create_table, name='create_table'),
    url(r'^table/(?P<pk>\d+)/edit/$', views.edit_table, name='edit_table'),
    url(r'^table/(?P<pk>\d+)/entry/$', views.input_table_entry, name='input_table_entry'),
]

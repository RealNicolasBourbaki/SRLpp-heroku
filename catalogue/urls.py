from django.urls import re_path

from .views import browse, search_view, search, download, search_download, all_catalogue_download, upload_file, submit_sg_generation

urlpatterns = [
    re_path(r'^search/.*$', search, name='search'),
    re_path(r'^search_results/(?P<link>.*)_(?P<query>.*)$', search_view, name='search_results'),
    re_path(r'^download/(?P<path>.*)$', download, name='download_file'),
    re_path(r'^search_download/*$', search_download, name='search_download'),
    re_path(r'^catalogue_download/.*$', all_catalogue_download, name='catalogue_download'),
    re_path(r'^generate_sg/.*$', submit_sg_generation, name='generate_sg'),
    re_path(r'^(?P<path>.*)_(?P<mode>.*)$', browse, name='catalogue_browse'),
    re_path(r'^submit/.*$', upload_file, name='submit'),
]

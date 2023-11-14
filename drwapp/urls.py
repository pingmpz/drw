from django.urls import path,include
from django.conf import settings
from django.urls import re_path
from django.conf.urls.static import static
from django.views.static import serve
from . import views

urlpatterns = [
    #################################### PAGE ######################################
    path('<str:dir>&<str:fg_code>', views.drw, name='drw'),
    path('img/<str:fg_code>&<str:file_name>', views.img, name='img'),
    path('search/<str:fg_code>', views.search, name='search'),
    #################################### FILE ######################################
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),
]+ static(settings.MEDIA_URL, serve, document_root=settings.MEDIA_ROOT)

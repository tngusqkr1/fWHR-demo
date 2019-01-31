from django.conf.urls import url
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
                  url(r'^$', views.main, name='main'),
                  url(r'^browse$', views.simple_upload),
                  url(r'^download/media/(?P<file_name>.+)$', views.image_download, name='download'),

              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

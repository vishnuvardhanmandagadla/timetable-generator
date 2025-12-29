from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('inputs.html', views.inputs, name='inputs'),
    path('outputs.html', views.outputs, name='outputs'),
    path('loading_animation.html', views.loading_animation, name='loading_animation'),
    path('generate_timetable', views.generate_timetable, name='generate_timetable'),
    path('profile.html', views.profile, name='profile'),
    path('contact.html', views.contact, name='contact'),
    path('about.html', views.about, name='about'),
    path('help.html', views.help, name='help'), 
    path('rules.html', views.rules, name='rules'),
    path('download-demo/<str:filename>', views.download_demo, name='download_demo'),
    path('download/<str:file_name>', views.download_file, name='download_file'),
    
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
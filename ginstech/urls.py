
from django.contrib import admin
from django.urls import path,include
from ginstech import views


urlpatterns = [
    path('', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
    path('authenticate/', include('authenticate.urls')),
    path('chatbot/', include('chatbot.urls'), name='chatbot'),
]

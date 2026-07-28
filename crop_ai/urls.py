from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from app.views import custom_logout

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('app.urls')),

    path('login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', custom_logout, name='logout'),
]

# THIS MUST BE AFTER urlpatterns
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
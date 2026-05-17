from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView, RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Root redirect
    path('', RedirectView.as_view(url='/djangoapp/', permanent=False), name='root'),
    # Static pages
    path('about/', TemplateView.as_view(template_name="About.html"), name='about'),
    path('contact/', TemplateView.as_view(template_name="Contact.html"), name='contact'),
    # React app routes (serves built index.html)
    path('login/', TemplateView.as_view(template_name="index.html"), name='login_page'),
    path('register/', TemplateView.as_view(template_name="index.html"), name='register_page'),
    # Django app
    path('djangoapp/', include('djangoapp.urls')),
]

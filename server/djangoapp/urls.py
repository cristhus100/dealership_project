from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # Static pages
    path('about/', TemplateView.as_view(template_name="About.html"), name='about'),
    path('contact/', TemplateView.as_view(template_name="Contact.html"), name='contact'),

    # Auth API
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('register/', views.register_user, name='register'),
    path('csrf/', views.get_csrf_token, name='csrf'),

    # Cars API (lab exacto)
    path('get_cars', views.get_cars, name='getcars'),

    # ============================================================
    # Dealers API (lab exacto via restapis.py)
    # ============================================================
    path('get_dealers', views.get_dealerships, name='get_dealers'),
    path('get_dealers/<str:state>', views.get_dealerships, name='get_dealers_by_state'),
    path('api/dealer/<int:dealer_id>', views.get_dealer_details, name='dealer_details_api'),

    # ============================================================
    # Reviews API (lab exacto via restapis.py)
    # ============================================================
    path('reviews/dealer/<int:dealer_id>', views.get_dealer_reviews, name='get_dealer_reviews'),
    path('add_review', views.add_review, name='add_review'),

    # ============================================================
    # Template-based pages (HTML)
    # ============================================================
    path('', views.get_dealers_page, name='home'),
    path('dealer/<int:dealer_id>/', views.get_dealer_details_page, name='dealer_details_page'),
    path('add_review/<int:dealer_id>/', views.add_review_page, name='add_review_page'),

    # Sentiment
    path('analyze/<path:text>/', views.analyze_review, name='analyze_review'),
]

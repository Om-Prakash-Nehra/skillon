from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('tickets.urls')),  # Your DRF API endpoints

    # Template routes (all inside tickets/templates/tickets/)
    path('', TemplateView.as_view(template_name='tickets/index.html'), name='login'),
    path('register/', TemplateView.as_view(template_name='tickets/register.html'), name='register'),
    path('dashboard/', TemplateView.as_view(template_name='tickets/dashboard.html'), name='dashboard'),
    path('ticket-details/', TemplateView.as_view(template_name='tickets/ticket-detail.html'), name='ticket-details'),

]

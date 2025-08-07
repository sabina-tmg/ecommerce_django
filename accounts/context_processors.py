# context_processors.py
from .models import SiteSettings

def site_settings(request):
    settings = SiteSettings.objects.first()  # assuming only one settings record
    return {
        'email': settings.email if settings else '',
        'phone': settings.phone if settings else '',
    }

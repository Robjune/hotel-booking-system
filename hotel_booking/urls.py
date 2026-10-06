from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # Main website
    path('', include('core.urls')),

    # Rooms
    path('rooms/', include('rooms.urls')),

    # Bookings
    path('bookings/', include('bookings.urls')),

    # Accounts
    path('accounts/', include('accounts.urls')),

    # Contact
    path('contact/', include('contact.urls')),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
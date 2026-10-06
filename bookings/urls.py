from django.urls import path

from . import views

app_name = 'bookings'

urlpatterns = [
    path('', views.my_bookings, name='my_bookings'),
    path('book/<int:room_id>/', views.create_booking, name='create'),
    path('<str:reference>/', views.booking_detail, name='detail'),
    path('<str:reference>/cancel/', views.cancel_booking, name='cancel'),
]

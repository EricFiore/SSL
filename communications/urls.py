from django.urls import path
from .views import MessageView, MessageDeleteView

urlpatterns = [
    path('', MessageView.as_view(), name='message-list'),
    path('delete/<uuid:pk>', MessageDeleteView.as_view(), name='message-delete'),
]

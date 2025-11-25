from django.urls import path
from chatpage import views


urlpatterns = [
    path("", views.ChatView.as_view(), name="query"),
]

from django.contrib import admin
from django.urls import path
from webapp.views import (
    CustomLoginView,
    CustomLogoutView,
    listmaker_view,
    judge_view,
    public_view,
    manage_items,
)

urlpatterns = [
    path('admin/', admin.site.urls),  # Ensure this line is included
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),  
    path('listmaker/', listmaker_view, name='listmaker'),
    path('judge/', judge_view, name='judge'),
    path('public/', public_view, name='public'),
    path('items/', manage_items, name='manage_items'),
    path('items/<int:pk>/', manage_items, name='manage_single_item'),
    path('', CustomLoginView.as_view(), name='default'),
]
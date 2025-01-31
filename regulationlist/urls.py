from django.contrib import admin
from django.urls import path
from webapp.views import (
    CustomLoginView,
    CustomLogoutView,
    listmaker_view,
    judge_view,
    public_view,
    manage_items,
    judge_item,
    add_list_item,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('listmaker/', listmaker_view, name='listmaker'),
    path('judge/', judge_view, name='judge'),
    path('public/', public_view, name='public'),
    path('items/', manage_items, name='manage_items'),
    path('items/<int:pk>/', manage_items, name='manage_single_item'),
    path('judge_item/<int:pk>/', judge_item, name='judge_item'),
    path('', CustomLoginView.as_view(), name='default'),
    path('add-item/', add_list_item, name='add_item'),
]

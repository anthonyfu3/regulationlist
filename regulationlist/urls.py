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
    fetch_list_items,
    edit_list_item,
    public_fetch_list_items,
    fetch_judge_list_items
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
    path('add-item/', add_list_item, name='add_list_item'),
    path('fetch-list-items/', fetch_list_items, name='fetch_list_items'),
    path('edit-item/<int:pk>/', edit_list_item, name='edit_list_item'),
    path('api/public-list-items/', public_fetch_list_items, name='public_fetch_list_items'),
    path('fetch-judge-list-items/', fetch_judge_list_items, name='fetch_judge_list_items'),
]
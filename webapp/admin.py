from django.contrib import admin
from .models import ListItem

@admin.register(ListItem)
class ListItemAdmin(admin.ModelAdmin):
    list_display = ('number_in_list', 'name', 'description', 'vote_status', 'votes_needed', 'votes_had', 'created_by')
    list_filter = ('is_valid',)
    search_fields = ('description', 'created_by__username')
    actions = ['mark_as_valid', 'mark_as_not_valid']

    # Custom actions for bulk updates
    @admin.action(description="Mark selected items as Valid")
    def mark_as_valid(self, request, queryset):
        queryset.update(is_valid=True)

    @admin.action(description="Mark selected items as Not Valid")
    def mark_as_not_valid(self, request, queryset):
        queryset.update(is_valid=False)

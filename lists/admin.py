from django.contrib import admin

from .models import *

class ListAdmin(admin.ModelAdmin):
    model = List
    
    list_display = ('owner', 'title', 'members', 'created_at')
    list_filter = ('created_at', 'owner')
    
    readonly_fields = ('owner', 'created_at', 'members')
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('title', 'tweets')}
         ),
    )
    
    search_fields = ('title', 'owner')
    ordering = ('-created_at',)
    
    def get_fieldsets(self, request, obj):
        if not obj:
            return (
                (None, {'fields': ('title', 'tweets')}),
            )

        return (
            (None, {'fields': ('title', 'tweets', 'owner')}),
            ('Statistics', {'fields': ('members',)}),
            ('Date', {'fields': ('created_at',)}),
        )

    def members(self, obj):
        return obj.users.count()
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.owner = request.user

        return super().save_model(request, obj, form, change)
    
admin.site.register(List, ListAdmin)
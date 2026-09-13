from typing import Any
from django.contrib import admin
from django.http import HttpRequest

from .forms import *
from .models import *

class ImageInline(admin.TabularInline):
    model = Image
    form = ImageForm
    extra = 1

class TweetAdmin(admin.ModelAdmin):
    model = Tweet

    list_display = ('owner', 'content', 'views', 'created_at')
    list_filter = ('created_at',)

    readonly_fields = ('views', 'created_at')

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('content', 'quote_tweet')}
         ),
    )
    inlines = [ImageInline]

    search_fields = ('owner__username', 'content')
    ordering = ('-created_at',)
    
    def get_fieldsets(self, request, obj):
        if not obj:
            return (
                (None, {'fields': ('content', 'quote_tweet')}),
            )
        
        return (
            (None, {'fields': ('content', 'quote_tweet')}),
            ('Statistics', {'fields': ('views',)}),
            ('Dates', {'fields': ('created_at',)})
        )
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.owner = request.user

        return super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for formset in formsets:
            if isinstance(formset, ImageInline):
                for obj in formset.save(commit=False):
                    obj.tweet = form.instance
                    obj.save()

class ReplyAdmin(admin.ModelAdmin):
    model = Reply
    
    list_display = ('owner', 'content', 'views', 'created_at')
    list_filter = ('created_at',)
    
    inlines = [ImageInline]
    
    readonly_fields = ('views', 'created_at', 'owner')

    search_fields = ('owner__username', 'content')
    ordering = ('-created_at',)
    
    def get_fieldsets(self, request, obj):
        if not obj:
            return (
                (None, {'fields': ('tweet', 'parent_reply', 'content')}),
            )
        
        return (
            (None, {'fields': ('tweet', 'parent_reply', 'content', 'owner')}),
            ('Statistics', {'fields': ('views',)}),
            ('Dates', {'fields': ('created_at',)})
        )
        
    def get_readonly_fields(self, request, obj):
        if not obj:
            return self.readonly_fields
        
        obj.clean()
        return self.readonly_fields + ('tweet', 'parent_reply')
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.owner = request.user

        return super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        for formset in formsets:
            if isinstance(formset, ImageInline):
                for obj in formset.save(commit=False):
                    if form.instance.tweet is not None:
                        obj.tweet = form.instance
                    else:
                        obj.reply = form.instance

                    obj.save()


admin.site.register(Tweet, TweetAdmin)
admin.site.register(Reply, ReplyAdmin)
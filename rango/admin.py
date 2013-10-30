from django.contrib import admin
from rango.models import Category, Page

class PageInline(admin.TabularInline):
    model = Page
    extra = 3

class CategoryAdmin(admin.ModelAdmin):
    fieldsets = [
            (None,            {'fields' : ['name']}),
            ('Rating info',   {'fields' : ['views', 'likes'], 'classes' : ['collapse']})
    ]
    inlines = [PageInline]

class PageAdmin(admin.ModelAdmin):
    list_display = ('category', 'title', 'url')

admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)

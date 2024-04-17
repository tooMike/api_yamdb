from django.contrib import admin

from .models import Category, Comment, Genre, GenreTitle, Review, Title


class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('slug',)
    list_display_links = ('name',)


class GenreAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    search_fields = ('name',)
    list_filter = ('slug',)
    list_display_links = ('name',)


class GenreInline(admin.TabularInline):
    model = GenreTitle
    extra = 1


class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'year',
    )
    search_fields = ('name',)
    list_filter = ('category',)
    list_display_links = ('name',)
    inlines = (GenreInline,)


admin.site.register(Category, CategoryAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Title, TitleAdmin)
admin.site.register(Review)
admin.site.register(Comment)

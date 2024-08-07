from django.contrib import admin

from .models import User, Category, Genre, Title, Review, Comment


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'bio')
    search_fields = ('username', 'email')
    list_filter = ('role',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category')
    search_fields = ('name', 'category__name')
    list_filter = ('category', 'year')


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'score', 'pub_date')
    search_fields = ('author__username', 'title__name')
    list_filter = ('score', 'pub_date')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'review', 'pub_date')
    search_fields = ('author__username', 'review__title__name')
    list_filter = ('pub_date',)

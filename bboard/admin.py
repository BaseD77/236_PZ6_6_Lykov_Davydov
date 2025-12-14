from django.contrib import admin
from .models import Bb, Rubric, UserProfile, Tag, Category, Friend, Order, OrderItem


class BbAdmin(admin.ModelAdmin):
    list_display = ('rubric', 'title', 'content', 'price', 'published')
    list_display_links = ('title', 'content')
    search_fields = ('title', 'content')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address')
    search_fields = ('user__username', 'phone')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_bbs_count')

    def get_bbs_count(self, obj):
        return obj.bbs.count()

    get_bbs_count.short_description = 'Количество объявлений'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent')
    list_filter = ('parent',)
    search_fields = ('name',)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'created_at', 'total_price')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'bb', 'quantity', 'price_at_order')
    list_filter = ('order',)


# Только ОДНА регистрация каждой модели!
admin.site.register(Bb, BbAdmin)
admin.site.register(Rubric)
admin.site.register(Friend)
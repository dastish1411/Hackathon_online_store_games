from django.contrib import admin
from .models import Products, Rating, ProductsImage, Like

admin.site.register([Rating, Like])


class TabularInlineImages(admin.TabularInline):
    model = ProductsImage
    extra = 1
    fields = ['image']


class ProductAdmin(admin.ModelAdmin):
    model = Products
    inlines = [TabularInlineImages]

admin.site.register(Products, ProductAdmin)
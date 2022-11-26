from django.contrib import admin
from django.contrib.auth.models import Group

from .models import (Ingredients, Recipe, RecipeFavorited, RecipeIngredient,
                     ShoppingCart, Subscription, Tags)

admin.site.unregister(Group)

admin.site.site_header = "Административная панель проекта Foodgram"
admin.site.site_title = "Панель администрирования Foodgram"
admin.site.index_title = "Добро пожаловать в админку Foodgram"


class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "role")
    list_filter = ("email", "username",)
    empty_value_display = "-пусто-"


class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "color", "slug")
    empty_value_display = "-пусто-"


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "following")
    empty_value_display = "-пусто-"


class IngredientAdmin(admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    list_filter = ("name",)
    empty_value_display = "-пусто-"


class IngredientInline(admin.StackedInline):
    model = RecipeIngredient
    extra = 5


class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline]
    list_display = ("name", "author")
    search_fields = ('name',)
    list_filter = ("author", "name", "tags",)
    empty_value_display = '-пусто-'
    readonly_fields = ["favourited_count"]

    def favourited_count(self, obj):
        count = RecipeFavorited.objects.filter(recipe_id=obj.pk).count()
        return f"{count}"
    favourited_count.short_description = (
            "Этот рецепт в избранном пользователей")


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


class RecipeFavoritedAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tags, TagAdmin)
admin.site.register(Ingredients, IngredientAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(RecipeFavorited, RecipeFavoritedAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
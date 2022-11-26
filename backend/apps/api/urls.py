from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework import routers
from users.views import UserSubscriptionViewSet

from .views import (IngredientsViewSet, RecipeFavoritedViewSet, RecipesViewSet,
                    ShoppingCartViewSet, TagsViewSet, UserCurrentViewSet)

router = routers.DefaultRouter()

router.register("tags", TagsViewSet, basename="tags")
router.register("ingredients", IngredientsViewSet, basename="ingredients")
router.register("recipes", RecipesViewSet, basename="recipes")

urlpatterns = [
    path(
        "recipes/<int:recipe_id>/shopping_cart/",
        ShoppingCartViewSet.as_view(), name="shopping_cart"
        ),
    path(
        "recipes/<int:recipe_id>/favorite/", RecipeFavoritedViewSet.as_view(),
        name="recipe_favorited"
        ),
    path(
        "users/<int:following_id>/subscribe/",
        UserSubscriptionViewSet.as_view(
            {'post': 'create', 'delete': 'destroy'}),
        name="user_subscribe"
        ),
    path(
        "users/subscriptions/",
        UserSubscriptionViewSet.as_view({'get': 'list'}),
        name="user_subscription"
        ),
    path(
        "users/<int:pk>/", UserCurrentViewSet.as_view({'get': 'retrieve'}),
        name="user_current"
        ),
    path("auth/", include('djoser.urls.authtoken')),
    path("", include(router.urls), name="main"),
    path("", include('djoser.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# from http import HTTPStatus

from django.db.models import Subquery
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from recipes import utils
from recipes.models import (Ingredients, Recipe, RecipeFavorited,
                            RecipeIngredient, ShoppingCart, Subscription, Tags,
                            User)
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.settings import VALIDATION_ERRORS

from .permissons import IsUserOrReadOnly
from .serializers import (IngredientSerializer, RecipeFavoritedSerializer,
                          RecipeSerializer, ShoppingCartSerializer,
                          TagSerializer, UsersSerializer)


class TagsViewSet(viewsets.ModelViewSet):
    """
    Тэги.
    """
    queryset = Tags.objects.all()
    serializer_class = TagSerializer
    permission_classes = (
        AllowAny,
    )
    pagination_class = None


class IngredientsViewSet(viewsets.ModelViewSet):
    """
    Ингредиенты.
    """
    serializer_class = IngredientSerializer
    permission_classes = (
        AllowAny,
    )
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredients.objects.all()
        name = self.request.query_params.get('name')
        if name is not None:
            queryset = queryset.filter(name__contains=name)
        return queryset


class RecipesViewSet(viewsets.ModelViewSet):
    """
    Рецепты.
    """
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (
        IsUserOrReadOnly,
    )

    def get_queryset(self):
        queryset = Recipe.objects.all()
        tags = self.request.query_params.get('tags')
        author = self.request.query_params.get('author')
        limit = self.request.query_params.get('limit')
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        if tags is not None:
            tags_query = self.request.query_params.getlist('tags',)
            queryset = Recipe.objects.filter(tags__slug__in=tags_query)
        elif author is not None:
            author_query = self.request.query_params['author']
            queryset = Recipe.objects.filter(author=author_query)
        elif is_favorited and str(self.request.user) != 'AnonymousUser':
            is_favorited_query = self.request.query_params['is_favorited']
            if int(is_favorited_query) == 1:
                recipes_favorited = RecipeFavorited.objects.filter(
                    user_id=self.request.user)
                queryset = Recipe.objects.filter(
                    pk__in=Subquery(recipes_favorited.values("recipe_id")))
        elif is_in_shopping_cart and str(self.request.user) != 'AnonymousUser':
            if int(is_in_shopping_cart) == 1:
                recipes_shopping_cart = ShoppingCart.objects.filter(
                    user_id=self.request.user)
                queryset = Recipe.objects.filter(
                    pk__in=Subquery(recipes_shopping_cart.values("recipe_id")))

        if limit is not None:
            limit = int(limit)
            queryset = queryset[:limit]
        return queryset

    def retrieve(self, request, *args, **kwargs):
        recipe_id = kwargs["pk"]
        recipe_is_favorited = False
        recipe_is_in_shopping_cart = False
        user_is_subscribed = False
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        serializer_data = serializer.data
        recipe_author_id = serializer_data["author"]["id"]
        if str(request.user) != "AnonymousUser":
            if RecipeFavorited.objects.filter(
                                              user=request.user,
                                              recipe_id=recipe_id
                                              ).count() != 0:
                recipe_is_favorited = True
            if ShoppingCart.objects.filter(user=request.user,
                                           recipe_id=recipe_id).count() != 0:
                recipe_is_in_shopping_cart = True
            if Subscription.objects.filter(user=request.user,
                                           following_id=recipe_author_id
                                           ).count() != 0:
                user_is_subscribed = True
        serializer_data["is_favorited"] = recipe_is_favorited
        serializer_data["is_in_shopping_cart"] = recipe_is_in_shopping_cart
        serializer_data["author"]["is_subscribed"] = user_is_subscribed
        return Response(serializer_data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=self.request.data)
        row_image_data = self.request.data['image']
        tags = self.request.data.get("tags")
        ingredients = self.request.data.get("ingredients")
        if serializer.is_valid():
            serializer.save(tags=tags,
                            ingredients=ingredients,
                            author=self.request.user)
            data_to_response = serializer.data
            data_to_response_new_order = (
                utils.recipe_serializer_response_update(
                    data_to_response)
                )
            data_to_response_new_order['image'] = row_image_data
            return Response(data_to_response_new_order,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(
                    instance=self.get_object(), data=request.data)
        row_image_data = self.request.data['image']
        tags = self.request.data.get("tags")
        ingredients = self.request.data.get("ingredients")
        if serializer.is_valid():
            serializer.save(tags=tags,
                            ingredients=ingredients,
                            author=self.request.user)
            data_to_response = serializer.data
            data_to_response_new_order = (
                utils.recipe_serializer_response_update(data_to_response))
            data_to_response_new_order['image'] = row_image_data
            return Response(data_to_response_new_order,
                            status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
            methods=("GET",),
            detail=False,
            permission_classes=(IsAuthenticated,),
            url_path="download_shopping_cart",
        )
    def download_shopping_cart(self, request):
        recipes_in_shopping_cart = ShoppingCart.objects.filter(
                            user=request.user)
        recipes_ingredients_in_shopping_cart = RecipeIngredient.objects.filter(
            recipe_id__in=Subquery
            (recipes_in_shopping_cart.values("recipe_id"))).values(
            "ingredient_id", "amount",
            "ingredient__name", "ingredient__measurement_unit")
        products = {}
        for rec in recipes_ingredients_in_shopping_cart:
            rec = dict(rec)
            ingredient_id = rec["ingredient_id"]
            ingredient_name = rec["ingredient__name"]
            ingredient_amount = int(rec["amount"])
            ingredient_measurement_unit = rec["ingredient__measurement_unit"]
            if ingredient_id in products.keys():
                ammount = products[ingredient_id][2] + ingredient_amount
                products[ingredient_id] = [ingredient_name,
                                           ingredient_measurement_unit,
                                           ammount]
            else:
                products[ingredient_id] = [ingredient_name,
                                           ingredient_measurement_unit,
                                           rec["amount"]]
        file_data = ""
        for k, v in products.items():
            file_data += f"<li> {v[0].title()} ({v[1]}) — {v[2]}\n"
        response = HttpResponse(file_data,
                                content_type='text/html; charset=utf-8')
        response['Content-Disposition'] = 'attachment;filename="products.html"'
        return response


class ShoppingCartViewSet(generics.CreateAPIView, generics.DestroyAPIView):
    """
    Список покупок.
    """
    permission_classes = (
        IsUserOrReadOnly,
    )
    serializer_class = ShoppingCartSerializer

    def create(self, request, **kwargs):
        recipe_id = kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, pk=recipe_id)
        serializer = self.serializer_class(data=request.data)
        if ShoppingCart.objects.filter(recipe_id=recipe_id,
                                       user=request.user).count() != 0:
            return Response({"errors":
                            VALIDATION_ERRORS[
                                'RECIPE_ALREADY_IN_SHOPPING_CART'
                                ]},
                            status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid(self):
            serializer.save(recipe_id=recipe_id, user=request.user)
            recipe_image = utils.recipe_image_name_get(recipe)
            return Response({
                            "id": recipe.id,
                            "name": recipe.name,
                            "cooking_time": recipe.cooking_time,
                            "image": recipe_image
                            },
                            status=status.HTTP_201_CREATED
                            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        recipe_id = kwargs['recipe_id']
        if ShoppingCart.objects.filter(recipe_id=recipe_id,
                                       user=request.user).count() == 0:
            return Response({
                    "errors":
                    VALIDATION_ERRORS['RECIPE_NOT_FOUND_IN_SHOPPING_CART']
                    },
                    status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.get(recipe_id=recipe_id,
                                 user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeFavoritedViewSet(generics.CreateAPIView, generics.DestroyAPIView):
    """
    Избранное.
    """
    permission_classes = (
        IsUserOrReadOnly,
    )
    serializer_class = RecipeFavoritedSerializer

    def create(self, request, **kwargs):
        recipe_id = kwargs['recipe_id']
        serializer = self.serializer_class(data=request.data)
        if RecipeFavorited.objects.filter(recipe_id=recipe_id,
                                          user=request.user).count() != 0:
            return Response({
                            "errors":
                            VALIDATION_ERRORS['RECIPE_ALREADY_IN_FAVORITED']
                            },
                            status=status.HTTP_400_BAD_REQUEST)
        if serializer.is_valid(self):
            serializer.save(recipe_id=recipe_id, user=self.request.user)
            recipe = Recipe.objects.get(pk=recipe_id)
            recipe_image = utils.recipe_image_name_get(recipe)
            return Response({
                            "id": recipe.id,
                            "name": recipe.name,
                            "image": recipe_image,
                            "cooking_time": recipe.cooking_time
                            },
                            status=status.HTTP_201_CREATED
                            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, **kwargs):
        recipe_id = kwargs['recipe_id']
        if RecipeFavorited.objects.filter(recipe_id=recipe_id,
                                          user=request.user).count() == 0:
            return Response({
                            "errors":
                            VALIDATION_ERRORS[
                                             'RECIPE_NOT_FOUND_IN_FAVORITED']},
                            status=status.HTTP_400_BAD_REQUEST,
                            )
        RecipeFavorited.objects.get(recipe_id=recipe_id,
                                    user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserCurrentViewSet(viewsets.ModelViewSet):
    """
    Пользователи.
    """
    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (
        IsAuthenticated,
    )

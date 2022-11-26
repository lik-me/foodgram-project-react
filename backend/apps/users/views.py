from rest_framework.permissions import IsAuthenticated
from rest_framework import status, viewsets
from users.models import User
from recipes.models import Subscription, Recipe
from api.serializers import (SubscriptionSerializer, 
                             SubscriptionSerializerList,)
from rest_framework.response import Response
# from django.contrib.auth.hashers import check_password, make_password
from django.db.models import Subquery
from recipes import utils
from apps.settings import VALIDATION_ERRORS


class UserSubscriptionViewSet(viewsets.ModelViewSet):
    """"
    Подписки пользователя.
    """
    permission_classes = (
        IsAuthenticated,
    )
    serializer_class = SubscriptionSerializer

    def get_serializer_class(self):
        print(self.request.method)
        if self.request.method == "GET":
            return SubscriptionSerializerList
        return SubscriptionSerializer

    def get_queryset(self):
        if self.request.method == "GET":
            following_users_pre = (
                    Subscription.objects.filter(user=self.request.user)
                                  )
            queryset = User.objects.filter(
                    pk__in=Subquery(following_users_pre.values('following_id'))
                    ).all()
            return queryset
        queryset = Subscription.objects.filter(user=self.request.user).all()
        return queryset

    def get_serializer_context(self):
        context = {}
        if self.request.query_params.get("recipes_limit"):
            context['recipes_limit'] = (
                self.request.query_params.get("recipes_limit")
                )
        return context

    def create(self, request, **kwargs):
        following_id = kwargs['following_id']
        serializer = self.serializer_class(data=request.data)
        if Subscription.objects.filter(
                following_id=following_id, user=request.user
                ).count() != 0:
            return Response({"errors": 
                            VALIDATION_ERRORS['USER_ALREADY_SUBSCRIBED']}, 
                            status=status.HTTP_400_BAD_REQUEST)
        if following_id == request.user.id:
            return Response({
                "errors": VALIDATION_ERRORS['SELF_SUBSCRIBED']
                }, 
                status=status.HTTP_400_BAD_REQUEST)

        if serializer.is_valid(self):
            serializer.save(following_id=following_id, user=request.user)
            following_user = User.objects.filter(
                    pk=following_id).values(
                        "email", "id", "username", "first_name", "last_name")
            following_user_recipes_pre = Recipe.objects.filter(
                    author=following_id)
            following_user_recipes = following_user_recipes_pre.values(
                    "id", "name", "image", "cooking_time")
            ri = 0
            for cur_recipe in following_user_recipes:
                recipe_image = utils.recipe_image_name_get(
                    following_user_recipes_pre[ri])
                for recipe_k, recipe_v in cur_recipe.items():
                    if recipe_k == 'image':
                        cur_recipe['image'] = recipe_image
                ri += 1
            following_user_recipes_count = following_user_recipes_pre.count()
            following_user_d = following_user[0]
            following_user_d["is_subscribed"] = True
            following_user_d["recipes"] = following_user_recipes
            following_user_d["recipes_count"] = following_user_recipes_count
            return Response(
                following_user_d, 
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  

    def destroy(self, request, **kwargs):
        following_id = kwargs['following_id']
        if Subscription.objects.filter(
                following_id=following_id, user=request.user).count() == 0:
            return Response(
                {"error": VALIDATION_ERRORS['USER_SUBSCRIBE_WRONG']},
                status=status.HTTP_400_BAD_REQUEST,
            )
        Subscription.objects.get(
                following_id=following_id, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

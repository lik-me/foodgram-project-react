from djoser.serializers import (TokenCreateSerializer, UserCreateSerializer,
                                UserSerializer)
from recipes import utils
from recipes.models import (Ingredients, Recipe, RecipeFavorited,
                            RecipeIngredient, ShoppingCart, Subscription, Tags)
from rest_framework import serializers
from users.models import User

from apps.settings import VALIDATION_ERRORS


class UserRegistrationSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        fields = ("email", "username", "first_name", "last_name", "password")
        read_only_fields = ['password']


class UserListSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = (
            "email", "id", "username",
            "first_name", "last_name",)
        read_only_fields = ['password']

    def to_representation(self, instance):
        data = super(UserListSerializer, self).to_representation(instance)
        data["is_subscribed"] = False
        if self.context.get('request') is not None:
            user = self.context['request'].user
            if str(user) != "AnonymousUser":
                for k, v in data.items():
                    if k == "id" and user.id != data[k]:
                        if Subscription.objects.filter(
                                user_id=user.id,
                                following_id=data[k]).count() != 0:
                            data["is_subscribed"] = True
            data = dict(data)
        return data


class UserTokenCreateSerializer(TokenCreateSerializer):

    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("password", "email",)

    def to_internal_value(self, data):
        user = User.objects.filter(email=data['email']).first()
        if user is None:
            raise serializers.ValidationError({
                "detail": [VALIDATION_ERRORS['USER_EMAIL_NOT_FOUND']]})
        check_password = user.check_password(data['password'])
        if check_password is False:
            raise serializers.ValidationError({
                "detail": [VALIDATION_ERRORS['USER_NAME_EMAIL_WRONG']]})
        return {
            'password': data['password'],
            'username': user.username
        }


class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "id", "username",
                  "first_name", "last_name",
                  )

    def to_representation(self, instance):
        data = super(UsersSerializer, self).to_representation(instance)
        data["is_subscribed"] = False
        if self.context.get('request') is not None:
            user = self.context['request'].user
            if str(user) != "AnonymousUser":
                for k, v in data.items():
                    if k == "id" and user.id != data[k]:
                        if Subscription.objects.filter(
                                user_id=user.id,
                                following_id=data[k]).count() != 0:
                            data["is_subscribed"] = True
            data = dict(data)
        return data


class UsersPasswordSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("password",)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tags
        fields = ("id", "name", "color", "slug")
        read_only_fields = ('name',)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredients
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')
    id = serializers.ReadOnlyField(source='ingredient.pk')
    amount = serializers.IntegerField(read_only=False, min_value=0)

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False, read_only=True)
    ingredients = RecipeIngredientSerializer(
        source="recipeingredient_set",
        many=True, required=True,
        read_only=False)
    author = UsersSerializer(many=False, required=False)
    is_favorited = serializers.BooleanField(default=False, read_only=False)
    is_in_shopping_cart = serializers.BooleanField(
        default=False,
        read_only=False)
    image = serializers.ImageField(
        max_length=None,
        allow_empty_file=False,
        use_url=False)

    class Meta:
        model = Recipe
        fields = (
            "id", "tags", "author",
            "ingredients", "is_favorited", "is_in_shopping_cart",
            "name", "image", "text", "cooking_time",)

    def to_representation(self, instance):
        data = super(RecipeSerializer, self).to_representation(instance)
        if self.context.get('request') is not None:
            user = self.context['request'].user
            data = dict(data)
            # without that convertation it's not possible
            # to update value in OrderedDict
            if str(user) != "AnonymousUser":
                for k, v in data.items():
                    if k == "id":
                        if RecipeFavorited.objects.filter(
                                user=user,
                                recipe_id=data[k]).count() != 0:
                            data["is_favorited"] = True
                        else:
                            data["is_favorited"] = False
                        if ShoppingCart.objects.filter(
                                user=user,
                                recipe_id=data[k]).count() != 0:
                            data["is_in_shopping_cart"] = True
                        else:
                            data["is_in_shopping_cart"] = False
                    elif k == "author":
                        following_id = data["author"]["id"]
                        if Subscription.objects.filter(
                                user=user,
                                following_id=following_id).count() != 0:
                            data["author"]["is_subscribed"] = True
                        else:
                            data["author"]["is_subscribed"] = False
        return data

    def to_internal_value(self, data):
        # print(self.instance.id)
        # print(self.context.get('id', None))
        # print(self.instance.__hash__())
        # print(self.instance)
        # print(self.context.get("image_already_saved"))
        image_already_saved = 0
        if self.context.get("image_already_saved") is not None:
            image_already_saved = 1
        required_fields = (
            "image", "name", "text",
            "cooking_time", "tags",
            "ingredients")
        for fld in required_fields:
            if fld not in data:
                raise serializers.ValidationError({
                    fld: [VALIDATION_ERRORS['FIELD_REQUIRED']]})
            elif data[fld] == "" or data[fld] is None:
                raise serializers.ValidationError({
                    fld: [VALIDATION_ERRORS['FIELD_REQUIRED']]})
            if fld == "ingredients":
                for ingredient in data[fld]:
                    if int(ingredient["amount"]) < 0:
                        raise serializers.ValidationError({
                            "amount":
                            [VALIDATION_ERRORS['RECIPE_AMOUNT_WRONG']]
                        })
            if fld == 'name' and len(data[fld]) > 200:
                raise serializers.ValidationError({
                    "name": [VALIDATION_ERRORS['RECIPE_NAME_WRONG']]})
            if fld == 'cooking_time' and int(data[fld]) < 1:
                raise serializers.ValidationError({
                    "cooking_time": [VALIDATION_ERRORS['COOKING_TIME_WRONG']]})
        image_data = data["image"]
        return {
            'image': image_data,
            'name': data['name'],
            'text': data['text'],
            'cooking_time': data['cooking_time'],
            'image_already_saved': image_already_saved
        }

    def update(self, instance, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        image = validated_data.pop("image")
        validated_data["image"] = 'null'
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time)
        instance.tags.clear()
        for tg in tags:
            instance.tags.add(tg)
        RecipeIngredient.objects.filter(recipe_id=instance.pk).delete()
        for ingr in ingredients:
            ingredient = Ingredients.objects.get(pk=ingr['id'])
            RecipeIngredient.objects.create(
                ingredient=ingredient,
                amount=ingr['amount'],
                recipe=instance)
        if validated_data.get('image_already_saved') == 0:
            image_info_to_save = utils.recipe_image_create(image, instance.id)
        else:
            image_info_to_save = image
        instance.image = image_info_to_save
        instance.save()
        return instance

    def create(self, validated_data):
        ingredients = validated_data.pop("ingredients")
        tags = validated_data.pop("tags")
        image = validated_data.pop("image")
        validated_data["image"] = 'null'
        validated_data.pop("image_already_saved")
        recipe = Recipe.objects.create(**validated_data)
        for tg in tags:
            recipe.tags.add(tg)

        for ingr in ingredients:
            ingredient = Ingredients.objects.get(pk=ingr['id'])
            RecipeIngredient.objects.create(
                ingredient=ingredient,
                amount=ingr['amount'],
                recipe=recipe)

        image_info_to_save = utils.recipe_image_create(image, recipe.id)
        recipe_new = Recipe.objects.get(pk=recipe.id)
        recipe_new.image = image_info_to_save
        recipe_new.save()
        return recipe_new


class RecipeShortSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ("id", "name", "cooking_time")


class ShoppingCartSerializer(serializers.ModelSerializer):

    class Meta:
        model = ShoppingCart
        fields = ("recipe_id",)


class RecipeFavoritedSerializer(serializers.ModelSerializer):

    class Meta:
        model = RecipeFavorited
        fields = ("recipe_id",)


class SubscriptionSerializerList(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
        ]

    def to_representation(self, instance):
        data = super(
            SubscriptionSerializerList,
            self).to_representation(instance)
        following_user_recipes_pre = Recipe.objects.filter(author=instance.id)
        data['is_subscribed'] = True
        if self.context.get("recipes_limit"):
            recipes_limit = int(self.context.get("recipes_limit"))
            following_user_recipes = following_user_recipes_pre.values(
                "id", "name", "image", "cooking_time")[:recipes_limit]
        else:
            following_user_recipes = following_user_recipes_pre.values(
                "id", "name", "image", "cooking_time")
        ri = 0
        for cur_recipe in following_user_recipes:
            for recipe_k, recipe_v in cur_recipe.items():
                if recipe_k == 'image':
                    recipe_image = utils.recipe_image_name_get(
                        following_user_recipes_pre[ri])
                    cur_recipe['image'] = recipe_image
            ri += 1
        following_user_recipes_count = following_user_recipes_pre.count()
        data["recipes"] = following_user_recipes
        data["recipes_count"] = following_user_recipes_count
        return data


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ("following_id",)

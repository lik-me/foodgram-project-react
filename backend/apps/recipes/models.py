from django.db import models
from users.models import User

from . import utils


class Ingredients(models.Model):
	name = models.TextField(
		help_text="Введите название ингредиента",
		verbose_name="Название ингредиента",
	)
	measurement_unit = models.TextField(
		help_text="Введите единицу измерения",
		verbose_name="Единица измерения",
	)

	class Meta:
		ordering = ["name"]
		verbose_name = "Ингредиент"
		verbose_name_plural = "Ингредиенты"

	def __str__(self):
		return self.name


class Tags(models.Model):
	name = models.TextField(
		max_length=100,
		help_text="Введите название тэга",
		verbose_name="Название тэга",
	)
	color = models.TextField(
		max_length=8,
		help_text="Укажите цвет тэга",
		verbose_name="Цвет",
	)
	slug = models.SlugField(
		max_length=50,
		unique=True,
		db_index=True,
	)

	class Meta:
		verbose_name = "Тег"
		verbose_name_plural = "Теги"

	def __str__(self):
		return self.name


class Recipe(models.Model):
	name = models.TextField(
		help_text="Введите название рецепта",
		verbose_name="Название рецепта",
		blank=False,
	)
	text = models.TextField(
		help_text="Введите описание рецепта",
		verbose_name="Описание рецепта",
		blank=False,
	)
	author = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name="recipes",
		verbose_name="Автор",
	)
	cooking_time = models.IntegerField(
		default=0,
		help_text="Укажите время приготовления в минутах",
		verbose_name="Время приготовления",
		blank=False,
	)
	pub_date = models.DateTimeField(
		auto_now_add=True,
		db_index=True,
	)
	image = models.ImageField(
		"Картинка",
		upload_to=utils.recipe_image_name,
		blank=False,
	)
	tags = models.ManyToManyField(
		Tags,
		related_name="tags",
		verbose_name="Тэги",
		blank=False,
	)
	ingredients = models.ManyToManyField(
		Ingredients,
		through='RecipeIngredient',
		related_name="ingredient",
		verbose_name="Ингредиенты",
	)

	class Meta:
		ordering = ["-pub_date"]
		verbose_name = "Рецепт"
		verbose_name_plural = "Рецепты"

	def __str__(self):
		return self.name


class RecipeIngredient(models.Model):
	recipe = models.ForeignKey(
		Recipe,
		on_delete=models.CASCADE,
		verbose_name="Рецепт",
	)
	ingredient = models.ForeignKey(
		Ingredients,
		on_delete=models.CASCADE,
		related_name="ingredient_name",
		verbose_name="Ингредиенты",
	)
	amount = models.IntegerField(
		default=0,
		help_text="Количество",
		verbose_name="Количество",
	)

	class Meta:
		verbose_name = "Ингредиенты"
		verbose_name_plural = "Ингредиенты"


class ShoppingCart(models.Model):
	recipe = models.ForeignKey(
		Recipe,
		on_delete=models.CASCADE,
		related_name="shopping_cart",
		verbose_name="Рецепт",
	)
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name="shopping_cart",
		verbose_name="Автор",
	)

	class Meta:
		unique_together = ('recipe', 'user',)
		verbose_name = "Список покупок"
		verbose_name_plural = "Списки покупок"

	def __str__(self):
		return f"{self.recipe.name}, {self.user.username}"


class RecipeFavorited(models.Model):
	recipe = models.ForeignKey(
		Recipe,
		on_delete=models.CASCADE,
		verbose_name="Рецепт",
	)
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name="recipe_favorited",
		verbose_name="Автор",
	)

	class Meta:
		unique_together = ('recipe', 'user',)
		verbose_name = "Избранное"
		verbose_name_plural = "Избранное"


class Subscription(models.Model):
	user = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name='follow',
	)
	following = models.ForeignKey(
		User,
		on_delete=models.CASCADE,
		related_name="following",
	)

	class Meta:
		unique_together = ('user', 'following',)
		verbose_name = "Подписка"
		verbose_name_plural = "Подписки"

import base64
import re
from os.path import join as path_join

from apps.settings import MEDIA_ROOT


def recipe_image_name(instance, filename):
    file_ext = filename[filename.rfind("."):]
    file_name = (f"{str(instance.id)}{file_ext}")
    return path_join('recipes', 'images', file_name)


def recipe_image_create(data, recipe_id):
    image_data = re.search(r'([^\/]*)/([^;]*);([^,]*),(.*)', data)
    decoded_image_data = base64.b64decode(image_data[4])
    f = open(path_join(
        MEDIA_ROOT, 'recipes', 'images',
        f"{recipe_id}.{image_data[2]}"), 'wb')
    f.write(decoded_image_data)
    f.close()
    return f"/recipes/images/{recipe_id}.{image_data[2]}"


def recipe_image_name_get(recipe_instance):
    recipe_image = str(recipe_instance.image)
    recipe_id = str(recipe_instance.id)
    file_ext = recipe_image[recipe_image.rfind("."):]
    file_name = f"{str(recipe_id)}{file_ext}"
    return path_join('recipes', 'images', file_name)


def recipe_serializer_response_update(data_to_response):
    data_to_response_new_order = {}
    ingredients = data_to_response["ingredients"]
    for ingredient in ingredients:
        ingredient.pop("name")
        ingredient.pop("measurement_unit")
    data_to_response_new_order["ingredients"] = ingredients
    tags = data_to_response.pop("tags")
    tags_new = []
    for tag in tags:
        tags_new.append(tag["id"])
    data_to_response_new_order["tags"] = tags_new
    data_to_response_new_order["image"] = data_to_response.pop("image")
    data_to_response_new_order["name"] = data_to_response.pop("name")
    data_to_response_new_order["text"] = data_to_response.pop("text")
    data_to_response_new_order["cooking_time"] = (
        data_to_response.pop("cooking_time"))
    return data_to_response_new_order

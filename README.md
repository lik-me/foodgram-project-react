# Проект Foodgram 
### Описание
Foodgram - социальная сеть для публикации клинарных рецептов.
Пользователи имеют возможность публиковать свои рецепты и получать доступ к рецептам других пользователей сети.
Среди полезных опций отметим такие:
- формирование списков избранных рецептов, 
- подписка на других участниуов сети,
- формирование удобного списка покупок с возможность сохранить его в виде отдельного файла.


Деплой проекта на on-line сервер осуществляется с помощью технологии контейнеризации Docker.

### Технологии
Python 3.7
Django 2.2.19
Django Rest Framework 3.12.4
Postgres
Gunicorn 20.0.4
React

# После запуска приложения в контейнере 
- выполните миграции,
- создайте суперпользователя,
- перенесите статичный контент,
- войдите в админку,
- создайте одну-две записи объектов.

```
sudo docker-compose exec web python manage.py migrate
sudo docker-compose exec web python manage.py createsuperuser
sudo docker-compose exec web python manage.py collectstatic
http://51.250.70.5/admin/
```

# Примеры API
```
http://51.250.70.5/redoc/
```


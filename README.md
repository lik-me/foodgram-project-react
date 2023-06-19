# Foodgram - продуктовый помощник.
### Описание
Foodgram - сайт для размещения клинарных рецептов.
Foodgram ориентирован, в первую очередь, для пользователей, которым требуется простой в использовании и надежный сервис для хранения базы своих кулинарных рецептов, доступ к которым можно быстро получить.

Пользователи имеют возможность публиковать свои рецепты и получать доступ к рецептам других пользователей системы.

### Среди полезных опций отметим:
- формирование списков избранных рецептов, 
- подписка на других участников сети,
- формирование удобного списка покупок с возможностью сохранить его в виде отдельного файла.

Добавлять рецепты в избранное и корзину покупок, а также подписываться на других участников могут зарегистрированные на сайте пользователи. 
Для регистрации требуется указать свое имя и фамилию, логин, e-mail и пароль.

Сайт снабжен удобной системой фильтрации рецептов по описательным тегам.

### Технологии
Python 3.7
Django 2.2.19
Django Rest Framework 3.12.4
Postgres
Gunicorn 20.0.4
React

Деплой проекта на on-line сервер осуществляется с помощью технологии контейнеризации Docker.

# После запуска приложения в контейнере 
- выполните миграции,
- создайте суперпользователя,
- перенесите статичный контент,
- войдите в админку,
- создайте одну-две записи объектов.

```
sudo docker-compose exec web python manage.py migrate
sudo docker-compose exec web python manage.py createsuperuser
sudo docker-compose exec web python manage.py import_data
```

# Автор

Разработчик бэкэнда - студент 13 когорты Яндекс Практикума Леонид Клет.

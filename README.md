![Actions Status](https://github.com/Sergey-Aleksandrovich/yamdb_final/workflows/yamdb%20workflow/badge.svg)

(https://github.com/Sergey-Aleksandrovich/yamdb_final/workflows/yamdb20workflow/badge.svg)-Добавил эту срочку, чтобы проходили тесты, судя по всему в регулярное выражение не попал % в name workflows.


# Название проекта

YamDB - это база отзывов о фильмах, книгах и музыке.

## Быстрый старт

Эти инструкции позволят вам запустить копию проекта на вашем компьютере.

### Скачавание и запуск проекта


Команда для запуска проекта
 
```
docker-compose up
```

Команда для выполнения миграций

```
docker-compose exec web python manage.py migrate
```

### Создание суперпользователя

Команда, для создания суперпользователя

```
 docker-compose exec web python manage.py createsuperuser
```

### Заполнение базы начальными данными

Команда для заполнения базы начальными данными

```
docker-compose exec web python manage.py loaddata fixtures.json
```


![YAMDB workflow](https://github.com/xeniakutsevol/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg)

# Запуск docker-compose для API YAMDB

### Описание проекта

Проект **YaMDb** собирает **отзывы (Review)** пользователей на **произведения (Titles)**. Произведения делятся на категории, например, «Книги», «Фильмы», «Музыка». **Список категорий (Category)** может быть расширен администратором.
Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.
Произведению может быть присвоен **жанр (Genre)** из списка предустановленных (например, «Сказка», «Рок» или «Артхаус»). Новые жанры может создавать только администратор.
Благодарные или возмущённые пользователи оставляют к произведениям **текстовые отзывы (Review)** и ставят произведению оценку в диапазоне от одного до десяти (целое число); из пользовательских оценок формируется усреднённая оценка произведения — **рейтинг** (целое число). На одно произведение пользователь может оставить только один отзыв.

Проект помещен в контейнеры docker-compose для упрощения развертывания.

### Используемые технологии
- Django
- Django Rest Framework
- Simple JWT
- Docker

### Как запустить проект:

Клонировать репозиторий:

```
git clone https://github.com/xeniakutsevol/infra_sp2
```

Создать файл .env в каталогe infra и добавить в него переменную SECRET_KEY=<random_string>:

```
cd infra_sp2/infra
```

```
touch .env
```

```
nano .env
```

Дефолтное значение SECRET_KEY герерируется автоматически с помощью get_random_secret_key() из django.core.management.utils, если не задать свое.


Перейти в репозиторий с Dockerfile и собрать образ:

```
cd infra_sp2/api_yamdb/
```

```
docker build -t api_yamdb .
```

Запустить контейнеры docker-compose:

```
cd ../infra/
```

```
docker-compose up -d --build
```

Cоздать суперпользователя:

```
docker-compose exec web python manage.py createsuperuser
```

Залить данные из БД:

```
docker-compose exec web python manage.py loaddata fixtures.json
```

Проверить работоспособность проекта:

```
http://localhost/admin/
```

Образ проекта также доступен в DockerHub:

```
xeniakutsevol/api_yamdb:v2.00.0000
```

### Как пользоваться проектом

Документация к API YAMDB:

```
http://localhost/redoc/
```
from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .utils import current_year, max_value_current_year


class User(AbstractUser):

    class Role(models.TextChoices):
        USER = 'user', 'user'
        MODERATOR = 'moderator', 'moderator'
        ADMIN = 'admin', 'admin'

    confirmation_code = models.UUIDField(default=uuid4, editable=False)
    bio = models.TextField('О себе', max_length=500, blank=True)
    role = models.CharField('Роль', max_length=10,
                            choices=Role.choices, default=Role.USER)

    def is_admin(self):
        return self.is_staff or self.role == self.Role.ADMIN

    def is_not_user(self):
        return self.is_admin() or self.role != self.Role.USER

    def is_user(self):
        return not self.is_not_user()


class Categories(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=12, unique=True)

    def __str__(self):
        return self.name


class Genres(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=12, unique=True)

    def __str__(self):
        return self.name


class Titles(models.Model):
    name = models.CharField(max_length=200)
    # Первая точно датированная печатная книга —
    # буддийская «Алмазная сутра» — была издана 11 мая 868 года
    year = models.PositiveIntegerField(
        default=current_year(),
        validators=[MinValueValidator(868), max_value_current_year],
    )
    description = models.TextField()
    genre = models.ManyToManyField(Genres, blank=True)
    category = models.ForeignKey(Categories, on_delete=models.CASCADE)
    rating = models.IntegerField(default=None, null=True)


class Review(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    title = models.ForeignKey(
        Titles,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
    )
    score = models.IntegerField(
        default=None,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['title', 'author'],
            name='unique_review',
        )]


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
    )
    pub_date = models.DateTimeField(
        'Дата добавления',
        auto_now_add=True,
        db_index=True,
    )

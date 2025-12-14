from django.db import models
from django.conf import settings
from .validators import (
    validate_price_not_zero,
    validate_phone_number,
    validate_no_bad_words,
    validate_price_range,
    validate_text_length_min_5_max_50,
    validate_text_length_min_20_max_5000
)

class Rubric(models.Model):
    name = models.CharField(max_length=20, db_index=True, verbose_name='Название')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Рубрики'
        verbose_name = 'Рубрика'
        ordering = ['name']

class Bb(models.Model):
    rubric = models.ForeignKey(Rubric, null=True, on_delete=models.PROTECT, verbose_name='Рубрика')
    title = models.CharField(
        max_length=50,
        verbose_name='Товар',
        validators=[validate_no_bad_words, validate_text_length_min_5_max_50]
    )
    content = models.TextField(
        verbose_name='Описание',
        validators=[validate_text_length_min_20_max_5000]
    )
    price = models.FloatField(
        verbose_name='Цена',
        validators=[
            validate_price_not_zero,
            validate_price_range
        ]
    )
    published = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Опубликовано')

    class Meta:
        verbose_name_plural = 'Объявления'
        verbose_name = 'Объявление'
        ordering = ['-published']
        constraints = [
            models.CheckConstraint(
                check=models.Q(price__gte=0),
                name='price_not_negative'
            ),
        ]

    def __str__(self):
        return self.title


    def clean(self):
        from django.core.exceptions import ValidationError
        errors = {}

        if self.rubric and self.rubric.name == 'Недвижимость' and self.price > 1000000:
            errors['price'] = ValidationError(
                'Цена недвижимости не должна превышать 1 000 000',
                code='real_estate_price_limit'
            )

        if self.price > 10000 and len(self.title) < 10:
            errors['title'] = ValidationError(
                'Для дорогих товаров заголовок должен быть более подробным',
                code='expensive_item_title'
            )

        if errors:
            raise ValidationError(errors)


# 3. One-to-One связь (с пользователем)
class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    phone = models.CharField(
        max_length=15,
        verbose_name='Телефон',
        validators=[validate_phone_number]
    )
    address = models.TextField(verbose_name='Адрес')

    def __str__(self):
        return f"Профиль {self.user.username}"

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'


# 4. Many-to-Many связь (теги для объявлений)
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, verbose_name='Название тега')
    bbs = models.ManyToManyField(Bb, related_name='tags', verbose_name='Объявления')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


# 5. Self-referential ForeignKey (иерархия рубрик)
class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название категории')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Родительская категория'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'


# 6. Self-referential Many-to-Many (друзья между пользователями)
class Friend(models.Model):
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='friends',
        verbose_name='Друзья'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Друг'
        verbose_name_plural = 'Друзья'

    def __str__(self):
        return f"Группа друзей {self.id}"


# 7. Связь через промежуточную модель (Many-to-Many с дополнительными полями)
class Order(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь'
    )
    bbs = models.ManyToManyField(
        Bb,
        through='OrderItem',
        verbose_name='Товары в заказе'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата заказа')
    total_price = models.FloatField(verbose_name='Общая стоимость')

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ')
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, verbose_name='Товар')
    quantity = models.IntegerField(default=1, verbose_name='Количество')
    price_at_order = models.FloatField(verbose_name='Цена на момент заказа')

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'
        unique_together = ('order', 'bb')

    def __str__(self):
        return f"{self.bb.title} в заказе #{self.order.id}"
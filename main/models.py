from django.core.validators import MaxLengthValidator
from django.db import models
from django.db import transaction
from math import log, sqrt


# Create your models here.
class Citation(models.Model):
    # unique - уникальность, validators - защита от спама (ограничение количества символов)
    text = models.TextField(unique=True, validators=[MaxLengthValidator(2000)], db_index=True)

    # ограничение размера источника для эффективного использования памяти БД
    source = models.CharField(max_length=255, db_index=True)

    # исключаем дроби и отрицательные значения (+быстродействие БД)
    weight = models.PositiveIntegerField(default=1, db_index=True)

    # db_index - ускорение производительности запросов
    likes = models.PositiveIntegerField(default=0, db_index=True)
    dislikes = models.PositiveIntegerField(default=0, db_index=True)
    views = models.PositiveIntegerField(default=0, db_index=True)

    MIN_WEIGHT = 1  # Минимальное значение веса

    #  Для администратора отображение будет в отсортированном формате по лайкам
    class Meta:
        ordering = ('likes',)
        indexes = [
            models.Index(fields=['weight']),
            models.Index(fields=['likes']),
            models.Index(fields=['dislikes']),
        ]

    def __str__(self):
        return f"{self.text} - {self.source}"

    # Чтобы избежать race conditions (гонка) - несколько пользователей взаимодействуют одновременно с цитатой
    # При использовании transaction.atomic пока один выполняет код функции, другой ждет (БД блокируется)
    @transaction.atomic
    def process_like(self):
        self.likes += 1
        delta = max(1, int(log(self.likes + 1, 2)))
        self.weight += delta
        self.save(update_fields=['likes', 'weight'])

    @transaction.atomic
    def process_dislike(self):
        current_weight = type(self).objects.filter(pk=self.pk).values_list('weight', flat=True).first()
        safe_value = min(int(sqrt(self.dislikes + 1)),
                         current_weight - self.MIN_WEIGHT) if current_weight > self.MIN_WEIGHT else 0

        self.dislikes += 1
        if safe_value > 0:
            self.weight -= safe_value
            self.save(update_fields=['dislikes', 'weight'])
        else:
            self.save(update_fields=['dislikes'])

    @transaction.atomic
    def process_view(self):
        self.views += 1
        if self.views % 10 == 0:
            self.weight += 1
        self.save(update_fields=['views', 'weight'])

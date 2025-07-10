from django.core.validators import MaxLengthValidator
from django.db import models


# Create your models here.
class Citation(models.Model):
    # unique - уникальность, validators - защита от спама (ограничение количества символов)
    text = models.TextField(unique=True, validators=[MaxLengthValidator(2000)])
    source = models.CharField(max_length=255)  # ограничение размера источника для эффективного использования памяти БД
    weight = models.PositiveIntegerField(default=1)  # исключаем дроби и отрицательные значения (+быстродействие БД)
    likes = models.PositiveIntegerField(default=0, db_index=True)  # db_index - ускорение производительности запросов
    dislikes = models.PositiveIntegerField(default=0)
    views = models.PositiveIntegerField(default=0)

    #  Для администратора отображение будет в отсортированном формате по лайкам
    class Meta:
        ordering = ('likes', )

    def __str__(self):
        return f"{self.text} - {self.source}"

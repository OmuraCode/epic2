from django.db import models


class News(models.Model):
    title = models.CharField(max_length=255, unique=True)
    image = models.URLField()
    link = models.URLField()

    class Meta:
        verbose_name = 'news'
        verbose_name_plural = 'news'

    def __str__(self):
        return self.title

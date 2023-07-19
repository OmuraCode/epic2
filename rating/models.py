from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from posts.models import Post


class Mark(models.Model):
    owner = models.ForeignKey('account.CustomUser', related_name='marks', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='marks', on_delete=models.CASCADE)
    mark = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        default=0,
        null=True,
        blank=True
    )

    class Meta:
        unique_together = ['owner', 'post']
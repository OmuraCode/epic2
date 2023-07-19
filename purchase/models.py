from django.db import models

from posts.models import Post


class Purchase(models.Model):
    owner = models.ForeignKey('account.CustomUser', related_name='purchase', on_delete=models.CASCADE)
    post = models.ForeignKey(Post, related_name='purchase', on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'purchase'
        verbose_name_plural = 'purchases'

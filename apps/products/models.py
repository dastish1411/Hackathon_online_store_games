from distutils.command.upload import upload
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from slugify import slugify


User = get_user_model()


class Products(models.Model):
    user = models.ForeignKey(
        verbose_name='Владелец игр',
        to=User,
        on_delete=models.CASCADE,
        related_name='publications'
    )

    title = models.CharField(max_length=150)
    slug = models.SlugField(max_length=170, primary_key=True, blank=True)
    description = models.TextField()
    image = models.ImageField(upload_to='post_images')
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)

    def  __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    class Meta:
        ordering = ('created_at',)

    def get_absolute_url(self):
        return reverse('products-detail', kwargs={'pk': self.pk})


class ProductsImage(models.Model):
    image = models.ImageField(upload_to='post_images')
    products = models.ForeignKey(
        ro=Products,
        on_delete=models.CASCADE,
        related_name='post_images'
    )


class Like(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    products = models.ForeignKey(
        to=Products,
        on_delete=models.CASCADE,
        related_name='likes'
    )

    def __str__(self) -> str:
        return f'Liked by {self.user.username}'



class Rating(models.Model):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    RATING_CHOICES = (
        (ONE, '1'),
        (TWO, '2'),
        (THREE, '3'),
        (FOUR, '4'),
        (FIVE, '5')
    )

    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES,
        blank=True,
        null=True
    )
    products = models.ForeignKey(
        to=Products,
        on_delete=models.CASCADE,
        related_name='ratings'
    )

    def __str__(self):
        return str(self.rating)


class Comment(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    products = models.ForeignKey(
        to=Products,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment from {self.user.username} to {self.post.title}'
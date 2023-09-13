from django.core.cache import cache
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from datetime import datetime



article = 'AR'
news = 'NW'

Type = [
    (article, 'Статья'),
    (news, 'Новость')
]


class Appointment(models.Model):
    date = models.DateField(
        default=datetime.utcnow,
    )
    client_name = models.CharField(
        max_length=200
    )
    message = models.TextField()

    def __str__(self):
        return f'{self.client_name}: {self.message}'


class Author(models.Model):
    name = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    user_rating = models.IntegerField(default=0)

    def update_rating(self):
        comment_rating = Comment.objects.filter(user_id=self.users.id).aggregate(models.Sum('rating'))['rating__sum']
        posts_rating = Post.objects.filter(author_id=self).aggregate(models.Sum('rating'))
        post_id = Post.objects.filter(author_id=self).values_list('id', flat=True)
        rating_comment_to_posts = Comment.objects.filter(post_id__in=post_id).aggregate(models.Sum('rating'))[
            'rating__sum']
        self.user_rating = (int(posts_rating['rating__sum']) * 3) + int(comment_rating) + int(rating_comment_to_posts)
        self.save()


class Category(models.Model):
    name = models.CharField(max_length = 255,
                            unique = True)
    subscribers = models.ManyToManyField(User, blank=True, related_name='categories')

    def __str__(self):
        return self.name.title()

    def get_absolute_url(self):
        return reverse('add_category')


class Post(models.Model):

    news = 'NW'
    article = 'AR'

    time_in = models.DateTimeField(auto_now_add = True)
    time_update = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length = 100)
    author = models.ForeignKey(Author, default=1, on_delete = models.SET_DEFAULT)
    category = models.ManyToManyField(Category, through = 'PostCategory')
    title = models.CharField(max_length = 255)
    text = models.TextField()
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()

    def preview(self):
        text = self.text[:124]
        if len(self.text) > 124:
            text += '...'
        return text

    def __str__(self):
        return f'{self.title.title()}: {self.text[:20]}'

    def get_absolute_url(self):
        return f'/news/{self.id}'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'post-{self.pk}')


class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    category = models.ForeignKey(Category, on_delete = models.CASCADE, related_name='post_category')


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete = models.CASCADE)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    text = models.TextField()
    time_in = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField(default=0)

    def like(self):
        self.rating += 1
        self.save()

    def dislike(self):
        self.rating -= 1
        self.save()


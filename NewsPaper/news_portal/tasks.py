from datetime import datetime
from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from .models import Post, Category

from django.conf import settings


from celery import shared_task


@shared_task
def send_post_for_subscribers_celery(post):
    categories = post.category.all()
    subscribers_all = []
    for category in categories:
        subscribers_all += category.subscribers.all()
    subscribers_list = {}
    for person in subscribers_all:
        subscribers_list[person.username] = person.email
    for name, email in subscribers_list.items():
        html_content = render_to_string('posts/post_for_subscribers.html',
                                        {'text': post.text[:50],
                                         "link": f'http://127.0.0.1:8000/post/{post.pk}',
                                         "user":name})
        print(name)
        print(email)
        message = EmailMultiAlternatives(
            subject=post.title,
            body=post.text[:50],
            from_email='Scotcher2@yandex.ru',
            to=email
        )
        message.attach_alternative(html_content, "text/html")  # добавляем htm
        message.send()
@shared_task
def weekly_post():
    today = datetime.datetime.now()
    day_week_ago = today - datetime.timedelta(days=7)
    posts = Post.objects.filter(date_post__gte=day_week_ago)
    categories = set(posts.values_list('category__name', flat=True))
    subscribers = set(Category.objects.filter(name__in=categories).values_list('subscribe__email', flat=True))

    html_content = render_to_string('category/category_post_subscribe.html',{
            'link': f'http://127.0.0.1:8000',
            'posts': posts,
        }
    )
    msg = EmailMultiAlternatives(
        subject="Новости за неделю",
        body='',
        from_email=f'{settings.EMAIL_HOST_USER}@yandex.ru',
        to=[subscribers]
    )
    msg.attach_alternative(html_content, 'text/html')
    msg.send()
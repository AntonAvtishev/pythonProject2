from django.conf import settings
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver  # импортируем нужный декоратор
from .models import Post
from .tasks import send_post_for_subscribers_celery


# в декоратор передаётся первым аргументом сигнал, на который будет реагировать эта функция, и в отправители надо передать также модель
@receiver(m2m_changed, sender=Post.category.through)
def category_post(sender, instance,  **kwargs):
    send_post_for_subscribers_celery(instance)

# @receiver(m2m_changed, sender=Post.category.through)
# def category_post(sender, instance,  **kwargs):
#     # if created:
#     categories=instance.category.all()
#     post=instance
#
#     print(categories)
#     print(post)
#
#     for category in categories:
#         for user in category.subscribers.all():
#             print(user)
#
#             html_content = render_to_string(
#                 'category/category_post_subscribe.html',
#                 {
#                     'category': category.name,
#                     'post':instance
#                 }
#             )
#             msg = EmailMultiAlternatives(
#                 subject=f'В категории: { category.name } появилась новая запись {instance.title}!',
#                 body=instance.text,
#                 from_email=f'{settings.EMAIL_HOST_USER}@yandex.ru',
#                 to=[f'{settings.EMAIL_HOST_USER}@yandex.ru']
#             )
#             msg.attach_alternative(html_content,  "text/html")
#
#             msg.send()
#

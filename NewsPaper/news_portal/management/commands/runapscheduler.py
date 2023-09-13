import datetime
import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

from news_portal.models import Category, Post


logger = logging.getLogger(__name__)


# наша задача по выводу текста на экран
def my_job():
    #  Your job processing logic here...
    print('hello from job')
    time_delta = datetime.timedelta(7)
    print(time_delta)
    start_date = datetime.datetime.utcnow() - time_delta
    print(start_date)
    end_date = datetime.datetime.utcnow()
    print(end_date)
    for category in Category.objects.all():
        posts = Post.objects.filter(
            time_in__range=(start_date,
                            end_date),
                        category=category
        )
        if posts:
            for user in category.subscribers.all():
                html_content = render_to_string(
                    'category/category_post_seven.html',
                    {
                        'category': category,
                        'posts': posts
                    }
                )
                msg = EmailMultiAlternatives(
                    subject=f'В категории: { category.name } появились новости за неделю!',
                    body='Подписка за 7 дней',
                    from_email=f'{settings.EMAIL_HOST_USER}@yandex.ru',
                    to=[f'{settings.EMAIL_HOST_USER}@yandex.ru']
                )
                msg.attach_alternative(html_content,  "text/html")

                msg.send()



# функция, которая будет удалять неактуальные задачи
def delete_old_job_executions(max_age=604_800):
    """This job deletes all apscheduler job executions older than `max_age` from the database."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs apscheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # добавляем работу нашему задачнику
        scheduler.add_job(
            my_job,
            trigger=CronTrigger(second="*/10"),
            # То же, что и интервал, но задача тригера таким образом более понятна django
            id="my_job",  # уникальный айди
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'my_job'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
            # Каждую неделю будут удаляться старые задачи, которые либо не удалось выполнить, либо уже выполнять не надо.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info(
            "Added weekly job: 'delete_old_job_executions'."
        )

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
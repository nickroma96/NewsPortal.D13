from celery import shared_task
import time
import instance


@shared_task
def hello():
    time.sleep(10)
    print("Hello, world!")


@shared_task
def printer(N):
    for i in range(N):
        time.sleep(1)
        print(i+1)


@shared_task
def send_mail_for_sub_test():
    # time.sleep(10)
    print("Отправка письма, проверка1")
    # send_mail_for_sub(instance)
    print("Отправка письма, проверка2")
from io import BytesIO
from celery import shared_task
import weasyprint
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.conf import settings
from orders.models import Order


@shared_task
def payment_completed(order_id):
    """
    Задание по отправке уведомления по электронной почте
    при успешной оплате заказа.
    """
    order = Order.objects.get(id=order_id)
    # create invoice e-mail
    subject = f'My Shop – Invoice no. {order.id}'
    message = 'Please, find attached the invoice for your recent purchase.'
    email = EmailMessage(subject,
                         message,
                         'admin@myshop.com',
                         [order.email])
    # сгенерировать PDF
    html = render_to_string('orders/order/pdf.html', {'order': order})
    out = BytesIO()
    stylesheets = [weasyprint.CSS(settings.STATIC_ROOT / 'css/pdf.css')]
    weasyprint.HTML(string=html).write_pdf(out,
                                           stylesheets=stylesheets)
    # прикрепить PDF-файл
    email.attach(f'order_{order.id}.pdf',
                 out.getvalue(),
                 'application/pdf')
    # отправить электронное письмо
    email.send()


"""
С помощью декоратора @shared_task определяется задание payment_completed.
В этом задании используется предоставляемый веб-фреймворком
Django класс EmailMessage, служащий для создания объекта email. Затем шаб-
лон прорисовывается в переменную html и из прорисованного шаблона ге-
нерируется PDF-файл, который выводится в экземпляр aBytesIO. Последний
представляет собой резидентный байтовый буфер. Затем с по мощью метода
attach() сгенерированный PDF-файл прикрепляется к объекту EmailMessage
вместе с содержимым выходного буфера. Наконец, письмо отправляется.
Не забудьте настроить параметры простого протокола передачи почты
(SMTP) в файле settings.py проекта, чтобы отправлять электронные письма. Задание payment_completed ставится в очередь путем вызова его метода
delay(). Задание будет добавлено в очередь и исполнено асинхронно работ-
ником Celery как можно раньше."""

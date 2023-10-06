import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            settings.STRIPE_WEBHOOK_SECRET)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    if event.type == 'checkout.session.completed':
        session = event.data.object
        if session.mode == 'payment' and session.payment_status == 'paid':
            try:
                order = Order.objects.get(id=session.client_reference_id)
            except Order.DoesNotExist:
                return HttpResponse(status=404)
            # Mark the order as paid
            order.paid = True
            order.stripe_id = session.payment_intent
            order.save()

    return HttpResponse(status=200)
"""
В новом исходном коде проверяется, что полученным событием является
checkout.session.completed. Это событие указывает на успешное завершение
сеанса оформления платежа. Если наступает это событие, то извлекается
сеансовый объект и делается проверка, не является ли режим (mode) сеанса
платежным (payment), поскольку это ожидаемый режим для разовых плате-
жей. Затем извлекается атрибут client_reference_id, который использовался
при создании сеанса оформления платежа, и задействуется преобразова-
телем Django ORM, чтобы получить объект Order с данным id. Если заказ не
существует, то вызывается исключение HTTP 404. В противном случае по-
средством инструкции order.paid = True заказ помечается как оплаченный
и сохраняется в базе данных."""


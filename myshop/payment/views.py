from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
import stripe
from orders.models import Order


def payment_process(request):
    order_id = request.session.get('order_id', None)
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        success_url = request.build_absolute_uri(reverse('payment:completed'))
        cancel_url = request.build_absolute_uri(reverse('payment:canceled'))

        # Данные сеанса оформления платежа Stripe
        session_data = {
            'mode': 'payment',
            'client_reference_id': order.id,
            'success_url': success_url,
            'cancel_url': cancel_url,
            'line_items': []
        }
        # добавить товарные позиции заказа
        # в сеанс оформления платежа Stripe
        for item in order.items.all():
            session_data['line_items'].append({
                'price_data': {
                    'unit_amount': int(item.price * Decimal('100')),
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                    },
                },
                'quantity': item.quantity,
            })

        # Создать сеанс оформления платежа Stripe
        session = stripe.checkout.Session.create(**session_data)

        # Перенаправить к платежной форме Stripe
        return redirect(session.url, code=303)

    else:
        return render(request, 'payment/process.html', locals())


"""
В приведенном выше исходном коде импортируется модуль stripe и с по-
мощью значения настроечного параметра STRIPE_SECRET_KEY задается ключ
API Stripe. Кроме того, с по мощью значения настроечного параметра STRIPE_
API_VERSION задается используемая версия API.
Представление payment_process выполняет следующую работу.
1. Текущий объект Order извлекается по сеансовому ключу order_id, кото-
рый ранее был сохранен в сеансе представлением order_create.
2. Объект Order извлекается из базы данных по данному order_id. Если при
использовании функции сокращенного доступа get_object_ or_404()
возникает исключение Http404 (страница не найдена), то заказ с задан-
ным ИД не найден.
3. Если представление загружается с по мощью запроса методом GET, то
прорисовывается и возвращается шаблон payment/process.html. Этот
шаблон будет содержать сводную информацию о заказе и кнопку для
перехода к платежу, которая будет генерировать запрос методом POST
к представлению.
4. Если представление загружается с по мощью запроса методом POST, то
сеанс Stripe оформления платежа создается с использованием Stripe.
checkout.Session.create() со следующими ниже параметрами:
– mode: режим сеанса оформления платежа. Здесь используется значе-
ние payment, указывающее на разовый платеж. На странице https://
stripe.com/docs/api/checkout/sessions/object#checkout_session_objectmode
можно увидеть другие принятые для этого параметра зна-
чения;
– client_reference_id: уникальная ссылка для этого платежа. Она будет
использоваться для согласования сеанса оформления платежа Stripe
с заказом. Передавая ИД заказа, платежи Stripe связываются с зака-зами в вашей системе, и вы сможете получать уведомления от Stripe
о платежах, чтобы помечать заказы как оплаченные;
– success_url: URL-адрес, на который Stripe перенаправляет пользо-
вателя в случае успешного платежа. Здесь используется request.
build_absolute_uri(), чтобы формировать абсолютный URI-иден ти-
фи катор из пути URL-адреса. Документация по этому методу на-
ходится по адресу https://docs.djangoproject.com/en/4.1/ref/requestresponse/#
django.http.HttpRequest.build_absolute_uri;
– cancel_url: URL-адрес, на который Stripe перенаправляет пользова-
теля в случае отмены платежа;
– line_items: это пустой список. Далее он будет заполнен приобретае-
мыми товарными позициями заказа.После создания сеанса оформления платежа возвращается HTTP-
перенаправление с кодом состояния, равным 303, чтобы перенаправить
пользователя к Stripe. Код состояния 303 рекомендуется для перена-
правления веб-приложений на новый URI-идентификатор после вы-
полнения HTTP-запроса методом POST."""


def payment_completed(request):
    return render(request, 'payment/completed.html')


def payment_canceled(request):
    return render(request, 'payment/canceled.html')

from django.shortcuts import render, redirect
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created
from django.urls import reverse


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         product=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'])
            # очистить корзину
            cart.clear()
            # запустить асинхронное задание
            order_created.delay(order.id)
            # задать заказ в сеансе
            request.session['order_id'] = order.id
            # перенаправить к платежу
            return redirect(reverse('payment:process'))
    else:
        form = OrderCreateForm()
    return render(request,
                  'orders/order/create.html',
                  {'cart': cart, 'form': form})


"""
В представлении order_create текущая корзина извлекается из сеанса по-
средством инструкции cart = Cart(request).
В зависимости от метода запроса выполняется следующая работа:
• запрос методом GET: создает экземпляр формы OrderCreateForm и про-
рисовывает шаблон orders/order/create.html;
• запрос методом POST: выполняет валидацию отправленных в запросе
данных. Если данные валидны, то в базе данных создается новый заказ,
используя инструкцию order = form.save(). Товарные позиции корзины прокручиваются в цикле, и для каждой из них создается OrderItem. На-
конец, содержимое корзины очищается, и шаблон orders/order/created.
html прорисовывается.

При размещении нового заказа вместо прорисовки шаблона orders/order/
created.html ИД заказа сохраняется в сеансе пользователя, и пользователь
перенаправляется на URL-адрес payment:process.  Напомним, что для того, чтобы задание order_created было
поставлено в очередь и исполнено, программа Celery должна работать"""

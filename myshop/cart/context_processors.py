from .cart import Cart


def cart(request):
    return {'cart': Cart(request)}
"""
Здесь в процессоре контекста создается экземпляр класса Сart с объектом
request в качестве параметра и обеспечивается его доступность для шаблонов
в виде переменной cart."""
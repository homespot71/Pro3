from django.shortcuts import render, get_object_or_404
from .models import Category, Product
from cart.forms import CartAddProductForm


def product_list(request, category_slug=None):
    category = None
    categories = Category.objects.all()
    products = Product.objects.filter(available=True)
    if category_slug:
        category = get_object_or_404(Category,
                                     slug=category_slug)
        products = products.filter(category=category)
    return render(request,
                  'shop/product/list.html',
                  {'category': category,
                   'categories': categories,
                   'products': products})


"""
В приведенном выше исходном коде набор запросов QuerySet фильтрует-
ся с параметром available=True, чтобы получать только те товары, которые
имеются в наличии. Опциональный параметр category_slug используется для
дополнительной фильтрации товаров по заданной категории."""


def product_detail(request, id, slug):
    product = get_object_or_404(Product,
                                id=id,
                                slug=slug,
                                available=True)
    cart_product_form = CartAddProductForm()
    return render(request,
                  'shop/product/detail.html',
                  {'product': product, 'cart_product_form': cart_product_form})


"""
На вход в представление product_detail должны передаваться параметры
id и slug, чтобы извлекать экземпляр класса Product. Указанный экземпляр
можно получить только по ИД, так как это уникальный атрибут. Однако
в URL-адрес еще включается слаг, чтобы формировать дружественные для
поисковой оптимизации URL-адреса товаров."""

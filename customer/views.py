from django.shortcuts import redirect, render
from .models import *
from django.conf import settings
# Create your views here.
from django.core.mail import send_mail
from django.views import View
import json

class Index(View):
    def get(self,request,*args, **kwargs):
        return render(request,'customer/index.html')

class About(View):
    def get(self,request,*args, **kwargs):
        return render(request,'customer/about.html')

class Order(View):
    def get(self,request,*args, **kwargs):
        ML6=Item.objects.filter(category__name__contains='ML-6')
        M24=Item.objects.filter(category__name__contains='M-24')
        M6=Item.objects.filter(category__name__contains='M-6')
        M9=Item.objects.filter(category__name__contains='M-9')
        M15=Item.objects.filter(category__name__contains='M-15')

        context={
            'ML6':ML6,
            'M24':M24,
            'M6':M6,
            'M9':M9,
            'M15':M15,


        }

        return render (request,'customer/order.html',context)
    def post(self, request, *args, **kwargs):
        name = request.POST.get('name')
        email = request.POST.get('email')
        street = request.POST.get('street')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zip_code = request.POST.get('zip')
        order_items = {
            'items': []
        }

        items = request.POST.getlist('items[]')

        for item in items:
            menu_item = Item.objects.get(pk__contains=int(item))
            item_data = {
                'id': menu_item.pk,
                'name': menu_item.name,
                'price': menu_item.price
            }

            order_items['items'].append(item_data)

            price = 0
            item_ids = []

        for item in order_items['items']:
            price += item['price']
            item_ids.append(item['id'])

        order = OrderModel.objects.create(price=price,name=name,email=email,street=street,city=city,state=state,zip_code=zip_code)
        order.items.add(*item_ids)
        body=('Thank you for your order, your package will be delivered soon!\n' f' Your Total: {price}\n''Get Well Soon!')

        send_mail(
            'Thank You For Your Order!!',
            body,
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False)

        context = {
            'items': order_items['items'],
            'price': price
        }

        return redirect('order-confirmation',pk=order.pk)

class OrderConfirmation(View):
    def get(self,request,pk,*args, **kwargs):
        order=OrderModel.objects.get(pk=pk)

        context={
            'pk': order.pk,
            'items':order.items,
            'price':order.price,
        }
        return render(request,'customer/order_confirmation.html',context)
    def post(self,request,pk,*args, **kwargs):
        data=json.loads(request.body)
        if data['isPaid']:
            order=OrderModel.objects.get(pk=pk)
            order.is_paid=True
            order.save()

        return redirect('payment-confirmation')

class OrderPayConfirmation(View):
    def get(self,request,*args, **kwargs):
        return render(request,'customer/order_pay_confirmation.html')
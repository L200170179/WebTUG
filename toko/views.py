from django.shortcuts import render
from django.http import JsonResponse
from .utils import cookieCart, cartData, guestOrder
from django.views.decorators.csrf import csrf_exempt
import json
import datetime
import midtransclient

from .models import Produk
from .models import Customer
from .models import Itempesan
from .models import IDpesan
from .models import Pesan

#Apabil from .... import * (Semua) pada simbol bintang akan membuat akses pencarian menjadi berat pada Django

def store(request):

	data = cartData(request)
	cartItems = data['cartItems']
	pesan = data['pesan']
	items = data['items']


	produks = Produk.objects.all()
	context = {'Produks':produks, 'cartItems':cartItems}
	return render(request, 'toko1/store.html', context)

def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	pesan = data['pesan']
	items = data['items']

	context = {'items':items, 'pesan':pesan, 'cartItems':cartItems}
	return render(request, 'toko1/cart.html', context)

def checkout(request):
	# print(request.User)
	print('tes')
	print(request)
	data = cartData(request)
	
	cartItems = data['cartItems']
	pesan = data['pesan']
	items = data['items']
	user = request.user

	context = {'items':items, 'pesan':pesan, 'cartItems':cartItems, 'user':user}
	return render(request, 'toko1/checkout.html', context)

 #advanechURL
def updateItem(request):
	data = json.loads(request.body)
	produkId = data['produkId']
	action = data['action']

	print('action:', action)
	print('produkId:', produkId)

	customer = request.user.customer
	produk = Produk.objects.get(id=produkId)
	pesan, created = Pesan.objects.get_or_create(customer=customer, complete=False)

	itemPesan, created = Itempesan.objects.get_or_create(pesan=pesan, produk=produk)
	if action == 'add':
		itemPesan.jumlah = (itemPesan.jumlah + 1)
	elif action == 'remove':
		itemPesan.jumlah = (itemPesan.jumlah - 1)

	itemPesan.save()

	if itemPesan.jumlah <= 0:
		itemPesan.delete()

	return JsonResponse('Item telah ditambahkan', safe=False)

@csrf_exempt
#csrf_exempt untuk membaca interaksi proses antara data customer ke admin
def prosesPesan(request):
	transaksi_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	print( data)

	if request.user.is_authenticated:
		customer = request.user.customer
		pesan, created = Pesan.objects.get_or_create(customer=customer, complete=False)
	
	else:
		customer, pesan = guestOrder(request, data)

	total = float(data['form']['total'])
	pesan.transaksi_id = transaksi_id

	if total == pesan.get_cart_total:
		pesan.complete = True
	pesan.save()

	if pesan.pengiriman == True:
		IDpesan.objects.create(
			customer=customer,
			pesan=pesan,
			idgame=data['pengiriman']['idgame'],
			servergame=data['pengiriman']['servergame'],
		)

# 	# Buat instance Snap API 
# 	snap = midtransclient.Snap(
# 		is_production = False,
# 		server_key = 'SB-Mid-server-Dn9OL3jS_ciTecK5wWjlwY2y',
# 		client_key = 'SB-Mid-client-5lyycFVbjPEEm8fh' 
# 	)
# 	# setel ulang server_key hanya 
# 	snap.api_config.set(server_key = 'SB-Mid-server-Dn9OL3jS_ciTecK5wWjlwY2y'),
# 	# setel ulang hanya 
# 	snap.api_config.set(is_production = True)

# 	# Build API parameter
# 	param = {
#     	"transaction_details": {
#         "order_id": "test-transaction-123",
#         "gross_amount": 200000
#     },	"credit_card":{
#         "secure" : True
#     },	"customer_details":{
#         "first_name": "budi",
#         "last_name": "pratama",
#         "email": "budi.pra@example.com",
#         "phone": "08111222333"
#     }
# }
	 
# 	transaction = snap.create_transaction(param)

# 	transaction_token  =  transaction [ 'token' ]
# 	print ( 'c3f7328f-f43c-4e65-a6d0-4bbcecb0d95c', )
# 	print ( transaction_token )

# 	# url pengalihan transaksi
# 	transaction_redirect_url  =  transaction [ 'redirect_url' ]
# 	print ( 'https://app.midtrans.com/snap/v2/vtweb/c3f7328f-f43c-4e65-a6d0-4bbcecb0d95c' )
# 	print ( transaction_redirect_url )
	

	return JsonResponse('Pembayaran Selesai!',safe=False)

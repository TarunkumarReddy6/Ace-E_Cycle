from django.shortcuts import render , redirect

from django.http import HttpResponse
from scrapweb.models import *
import pymongo
import base64
import json
from bson.objectid import ObjectId
from datetime import date, time, datetime
# Create your views here.
from django.core.files.storage import FileSystemStorage

Client = pymongo.MongoClient('mongodb://localhost:27017/')
db = Client['Scrap']
col_user_register = db['user_register']
col_add_product = db['add_product']
col_add_cart = db['add_cart']
col_orders = db['orders']
col_auction = db['add_auction']
col_bid = db['bid_data']



def index(req):
	req.session['admin']=False
	return render(req,"index.html")

def login(req):
	return render(req,"login.html")
	
def about(req):
	return render(req,"about.html")

def contact(req):
	return render(req,"contact.html")

def sell(req):
	email = req.session.get('customer_id')
	if(email):
		return render(req,"sell.html")
	else:
		return render(req, "login.html")

def signinup(req):
	return render(req,"signin-up.html")

def register(req):
	return render(req,"register.html")

def register_check(request):
	name = request.POST.get('name')
	email = request.POST.get('email')
	password = request.POST.get('password')
	cpassword = request.POST.get('cpassword')
	address = request.POST.get('address')
	number = request.POST.get('number')
	record={
		"Name":name,
		"Email":email,
		"Password" : password,
	    "Address" : address,
	    "Number" :number,
	}
	check_Email=bool(col_user_register.find_one({"Email":email}))
	if(check_Email):
		return render(request,"login.html", {'msg':'Email Already Existed'})
	else:
		if(password == cpassword):
			col_user_register.insert_one(record)
			return render(request,"login.html", {'msg':'User Registered Please Login'})
		else:
			return render(request,"register.html", {'msg':'Password is not same'})


def login_check(request):
	email = request.POST.get('email')
	password = request.POST.get('password')
	if(email == "aceecycle@mini.com" and password == "ace@123"):
		request.session['admin']=True
		return admin_dashboard(request)
	else:
		email_check = bool(col_user_register.find_one({"Email":email}))
		if(email_check):
			user = col_user_register.find_one({"Email":email})
			if(user['Password']==password):
				request.session['customer_id'] = user['Email']
				print(request.session.get('customer_id'))
				return render(request,"index.html",{'msg':user,'value':'disabled'})
			else:
				return render(request,"login.html",{'msg':'wrong credentials'})
		else:
			return render(request,"register.html",{'msg':'Email not registered'})
 

def profile(req):
	email = req.session.get('customer_id')
	if(email):
		user = col_user_register.find_one({"Email":email})
		orders = list(col_orders.find({"customer_id":email}))
		for i in orders:
			i['id'] = i['_id']
			del i['_id']
		return render(req,"profile.html",{'msg':user,'orders':orders})
	else:
		return render(req, "login.html")

def profile_edit(request):
	email = request.session.get('customer_id')
	address = request.POST.get('address')
	number = request.POST.get('number')
	pin = request.POST.get('pin')
	col_user_register.update_one({"Email":email},{"$set" :{"Address":address}})
	col_user_register.update_one({"Email":email},{"$set" :{"Number":number}})
	col_user_register.update_one({"Email":email},{"$set" :{"Pin":pin}})
	user = col_user_register.find_one({"Email":email})
	return render(request,"profile.html",{'msg':user})

def add_product(request):
	user = request.session.get('customer_id')
	admin = request.session.get('admin')
	if(user or admin):
		name = request.POST.get('name')
		image = request.FILES['image']
		description = request.POST.get('Description')
		category = request.POST.get('category')
		quantity = request.POST.get('Quantity')
		price =  request.POST.get('price')
		if(user):
			userId=user
			status = "pending"
		else:
			userId="aceadmin@mini.com"
			status = "accepted"
		fs = FileSystemStorage()
		filename = fs.save(image.name,image)
		with open(fs.path(filename),'rb') as f:
			img_binary = f.read()
		record={
		"user_id":userId,
		"name":name,
		"image_name":image.name,
		"image_data":img_binary,
		"description":description,
		"category":category,
		"quantity":quantity,
		"price":price,
		"status":status
		}
		col_add_product.insert_one(record)
		if(admin):
			return productset(request)
		return render(request,"sell.html",{'msg':'product saved'})
	else:
		return render(request,"login.html")

def shop(req):
    list_of_products = list(col_add_product.find({'status':"accepted"}))
    for i in list_of_products:
        i['id'] = i['_id']
        del i['_id']
        i['image_url'] = f"/media/{i['image_name']}"
    return render(req,"shop.html",{'list':list_of_products})

def shopsingle(req):
	r = req.get_full_path()
	id = r.split('?')
	id1=id[1]
	product = list(col_add_product.find({"_id":ObjectId(id1)}))
	image_url = f"/media/{product[0]['image_name']}"
	return render(req,"shop-single.html",{'product':product,"id":id1,'image_url': image_url})


def cart(req):
	p=0
	customer_id = req.session.get('customer_id')
	if(customer_id):
		cart_products = list(col_add_cart.find({"customer_id":customer_id}))
		for i in cart_products:
			i['id'] = i['_id']
			del i['_id']
		for x,y in enumerate(cart_products):
			p = p + int(y['price'])
		return render(req,"cart.html",{"list":cart_products,'total':p})
	return render(req, "login.html")

def add_cart(req):
	customer_id = req.session.get('customer_id')
	if(customer_id):
		product_id = req.POST.get('product_id')
		quantity =  req.POST.get('product-quanity') 
		product = list(col_add_product.find({"_id":ObjectId(product_id)}))
		price = product[0]['price']
		name = product[0]['name']
		total = int(price) * int(quantity)
		record={
		"customer_id":customer_id,
		"product_name":name,
		"price":price,
		"quantity":quantity,
		"total":total
		}
		col_add_cart.insert_one(record)
		return redirect(cart)
	else:
		return render(req, "login.html")


def remove_cart(req):
	customer_id = req.session.get('customer_id')
	r = req.get_full_path()
	id = r.split('?')
	id1=id[1]
	col_add_cart.delete_one({"_id":ObjectId(id1),"customer_id":customer_id})
	return redirect(cart)

def payment(req):
	customer_id = req.session.get('customer_id')
	cart_products = list(col_add_cart.find({"customer_id":customer_id}))
	for j in cart_products:
		col_orders.insert_one(j)
	for i in cart_products:
		col_add_cart.delete_one(i)
	return profile(req)

def admin_dashboard(req):
	products = list(col_add_product.find())
	productsLen = len(products)
	users = list(col_user_register.find())
	userslen = len(users)
	orders = list(col_orders.find())
	ordersLen = len(orders)
	return render(req,"admina.html",{"productsLen":productsLen,"userslen":userslen,"ordersLen":ordersLen,"orders":orders})

def auctionset(req):
	live = list(col_auction.find({"status":"live"}))
	upcoming = list(col_auction.find({"status":"upcoming"}))
	completed = list(col_auction.find({"status":"completed"}))
	for i in live:
			i['id'] = i['_id']
			del i['_id']
	for i in upcoming:
			i['id'] = i['_id']
			del i['_id']
	for i in completed:
			i['id'] = i['_id']
			del i['_id']
	return render(req, "auctionset.html",{'upcoming':upcoming,'completed':completed,'live':live})

def productset(req):
	products = list(col_add_product.find({"status":"accepted"}))
	for i in products:
		i['id'] = i['_id']
		del i['_id']
	pending = list(col_add_product.find({"status":"pending"}))
	for i in pending:
		i['id'] = i['_id']
		del i['_id']
	return render(req,"productset.html",{"products":products,"pending":pending})

def remove_product(req):
	r = req.get_full_path()
	id = r.split('?')
	id1=id[1]
	col_add_product.delete_one({"_id":ObjectId(id1)})
	return productset(req)

def remove_auction(req):
	r = req.get_full_path()
	id = r.split('?')
	id1=id[1]
	col_auction.delete_one({"_id":ObjectId(id1)})
	return auctionset(req)


from datetime import datetime
def add_auction(request):
    admin = request.session.get('admin')
    if(admin):
        image = request.FILES.get('image')
        if image:
            auction_name = request.POST.get('name')
            date_str = request.POST.get('date')
            time_str = request.POST.get('time')
            category = request.POST.get('category')
            quantity = request.POST.get('quantity')
            start_price = request.POST.get('price')
            description = request.POST.get('description')
            date_format = '%Y-%m-%d'
            time_format = '%H:%M'
            auction_datetime = datetime.strptime(date_str + ' ' + time_str, date_format + ' ' + time_format)

            if(auction_datetime > datetime.now()):
                status = "upcoming"
            elif(auction_datetime < datetime.now()):
                status = "completed"
            else:
                status = "current"

            fs = FileSystemStorage()
            filename = fs.save(image.name,image)
            with open(fs.path(filename),'rb') as f:
                img_binary = f.read()

            record={
                "user_id":"aceadmin@mini.com",
                "auction_name":auction_name,
                "image_name":image.name,
                "image_data":img_binary,
                "description":description,
                "category":category,
                "quantity":quantity,
                "start_price":start_price,
                "date":date_str,
                "time":time_str,
                "status":status
            }

            col_auction.insert_one(record)
            return auctionset(request)
        else:
            return render(request, "admina.html", {"message": "Image is required"})
    else:
        return render(request,"login.html")


def live_auction(req):
	r = req.get_full_path()
	id = r.split('?')
	id1=id[1]
	col_auction.update_one({"_id":ObjectId(id1)},{"$set" :{"status":"live"}})
	return auctionset(req)

def stop_auction(req):
	r = req.get_full_path()
	id = r.split('?')
	id1=id[1]
	one_bid = list(col_bid.find({"product_id":id1}))
	bid_sorted = sorted(one_bid, key=lambda x: int(x["bid_amt"]), reverse=True)
	print(one_bid)
	customer_id = bid_sorted[0]['user']
	price = bid_sorted[0]['bid_amt']
	product = col_auction.find_one({"_id":ObjectId(id1)})
	product_name = product['auction_name']
	quantity = product['quantity']
	total = int(price)*int(quantity)
	record={
		"customer_id":customer_id,
		"product_name":product_name,
		"price":price,
		"quantity":quantity,
		"total":total
	}
	print(record)
	col_orders.insert_one(record)
	col_auction.update_one({"_id":ObjectId(id1)},{"$set" :{"status":"completed"}})
	return auctionset(req)

def newauction(req):
	upcoming=list(col_auction.find({"status":"upcoming"}))
	completed=list(col_auction.find({"status":"completed"}))
	live=list(col_auction.find({"status":"live"}))
	if(live):
		for i in live:
			i['id'] = i['_id']
			del i['_id']
			i['image_url'] = f"/media/{i['image_name']}"
		for i in upcoming:
			i['id'] = i['_id']
			del i['_id']
			i['image_url'] = f"/media/{i['image_name']}"
		for i in completed:
			i['id'] = i['_id']
			del i['_id']
			i['image_url'] = f"/media/{i['image_name']}"
		live_id = str(live[0]['id'])
		bid = list(col_bid.find({"product_id": live_id, "user": {"$ne": None}}))
		bid_sorted = sorted(bid, key=lambda x: int(x["bid_amt"]), reverse=True)
		return render(req,"newauction.html",{'upcoming':upcoming,'completed':completed,'live':live,'bid':bid_sorted})
	else:
		for i in upcoming:
			i['id'] = i['_id']
			del i['_id']
			i['image_url'] = f"/media/{i['image_name']}"
		for i in completed:
			i['id'] = i['_id']
			del i['_id']
			i['image_url'] = f"/media/{i['image_name']}"
		return render(req,"newauction.html",{'upcoming':upcoming,'completed':completed})

def auction(req):
	r = req.get_full_path()
	id = r.split('?')
	id1=id[1]
	one_auction = list(col_auction.find({"_id":ObjectId(id1)}))
	for i in one_auction:
		i['image_url'] = f"/media/{i['image_name']}"
	one_bid = list(col_bid.find({"product_id":id1}))
	bid_sorted = sorted(one_bid, key=lambda x: int(x["bid_amt"]), reverse=True)
	message =  id[2]
	if(message == "closed"):	
		auction = list(col_auction.find())
		return render(req,"auction.html",{'oneauction':one_auction,'msg':message,'bid':bid_sorted})
	else:
		auction = list(col_auction.find())
		return render(req,"auction.html",{'oneauction':one_auction,'msg':message})

def logout(req):
	del req.session['customer_id']
	print(req.session.get('customer_id'))
	return redirect(index)

def accept_product(req):
	r = req.get_full_path()
	id = r.split('?')
	id1=id[1]
	one_product = list(col_add_product.find({"_id":ObjectId(id1)}))
	email = one_product[0]['_id']
	col_add_product.update_one({"_id":ObjectId(email)},{"$set" :{"status":"accepted"}})
	return redirect(productset)



from django.conf import settings
from django.views.static import serve

def serve_image(request, filename):
    filepath = settings.MEDIA_ROOT + '/' + filename
    return serve(request, filename, document_root=settings.MEDIA_ROOT)

def pass_recovery(req):
	email = req.POST.get('email')
	password = req.POST.get('password')
	newpassword = req.POST.get('newpassword')
	cnewpassword = req.POST.get('cnewpassword')
	if newpassword == cnewpassword:
		user = col_user_register.find_one({"Email":email})
		if user:
			if user['password'] == password:
				col_user_register.update_one({"Email":email},{"$set" :{"password":newpassword}})
				return login(req)
			else:
				return render(req,"recover.html")
		else:
			return render(req,"recover.html")
	else:
		return render(req,"recover.html")

def bid_data(req):
    iid = req.POST.get('id')
    customer_id = req.session.get('customer_id')
    bid_input = req.POST.get('bid-input')

    existing_bid = col_bid.find_one({"product_id": iid})

    customer_bid = col_bid.find_one({"product_id": iid, "user": customer_id})

    if existing_bid and customer_bid:
        col_bid.update_one({"product_id": iid, "user": customer_id}, {"$set": {"bid_amt": bid_input}})
    else:
        record = {"product_id": iid, "user": customer_id, "bid_amt": bid_input}
        col_bid.insert_one(record)

    return newauction(req)

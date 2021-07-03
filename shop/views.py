from django.contrib import messages
from django.db.models import query
from django.http import response, HttpResponse
from django.shortcuts import render, redirect
from .models import Product, ContactUs, Orders, OrderUpdate
import json
from paytmchecksum import PaytmChecksum
from math import ceil
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required,user_passes_test
from django.views.decorators.csrf import csrf_exempt

# MID:DIY12386817555501617
# Merchant Key:bKMfNxPPf_QdZppa
#testing payment details phone-7777777777 otp-489871
#pip install paytmchecksum

# Create your views here.
#import the logging library
# from logging
# #Get an instance of a logger
# logger = logging.getlogger(_name_)

def index(request):
    products= Product.objects.all()[:6]
    n= len(products)
    #nSlides= n//4 + ceil((n/4)-(n//4))
    allProds=[[products, range(1, len(products))]]
    params={'allProds':allProds }
    return render(request,"shop/index.html", params)

def products(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n//4 + ceil((n/4)-(n//4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params={'allProds':allProds}
    return render(request,'shop/products.html',params)

def searchMatch(query, item):
    if query in item.product_name.lower() or query in item.category.lower() or query in item.desc.lower() or query in item.subcategory.lower():
        return True
    else:
        return False

def search(request):
    query= request.GET.get('search')
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prodtemp= Product.objects.filter(category=cat)
        prod = [item for item in prodtemp if searchMatch(query,item)]
        n = len(prod)
        nSlides = n//4 + ceil((n/4)-(n//4))
        if len(prod)!=0:
            allProds.append([prod, range(1, nSlides), nSlides])
    params={'allProds':allProds, "msg":""}
    if len(allProds)==0 or len(query)<2:
        params = {'msg':"Please make sure to enter relevant search query."}
    return render(request, 'shop/search.html', params)


def about(request):
    return render(request, 'shop/about.html')

def form1(request):
    return render(request, 'shop/form1.html')
def form2(request):
    return render(request, 'shop/form2.html')
def handleSignup(request):
    if request.method == 'POST':
        #Get the parameters of POST
        username = request.POST['username']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        #check for error input
        if len(username) > 10:
            messages.error(request,"Username must be under 10 characters")
            return redirect('/shop/form2')
        if not username.isalnum():
            messages.error(request,"Username must be Alphanumeric characters")
            return redirect('/shop/form2')
        if pass1 != pass2:
            messages.error(request,"Passwords do not match.")
            return redirect('/shop/form2')
        #create the user
        myuser = User.objects.create_user(username, email, pass1)
        myuser.save()
        messages.success(request, " Your Account has been successfully created")
        return redirect('/shop/form1')
    else:
        return HttpResponse('404- NOT FOUND')

def handleLogin(request):
    if request.method == 'POST':
        #Get the parameters of POST
        loginusername = request.POST['loginusername']
        loginpass = request.POST['loginpass']
        
        user = authenticate(username=loginusername, password=loginpass)
        if user is not None:
            login(request,user)
            messages.success(request, "Successfully Logged In")
            return redirect('/')
        else:
            messages.error(request, "Invalid Crendentials, Please try again")
            return redirect('/shop/form1')
    else:
        return HttpResponse('404- NOT FOUND')
def handleLogout(request):
    logout(request)
    messages.success(request, "Successfully Logged Out")
    return redirect('/')

def contact(request):
    if request.method =="POST":
        name=request.POST.get('name', '')
        email=request.POST.get('email', '')
        phone=request.POST.get('phone', '')
        desc=request.POST.get('desc', '')
        contact = ContactUs(name=name,email=email, phone=phone, desc=desc )
        contact.save() 
        id = contact.msg_id
        messages.success(request, "Thanks for contacting us. Your Contact Id is "+str(id)+ ".We'll Revert back as soon possible.")
        return redirect('/')
    return render(request, 'shop/contact.html')

def tracker(request):
    if request.method=="POST":
        orderId = request.POST.get('orderId', '')
        email = request.POST.get('email', '')
        try:
            order = Orders.objects.filter(order_id=orderId, email=email)
            if len(order)>0:
                update = OrderUpdate.objects.filter(order_id=orderId)
                updates = []
                for item in update:
                    updates.append({'text': item.update_desc, 'time': item.timestamp})
                    response = json.dumps({"status":"success", "updates": updates, "itemsJson": order[0].items_json}, default=str)
                return HttpResponse(response)
            else:
                return HttpResponse('{"status":"noitem"}')
        except Exception as e:
            return HttpResponse('{"status":"error"}')
    
    return render(request, 'shop/tracker.html')
    


def productView(request,myid):
    #Fetch the Product using ID
    product= Product.objects.filter(id=myid)
    return render(request, 'shop/prodView.html',{'product':product[0]})


def checkout(request):
    if request.method=="POST":
        return render(request,'shop/order_address.html')  
    return render(request, 'shop/checkout.html')

#@login_required(login_url="/shop/form1/")
def checkout_address(request):
    if request.method =="POST":
        items_json=request.POST.get('itemsJson', '')
        name=request.POST.get('name', '')
        amount=request.POST.get('amount', '')
        email=request.POST.get('email', '')
        phone=request.POST.get('phone', '')
        address=request.POST.get('address1', '') + " " + request.POST.get('address2', '')
        city=request.POST.get('city', '')
        state=request.POST.get('state', '')
        zip_code=request.POST.get('zip_code', '')
        order = Orders(items_json=items_json, name=name,email=email, phone=phone, address=address, city=city, state=state, zip_code=zip_code, amount=amount)
        order.save()
        update = OrderUpdate(order_id=order.order_id, update_desc="The Order has been placed.")
        update.save()
        id = order.order_id
    
        O_id="1000"+str(id)#this statement is only used because of the merchant id and key used in this website have same order if so order get failed

        #request the paytm to transfer the amount after payment by user
        param_dict={

            'MID': 'DIY12386817555501617',
            'ORDER_ID': str(O_id),#you can directly used str(id) if you have autheticated merchant id and key 
            'TXN_AMOUNT': str(amount),
            'CUST_ID': email,
            'INDUSTRY_TYPE_ID': 'Retail',
            'WEBSITE': 'WEBSTAGING',
            'CHANNEL_ID': 'WEB',
            'CALLBACK_URL':'http://127.0.0.1:8000/shop/checkout/order_address/handlerequest/',

        }
        param_dict['CHECKSUMHASH'] = PaytmChecksum.generateSignature(param_dict,"bKMfNxPPf_QdZppa")
        return  render(request, 'shop/paytm.html', {'param_dict': param_dict})
    return render(request, 'shop/order_address.html')


@csrf_exempt
def handlerequest(request):
    #paytm will send post request
    form = request.POST
    response_dict = {}
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]

    verify = PaytmChecksum.verifySignature(response_dict, "bKMfNxPPf_QdZppa", checksum)
    if verify:
        if response_dict['RESPCODE'] == '01':
            print('order successful')
            messages.success(request, "Thanks for ordering with us. Your order id is " + response_dict['ORDERID']+ ". Use it to track your order using our order tracker")
        else:
            print('order was not successful because' + response_dict['RESPMSG'])
    return render(request, 'shop/paymentstatus.html', {'response': response_dict})
    
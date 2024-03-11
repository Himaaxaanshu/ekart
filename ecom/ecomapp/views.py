from django.shortcuts import render,HttpResponse,redirect
from ecomapp import urls
from ecomapp.models import Product,Cart,Orders,Myorder
from django.contrib.auth.models import User
from django.contrib.auth import login ,logout,authenticate
from django.db.models import Q
import random
import razorpay
from django.core.mail import send_mail

# Create your views here.

def register(request):
    if request.method == 'GET':
        return render(request, "Register.html")
    else:
        un = request.POST['uname']
        up = request.POST['upass']
        ucp = request.POST['ucpass']
        # print(un)
        # print(up)
        # print(ucp)
        context = {}
        if up != ucp:
            context['error'] = "password does not match"
            return render(request,"Register.html",context)
        elif len(up) > 5:
            context['error'] = "password should have less then 6 characters"
            return render(request,"Register.html",context)
        else:
            try:
                u = User.objects.create(username = un)
                u.set_password(up)
                u.save()
                context['success'] = "Successfully Registered !"
                return render(request,"Register.html",context)
            except:
                context['error'] = "User already exists !!"
                return render(request,"Register.html",context)
    
        
def user_login(request):
    if request.method == 'GET':
        return render(request, "login.html")
    else:
        un = request.POST['uname']
        up = request.POST['upass']
        u = authenticate(username = un, password = up)
        if u != None:
            login(request,u)
            return redirect("/home")
        else:
            context ={}
            context ['error']= "Invalid username or password"
            return render(request,"login.html",context)

def home(request):
    m = Product.objects.filter(is_active = True)
    #print(m)
    context = {}
    context['data'] = m

    return render(request,"index.html",context)

def product_details(request,prod_id ):
    p = Product.objects.filter(id = prod_id)
    context ={}
    context['data'] = p
    return render(request,'product details.html',context)

def cart(request,prod_id):
    if request.user.is_authenticated:
        u = User.objects.filter(id = request.user.id)
        # print(u[0])
        p = Product.objects.filter(id = prod_id)

        q1 = Q(user_id = u[0])
        q2 = Q(pid = p[0])
        c = Cart.objects.filter(q1 & q2)
        n = len(c)
        context = {}
        context['data'] = p
        if n==1:
            context['msg'] = "Product already exist in cart !"
            return render(request,"product details.html",context)
        else:
            c = Cart.objects.create(user_id = u[0],pid = p[0])
            c.save()
            context['msg'] = "Product added to cart !"
            return render(request,"product details.html",context)
        
    else:# if not authenticate
        return redirect("/login")


        

def updateqty(request,x,cid):
    c = Cart.objects.filter(id = cid)
    q = c[0].qty
    if x == '1':
        q = q+1
    elif q>1:
        q = q-1
    c.update(qty = q)

    return redirect("/viewcart")


def viewcart(request):
    c = Cart.objects.filter(user_id = request.user.id)
    # print(c)
    # print(c[0])
    # print(c[0].user_id.is_staff)
    tot = 0
    for x in c:
        tot = tot + x.pid.price * x.qty
    context = {}
    context['data'] = c
    context['totamt'] = tot
    context['n'] = len(c)
    return render(request,"cart.html",context)

def remove(request, cid):
    c = Cart.objects.filter( id = cid)
    c.delete()
    context = {}
    context['data'] = c
    return redirect("/viewcart")

def placeorder(request):
    c = Cart.objects.filter(user_id = request.user.id)
    o_id = random.randrange(1000, 9999)
    for x in c:
        amount = x.pid.price * x.qty
        o = Orders.objects.create(order_id = o_id, user_id = x.user_id,
                                  amt = amount, qty = x.qty, pid = x.pid )
        o.save()
        x.delete()
    return redirect("/fetchorder")
        
def fetchorder(request):
    orders = Orders.objects.filter(user_id = request.user.id)
    tot = 0
    for x in orders:
        tot = tot + x.amt

    context = {}
    context['orders'] = orders
    context['totamt'] = tot
    context['n'] = len(orders)
    return render(request, "placeorder.html",context)

def makepayment(request):
    client = razorpay.Client(auth=("rzp_test_R7kWkFU6ZllnWF", "W0gE85soRmV6WanAQr1nW69n"))
    ord = Orders.objects.filter(user_id = request.user.id)
    tot = 0
    for x in ord:
        tot = tot + x.amt
        oid = x.order_id

    data = {"amount":tot*100,"currency":"INR","receipt":oid}
    payment = client.order.create(data = data)
    print(payment)
    context = {}
    context['payment'] = payment
    return render(request,"pay.html", context)

def paymentsuccess(request):
    sub = "Ekart order summary"
    msg = "Thanks for Shopping with us!!"
    frm = "himanshu.narwal11@gmail.com"
    u = User.objects.filter(id = request.user.id)
    to = "vrushali@itvedant.com"
    send_mail(
        sub,
        msg,
        frm,
        [to],
        fail_silently=False
    )
    ord = Orders.objects.filter(id =request.user.id)
    for x in ord:
        mo = Myorder.objects.create(order_id = x.order_id,
                                    user_id = x.user_id,
                                    pid = x.pid,
                                    qty = x.qty,
                                    amt = x.amt)
        mo.save()
        x.delete()
    return HttpResponse("paymentsuccessful")

def catfilter(request, cv):
    q1 = Q(cat = cv)
    q2 = Q(is_active = True)

    p = Product.objects.filter(q1 & q2)
    context = {}
    context['data'] = p
    return render(request,"index.html",context)

def remove_order(request, oid):
    o = Orders.objects.filter( id = oid)
    o.delete()
    context = {}
    context['data'] = o
    return redirect("/fetchorder")

def user_logout(request):
    logout(request)
    return render(request, "login.html")

def search(request):
    context = {}
    query = request.POST['query']
    print(query)
    pname = Product.objects.filter(name__icontains = query)
    pdetails = Product.objects.filter(pdetails__icontains = query)
    pcat = Product.objects.filter(cat__icontains = query)
    allproducts = pname.union(pdetails,pcat)
    if len(allproducts)== 0:
        context['errmsg'] = "Products Not Found"
    context['data'] = allproducts
    return render(request,"index.html",context)
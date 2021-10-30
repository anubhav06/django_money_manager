from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.db.utils import Error
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Categories, Transaction

# Create your views here.

def index(request):

    if request.user.is_authenticated :
        user = User.objects.get(username = request.user)
        money = user.totalMoney
        balance = user.currentMoney

        return render(request, "moneyManager/index.html",{
            "money" : money,
            "balance" : balance
        })
    
    return render(request, "moneyManager/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "moneyManager/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "moneyManager/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "moneyManager/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "moneyManager/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "moneyManager/register.html")

@login_required(login_url="/login")
def addMoney(request):

    if request.method == "POST":
        # If total money is added
        if request.POST.get("totalMoney"):

            money = request.POST["totalMoney"]
            user = User.objects.get(username = request.user)

            # Only update money if total money is 0
            if user.totalMoney != 0:
                return HttpResponse('ERROR: You already have total money added!')

            user.totalMoney = money
            user.currentMoney = money
            user.save()
        
        # If a category is added
        elif request.POST.get("category"):
            
            inputCategory = request.POST["category"]
            inputCategory = inputCategory.upper()
            currentUser = User.objects.get(username = request.user)
            
            # Check if user has already created a category with that name
            try:
                category = Categories.objects.get(user = currentUser, name = inputCategory)
            except ObjectDoesNotExist:
                Categories.objects.create(user = currentUser, name = inputCategory)
                category = None
            
            if category is not None:

                user = User.objects.get(username = request.user)
                categories = Categories.objects.filter(user = user)

                return render(request, "moneyManager/addMoney.html", {
                    "message" : "You already have a category with that name!",  
                    "categories" : categories
                })

        # If a new transaction is added
        elif request.POST.get("newTransaction"):

            try:
                amount = request.POST["newTransaction"]
                category = request.POST["categories"]
            except Error:
                amount = None
                category = None
            
            if amount is None or category is None:
                return HttpResponse('You need to provide both the amount and category')

            print(amount)
            print(category)

            currentUser = User.objects.get(username = request.user)
            
            # Update the balance
            user = User.objects.get(username=currentUser)

            if user.currentMoney - int(amount) < 0:
                return HttpResponse("ERROR: You don't have that much money to spend!")
            user.currentMoney -= int(amount)
            user.save()

            # Add the transaction to history
            category = Categories.objects.get(user = currentUser, name=category)
            Transaction.objects.create(user=currentUser, amount=amount, category=category)


        return HttpResponseRedirect(reverse("addMoney"))
    else:

        user = User.objects.get(username = request.user)
        money = user.totalMoney
        balance = user.currentMoney
        categories = Categories.objects.filter(user = user)
        transactions = Transaction.objects.filter(user = user)
        return render(request, "moneyManager/addMoney.html", {
            "money" : money,
            "categories" : categories,
            "balance" : balance,
            "transactions" : transactions
        })
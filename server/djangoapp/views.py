# Uncomment the required imports before adding the code

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import logout
from django.contrib import messages
from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    data = {"userName":""}
    return JsonResponse(data)

# Create a `registration` view to handle sign up request
# @csrf_exempt
def registration(request):
    context = {}
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    first_name = data['firstName']
    last_name = data['lastName']
    email = data['email']
    username_exist = False
    email_exist = False
    try:
        # Check if user already exists
        User.objects.get(username=username)
        username_exist = True
    except:
        # If not, simply log this is a new user
        logger.debug("{} is new user".format(username))
    # If it is a new user
    if not username_exist:
        # Create user in auth_user table
        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,password=password, email=email)
        # Login the user and redirect to list page
        login(request, user)
        data = {"userName":username,"status":"Authenticated"}
        return JsonResponse(data)
    else :
        data = {"userName":username,"error":"Already Registered"}
        return JsonResponse(data)


def get_cars(request):
    count = CarMake.objects.count()
    print(f"CarMake count before initiate: {count}")
    
    if count == 0:
        print("Populating car makes and models...")
        initiate()
    else:
        print("Data already populated.")
    
    car_models = CarModel.objects.select_related('car_make')
    print(f"Retrieved {car_models.count()} car models")

    cars = []
    for car_model in car_models:
        cars.append({
            "CarModel": car_model.name,
            "CarMake": car_model.car_make.name
        })

    print("Cars returned in response:", cars)
    return JsonResponse({"CarModels": cars})



# # Update the `get_dealerships` view to render the index page with
# a list of dealerships
# def get_dealerships(request):
#Update the `get_dealerships` render list of dealerships all by default, particular state if state is passed
def get_dealerships(request, state="All"):
    if(state == "All"):
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/"+state
    dealerships = get_request(endpoint)
    return JsonResponse({"status":200,"dealers":dealerships})


def get_dealer_details(request, dealer_id):
    if(dealer_id):
        endpoint = "/fetchDealer/"+str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status":200,"dealer":dealership})
    else:
        return JsonResponse({"status":400,"message":"Bad Request"})

# Create a `get_dealer_reviews` view to render the reviews of a dealer
# def get_dealer_reviews(request,dealer_id):
def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = "https://sakthioviya1-3030.theiadockernext-0-labs-prod-theiak8s-4-tor01.proxy.cognitiveclass.ai/fetchReviews/dealer/" + str(dealer_id)

        reviews = get_request(endpoint)

        try:
            # Parse JSON if needed
            if isinstance(reviews, str):
                reviews = json.loads(reviews)

            if not isinstance(reviews, list):
                return JsonResponse({"status": 500, "message": "Invalid response format"})

            for review_detail in reviews:
                if isinstance(review_detail, dict) and 'review' in review_detail:
                    sentiment = analyze_review_sentiments(review_detail['review'])
                    review_detail['sentiment'] = sentiment.get('sentiment', 'neutral')
                else:
                    review_detail['sentiment'] = 'unknown'

            return JsonResponse({"status": 200, "reviews": reviews})

        except Exception as e:
            print("Error in get_dealer_reviews:", str(e))
            return JsonResponse({"status": 500, "message": str(e)})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})



# Create a `get_dealer_details` view to render the dealer details
# def get_dealer_details(request, dealer_id):
# ...

# Create a `add_review` view to submit a review
# def add_review(request):
def add_review(request):
    if(request.user.is_anonymous == False):
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status":200})
        except:
            return JsonResponse({"status":401,"message":"Error in posting review"})
    else:
        return JsonResponse({"status":403,"message":"Unauthorized"})

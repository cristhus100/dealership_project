import json
import logging
import requests
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.views.decorators.http import require_http_methods
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review

logger = logging.getLogger(__name__)

DEALER_API_URL = settings.DEALER_API_URL.rstrip('/')
SENTIMENT_API_URL = settings.SENTIMENT_API_URL.rstrip('/')


# ============================================================
# CSRF Token
# ============================================================
@ensure_csrf_cookie
def get_csrf_token(request):
    return JsonResponse({'csrfToken': get_token(request)})


# ============================================================
# Authentication
# ============================================================
@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    try:
        data = json.loads(request.body)
        username = data.get('userName')
        password = data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({
                'userName': user.username,
                'status': 'Authenticated'
            })
        return JsonResponse({
            'userName': username,
            'status': 'Failed'
        }, status=401)
    except Exception as e:
        logger.error(f"Login error: {e}")
        return JsonResponse({'status': 'Failed', 'message': str(e)}, status=400)


@require_http_methods(["GET"])
def logout_user(request):
    logout(request)
    return JsonResponse({
        'success': True,
        'message': 'Logout successful'
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    try:
        data = request.data
        username = data.get('username', data.get('userName'))
        password = data.get('password')
        first_name = data.get('firstName', data.get('first_name', ''))
        last_name = data.get('lastName', data.get('last_name', ''))
        email = data.get('email', '')

        if User.objects.filter(username=username).exists():
            return Response({
                'success': False,
                'message': 'Username already exists'
            }, status=status.HTTP_409_CONFLICT)

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )
        login(request, user)
        return Response({
            'success': True,
            'message': 'Registration successful',
            'username': user.username,
            'userId': user.id,
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


# ============================================================
# Car Make / Model (lab exacto)
# ============================================================
def get_cars(request):
    count = CarMake.objects.filter().count()
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels": cars})


# ============================================================
# Dealers (proxy via restapis.py)
# ============================================================
def get_dealerships(request, state="All"):
    if state == "All":
        endpoint = "/fetchDealers"
    else:
        endpoint = "/fetchDealers/" + state
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchDealer/" + str(dealer_id)
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


# ============================================================
# Reviews (proxy via restapis.py)
# ============================================================
def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        endpoint = "/fetchReviews/dealer/" + str(dealer_id)
        reviews = get_request(endpoint)
        for review_detail in reviews if isinstance(reviews, list) else []:
            response = analyze_review_sentiments(review_detail['review'])
            print(response)
            review_detail['sentiment'] = response['sentiment']
        return JsonResponse({"status": 200, "reviews": reviews})
    else:
        return JsonResponse({"status": 400, "message": "Bad Request"})


def add_review(request):
    if request.user.is_anonymous == False:
        data = json.loads(request.body)
        try:
            response = post_review(data)
            return JsonResponse({"status": 200})
        except:
            return JsonResponse({"status": 401, "message": "Error in posting review"})
    else:
        return JsonResponse({"status": 403, "message": "Unauthorized"})


# ============================================================
# Sentiment Analysis
# ============================================================
def analyze_sentiment(text):
    try:
        resp = requests.get(
            f'{SENTIMENT_API_URL}/analyze/{text}',
            timeout=0.3
        )
        resp.raise_for_status()
        result = resp.json()
        return result.get('sentiment', 'neutral')
    except requests.RequestException as e:
        logger.error(f"Sentiment analysis error: {e}")
        return 'neutral'


@api_view(['GET'])
def analyze_review(request, text):
    sentiment = analyze_sentiment(text)
    return Response({'text': text, 'sentiment': sentiment})


# ============================================================
# Template-based pages (HTML)
# ============================================================
def get_dealers_page(request):
    try:
        state = request.GET.get('state')
        if state:
            resp = requests.get(f'{DEALER_API_URL}/fetchDealers', timeout=10)
            resp.raise_for_status()
            dealers = resp.json()
            dealers = [d for d in dealers if d.get('state', '').lower() == state.lower()]
        else:
            resp = requests.get(f'{DEALER_API_URL}/fetchDealers', timeout=10)
            resp.raise_for_status()
            dealers = resp.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching dealers: {e}")
        dealers = []
    return render(request, 'djangoapp/index.html', {'dealers': dealers})


def get_dealer_details_page(request, dealer_id):
    dealer = None
    reviews = []
    try:
        resp = requests.get(f'{DEALER_API_URL}/fetchDealer/{dealer_id}', timeout=10)
        resp.raise_for_status()
        dealer = resp.json()

        rev_resp = requests.get(
            f'{DEALER_API_URL}/fetchReviews/dealer/{dealer_id}',
            timeout=10
        )
        rev_resp.raise_for_status()
        reviews = rev_resp.json()

        for review in reviews if isinstance(reviews, list) else []:
            if 'review' in review and review['review']:
                try:
                    review['sentiment'] = analyze_sentiment(review['review'])
                except Exception:
                    review['sentiment'] = 'neutral'
    except requests.RequestException as e:
        logger.error(f"Error fetching dealer details: {e}")
    return render(request, 'djangoapp/dealer_details.html', {
        'dealer': dealer,
        'reviews': reviews,
    })


def add_review_page(request, dealer_id):
    dealer = None
    car_makes = CarMake.objects.all()
    try:
        resp = requests.get(f'{DEALER_API_URL}/fetchDealer/{dealer_id}', timeout=10)
        resp.raise_for_status()
        dealer = resp.json()
    except requests.RequestException as e:
        logger.error(f"Error fetching dealer: {e}")

    if request.method == 'POST':
        try:
            payload = {
                'id': request.POST.get('id'),
                'name': request.POST.get('name'),
                'dealership': dealer_id,
                'review': request.POST.get('review'),
                'purchase': request.POST.get('purchase') == 'true',
                'purchase_date': request.POST.get('purchase_date', ''),
                'car_make': request.POST.get('car_make', ''),
                'car_model': request.POST.get('car_model', ''),
                'car_year': request.POST.get('car_year', ''),
            }
            rev_resp = requests.post(
                f'{DEALER_API_URL}/insertReview',
                json=payload,
                timeout=10
            )
            rev_resp.raise_for_status()
            return redirect(f'/djangoapp/dealer/{dealer_id}/')
        except requests.RequestException as e:
            logger.error(f"Error adding review: {e}")
            return render(request, 'djangoapp/add_review.html', {
                'dealer': dealer,
                'car_makes': car_makes,
                'error': 'Failed to submit review. Please try again.',
            })

    return render(request, 'djangoapp/add_review.html', {
        'dealer': dealer,
        'car_makes': car_makes,
    })

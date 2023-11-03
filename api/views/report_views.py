import json

from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta, date
from rest_framework import generics
from api.serializers import ReviewSerializer, RespondReviewSerializer
from api.models import Review, SOURCE_STREAM, INSTAGRAM, FACEBOOK, GOOGLE, LINKEDIN, STREAM_CHOICES
from django_filters import rest_framework as filters
from api.filters import ReviewFilter
from django.conf import settings
import calendar
from rest_framework import status
from streams.apis.facebook_apis import reply_facebook_comment, reply_instagram_comment
from django.db.models import Avg
from django.db.models import Count, Q, Case, When, Value, CharField, F
from collections import Counter
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import nltk
import pycountry
nltk.download('wordnet')
nltk.download('stopwords')
from api.utils_report import summary_evolution, comparative_graphics, reviews_location, summary_evolution_total, \
    reputation, keywords


class ComparativeGraphicsAPIView(APIView):
    def get(self, request):
        client = request.user.created_by if request.user.created_by else request.user

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        tour_id = request.query_params.get('tour_id', 'all')
        country_id = request.query_params.get('country_id', 'all')
        city_id = request.query_params.get('city_id', 'all')
        source_stream = request.query_params.get('source_stream', 0)

        result = comparative_graphics(client, start_date, end_date, tour_id, country_id, city_id, source_stream)

        return Response(result)


class ReviewsLocationAPIView(APIView):
    def get(self, request):
        client = request.user.created_by if request.user.created_by else request.user

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        source_stream = request.query_params.get('source_stream', 0)
        tour_id = request.query_params.get('tour_id', 'all')
        country_id = request.query_params.get('country_id', 'all')
        city_id = request.query_params.get('city_id', 'all')
        response_data = reviews_location(client, start_date, end_date, tour_id, country_id, city_id, source_stream)

        return Response(response_data)


class SummaryEvolutionAPIView(APIView):
    def get(self, request):
        client = request.user.created_by if request.user.created_by else request.user

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        tour_id = request.query_params.get('tour_id', 'all')
        country_id = request.query_params.get('country_id', 'all')
        city_id = request.query_params.get('city_id', 'all')
        source_stream = request.query_params.get('source_stream', 0)

        daily_review_stats = summary_evolution(client, start_date, end_date, tour_id, country_id, city_id, source_stream)

        return Response(daily_review_stats)

class SummaryEvolutionTotalsAPIView(APIView):
    def get(self, request):
        client = request.user.created_by if request.user.created_by else request.user

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        source_stream = request.query_params.get('source_stream', 0)
        tour_id = request.query_params.get('tour_id', 'all')
        country_id = request.query_params.get('country_id', 'all')
        city_id = request.query_params.get('city_id', 'all')
        res = summary_evolution_total(client, start_date, end_date, tour_id, country_id, city_id, source_stream)
        return Response(res)


class ReputationAPIView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        tour_id = request.query_params.get('tour_id', 'all')
        country_id = request.query_params.get('country_id', 'all')
        city_id = request.query_params.get('city_id', 'all')
        client = request.user.created_by if request.user.created_by else request.user

        if not start_date:
            start_date = date.today() - timedelta(days=31)
        else:
            start_date = date.fromisoformat(start_date)

        if not end_date:
            end_date = date.today()
        else:
            end_date = date.fromisoformat(end_date)

        data = reputation(client, start_date, end_date, tour_id, country_id, city_id, None)

        return Response(data, status=status.HTTP_200_OK)


class KeywordAPIView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        source_stream = request.query_params.get('source_stream', 0)

        tour_id = request.query_params.get('tour_id', 'all')
        country_id = request.query_params.get('country_id', 'all')
        city_id = request.query_params.get('city_id', 'all')

        user_word = request.query_params.get('user_word', None) 
        number_of_repetitions = request.query_params.get('number_of_repetitions', 0)
        number_of_repetitions_variation = request.query_params.get('number_of_repetitions_variation', 0.0)

        client = request.user.created_by if request.user.created_by else request.user

        data = keywords(user_word, int(number_of_repetitions), float(number_of_repetitions_variation), client, start_date, end_date, tour_id, country_id, city_id, source_stream)
        return Response(data, status=status.HTTP_200_OK)
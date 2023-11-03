import json

from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta, date
from rest_framework import generics
from api.serializers import ReviewSerializer, ExportReportSerializer
from api.models import ScheduleEmailAddress, SOURCE_STREAM, INSTAGRAM, FACEBOOK, GOOGLE, LINKEDIN, STREAM_CHOICES
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
from api.export_utils.export_comparative import export_pdf_comparative, export_xlsx_comparative
from api.export_utils.export_location import export_pdf_location, export_xlsx_location
from api.export_utils.export_evolution import export_pdf_evolution, export_xlsx_evolution
from api.export_utils.export_reputation import export_pdf_reputation, export_xlsx_reputation
from api.export_utils.export_keywords import export_pdf_keywords, export_xlsx_keywords
from django.http import HttpResponse
from tour_reviews_ai.tasks import save_tmp_file, send, save_tmp_file_xlsx


class ExportComparativeGraphicsAPIView(APIView):
    def get(self, request):
        client = request.user.created_by if request.user.created_by else request.user

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        tour_id = request.query_params.get('tour_id', 'all')
        country_id = request.query_params.get('country_id', 'all')
        city_id = request.query_params.get('city_id', 'all')
        source_stream = request.query_params.get('source_stream', 'all')
        type_ = request.query_params.get('type', 'pdf')
        email_addresses = request.query_params.get('email_addresses', None)
        if email_addresses:
            email_addresses = email_addresses.split(',')
            serializer = ExportReportSerializer(data={'email_addresses': email_addresses})
            if not serializer.is_valid():
                return Response('Emails not existent', status=400)

        result = comparative_graphics(client, start_date, end_date, tour_id, country_id, city_id, source_stream)

        if not start_date:
            start_date = datetime.today() - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if not end_date:
            end_date = datetime.today()
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if type_ == 'pdf':
            pdf_data, title = export_pdf_comparative(result, start_date, end_date)
            if email_addresses:
                new_file_path = save_tmp_file(pdf_data, 'pdf')

            # Return the PDF as a response
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="review_report.pdf"'
        else:
            output, title, extension = export_xlsx_comparative(result, start_date, end_date)
            if email_addresses:
                new_file_path = save_tmp_file_xlsx(output, 'xlsx')

            response = HttpResponse(output, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename="review_report.{extension}"'

        if email_addresses:
            email_addresses = [e.email for e in ScheduleEmailAddress.objects.filter(id__in=email_addresses)]
            send('Export', f'Comparative Graphics Export', email_addresses, new_file_path)

            return Response('Sent')
        else:
            return response


class ExportReviewsLocationAPIView(APIView):
    def get(self, request):
        client = request.user.created_by if request.user.created_by else request.user

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        source_stream = request.query_params.get('source_stream', 'all')
        tour_id = request.query_params.get('tour_id', 'all')
        country_id = request.query_params.get('country_id', 'all')
        city_id = request.query_params.get('city_id', 'all')
        type_ = request.query_params.get('type', 'pdf')
        email_addresses = request.query_params.get('email_addresses', None)
        if email_addresses:
            email_addresses = email_addresses.split(',')
            serializer = ExportReportSerializer(data={'email_addresses': email_addresses})
            if not serializer.is_valid():
                return Response('Emails not existent', status=400)

        response_data = reviews_location(client, start_date, end_date, tour_id, country_id, city_id, source_stream)
        if not start_date:
            start_date = datetime.today() - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if not end_date:
            end_date = datetime.today()
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")


        if type_ == 'pdf':
            pdf_data, title = export_pdf_location(response_data, start_date, end_date)
            if email_addresses:
                new_file_path = save_tmp_file(pdf_data, 'pdf')
            # Return the PDF as a response
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="review_report.pdf"'

        else:
            output, title, extension = export_xlsx_location(response_data, start_date, end_date)
            if email_addresses:
                new_file_path = save_tmp_file_xlsx(output, 'xlsx')
            response = HttpResponse(output, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename="review_report.{extension}"'

        if email_addresses:
            email_addresses = [e.email for e in ScheduleEmailAddress.objects.filter(id__in=email_addresses)]
            send('Export', f'Export Reviews Location', email_addresses, new_file_path)

            return Response('Sent')
        else:
            return response



class ExportSummaryEvolutionAPIView(APIView):
    def get(self, request):
        client = request.user.created_by if request.user.created_by else request.user

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        tour_id = request.query_params.get('tour_id', 'all')
        country_id = request.query_params.get('country_id', 'all')
        city_id = request.query_params.get('city_id', 'all')
        source_stream = request.query_params.get('source_stream', 'all')
        type_ = request.query_params.get('type', 'pdf')
        email_addresses = request.query_params.get('email_addresses', None)
        if email_addresses:
            email_addresses = email_addresses.split(',')
            serializer = ExportReportSerializer(data={'email_addresses': email_addresses})
            if not serializer.is_valid():
                return Response('Emails not existent', status=400)

        result = summary_evolution(client, start_date, end_date, tour_id, country_id, city_id, source_stream)

        if not start_date:
            start_date = datetime.today() - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if not end_date:
            end_date = datetime.today()
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        if type_ == 'pdf':
            pdf_data, title = export_pdf_evolution(result, start_date, end_date)
            if email_addresses:
                new_file_path = save_tmp_file(pdf_data, 'pdf')

            # Return the PDF as a response
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="review_report.pdf"'

        else:
            output, title, extension = export_xlsx_evolution(result, start_date, end_date)
            if email_addresses:
                new_file_path = save_tmp_file_xlsx(output, 'xlsx')

            response = HttpResponse(output, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename="review_report.{extension}"'

        if email_addresses:
            email_addresses = [e.email for e in ScheduleEmailAddress.objects.filter(id__in=email_addresses)]
            send('Export', f'Summary Export', email_addresses, new_file_path)

            return Response('Sent')
        else:
            return response


class ExportReputationAPIView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        tour_id = request.query_params.get('tour_id', 'all')
        country_id = request.query_params.get('country_id', 'all')
        city_id = request.query_params.get('city_id', 'all')
        type_ = request.query_params.get('type', 'pdf')
        email_addresses = request.query_params.get('email_addresses', None)
        if email_addresses:
            email_addresses = email_addresses.split(',')
            serializer = ExportReportSerializer(data={'email_addresses': email_addresses})
            if not serializer.is_valid():
                return Response('Emails not existent', status=400)

        client = request.user.created_by if request.user.created_by else request.user

        if not start_date:
            start_date = date.today() - timedelta(days=30)
        else:
            start_date = date.fromisoformat(start_date)

        if not end_date:
            end_date = date.today()
        else:
            end_date = date.fromisoformat(end_date)

        result = reputation(client, start_date, end_date, tour_id, country_id, city_id, None)

        if type_ == 'pdf':
            pdf_data, title = export_pdf_reputation(result, start_date, end_date)
            if email_addresses:
                new_file_path = save_tmp_file(pdf_data, 'pdf')
            # Return the PDF as a response
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="review_report.pdf"'

        else:
            output, title, extension = export_xlsx_reputation(result, start_date, end_date)
            if email_addresses:
                new_file_path = save_tmp_file_xlsx(output, 'xlsx')

            response = HttpResponse(output, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename="review_report.{extension}"'

        if email_addresses:
            email_addresses = [e.email for e in ScheduleEmailAddress.objects.filter(id__in=email_addresses)]
            send("Export", f'Reputation Score', email_addresses, new_file_path)

            return Response('Sent')
        else:
            return response


class ExportKeywordAPIView(APIView):
    def get(self, request):
        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        source_stream = request.query_params.get('source_stream', 'all')

        tour_id = request.query_params.get('tour_id', 'all')
        country_id = request.query_params.get('country_id', 'all')
        city_id = request.query_params.get('city_id', 'all')
        type_ = request.query_params.get('type', 'pdf')
        email_addresses = request.query_params.get('email_addresses', None)
        if email_addresses:
            email_addresses = email_addresses.split(',')
            serializer = ExportReportSerializer(data={'email_addresses': email_addresses})
            if not serializer.is_valid():
                return Response('Emails not existent', status=400)

        client = request.user.created_by if request.user.created_by else request.user

        data = keywords(client, start_date, end_date, tour_id, country_id, city_id, source_stream, number_keywords=15)
        if not start_date:
            start_date = datetime.today() - timedelta(days=30)
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if not end_date:
            end_date = datetime.today()
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        for item in data["positive"]:
            item["sentiment"] = "Positive"
        for item in data["negative"]:
            item["sentiment"] = "Negative"
        data = data["positive"] + data["negative"]

        if type_ == 'pdf':
            pdf_data, title = export_pdf_keywords(data, start_date, end_date)
            if email_addresses:
                new_file_path = save_tmp_file(pdf_data, 'pdf')
            # Return the PDF as a response
            response = HttpResponse(pdf_data, content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="review_report.pdf"'

        else:
            output, title, extension = export_xlsx_keywords(data, start_date, end_date)
            if email_addresses:
                new_file_path = save_tmp_file_xlsx(output, 'xlsx')
            response = HttpResponse(output, content_type='application/vnd.ms-excel')
            response['Content-Disposition'] = f'attachment; filename="review_report.{extension}"'

        if email_addresses:
            email_addresses = [e.email for e in ScheduleEmailAddress.objects.filter(id__in=email_addresses)]
            send('Export', f'Keyword Repetitions', email_addresses, new_file_path)

            return Response('Sent')
        else:
            return response
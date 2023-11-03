from rest_framework.views import APIView
from datetime import timedelta, date
from api.models import Review, SOURCE_STREAM
from django.db.models import Count
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import xlsxwriter
from django.http import HttpResponse
import pycountry
import json

from django.http import FileResponse
from api import utils
from api.utilities.export_report import export_pdf, export_xlsx


class ExportAPIView(APIView):
    def get(self, request):

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        search_factor = request.query_params.get('search_factor', None)
        xls = request.query_params.get('xls', False)
        compare = request.query_params.get('compare', True)

        if xls == 'true':
            xls = True
        else:
            xls = False

        if compare is True or compare == 'true':
            compare = True
        else:
            compare = False

        if not start_date:
            start_date = date.today() - timedelta(days=30)
        else:
            start_date = date.fromisoformat(start_date)

        if not end_date:
            end_date = date.today()
        else:
            end_date = date.fromisoformat(end_date)

        output, title, extension = export_xlsx(start_date, end_date, search_factor, compare, xls)

        response = HttpResponse(output, content_type='application/vnd.ms-excel')
        response['Content-Disposition'] = f'attachment; filename="review_report.{extension}"'

        return response


class ExportPDFAPIView(APIView):
    def get(self, request):

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        search_factor = request.query_params.get('search_factor', None)
        compare = request.query_params.get('compare', True)

        if compare is True or compare == 'true':
            compare = True
        else:
            compare = False

        if not start_date:
            start_date = date.today() - timedelta(days=30)
        else:
            start_date = date.fromisoformat(start_date)

        if not end_date:
            end_date = date.today()
        else:
            end_date = date.fromisoformat(end_date)

        pdf_data = export_pdf(start_date, end_date, search_factor, compare)

        # Return the PDF as a response
        response = HttpResponse(pdf_data, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="review_report.pdf"'
        return response

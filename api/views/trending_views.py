from serpapi import GoogleSearch
from rest_framework.response import Response
from rest_framework.views import APIView
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from rest_framework import status
from datetime import datetime, date, timedelta
from api.models import STREAM_CHOICES, Review

from api.utils_report import preprocess_text, trending_keywords

class TrendingViewset(APIView):
    def get(self, request):

        q = self.request.query_params.get('q')
        if not q:
            return Response({"message": "Query('q') parameter is requried...!"}, status=status.HTTP_400_BAD_REQUEST)
        params = {
            "api_key": "8d9e2043e5998164c6a3a250008f708946f0216cf278b0642f3fe0b12e5c4874",
            "engine": "google_trends",
            "q": q
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        return Response(results)
    
class TrendingKeywordsViewset(APIView):
    def get(self, request):

        start_date = request.query_params.get('start_date', None)
        end_date = request.query_params.get('end_date', None)
        source_stream = request.query_params.get('source_stream', 'all')

        tour_id = request.query_params.get('tour_id', 'all')
        country_id = request.query_params.get('country_id', 'all')
        city_id = request.query_params.get('city_id', 'all')

        user_word = request.query_params.get('user_word', None) 
        number_of_repetitions = request.query_params.get('number_of_repetitions', 0)
        number_of_repetitions_variation = request.query_params.get('number_of_repetitions_variation', 0.0)

        client = request.user.created_by if request.user.created_by else request.user

        data = trending_keywords(user_word, int(number_of_repetitions), float(number_of_repetitions_variation), client, start_date, end_date, tour_id, country_id, city_id, source_stream)

        if data['keyword']:
            keywords = ",".join(data['keyword'])

            # Split the string after every 4th comma
            split_keywords = []
            parts = keywords.split(',')
            for i in range(0, len(parts), 5):
                split_keywords.append(','.join(parts[i:i+5]))

            final_result = []

            # Now split_keywords contains the substrings after every 4th comma
            for q in split_keywords:
                try:
                    params = {
                        "api_key": "8d9e2043e5998164c6a3a250008f708946f0216cf278b0642f3fe0b12e5c4874",
                        "engine": "google_trends",
                        "q": q
                    }

                    search = GoogleSearch(params)
                    results = search.get_dict()

                    final_result.append(results)
                except Exception as e:
                    return Response({"Error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response(final_result, status=status.HTTP_200_OK)
        else:
            return Response(data={"message": "No Keywords"}, status=status.HTTP_200_OK)
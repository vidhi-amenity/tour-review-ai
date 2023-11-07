from rest_framework.views import APIView
from rest_framework.response import Response
from datetime import datetime, timedelta, date
from rest_framework import generics
from api.serializers import ReviewSerializer, RespondReviewSerializer
from api.models import Review, STREAM_CHOICES, INSTAGRAM, FACEBOOK, GOOGLE, LINKEDIN, Country, Tour, ApiKeyStream, Stream
from django_filters import rest_framework as filters
from api.filters import ReviewFilter
from django.conf import settings
import calendar
from rest_framework import status
from streams.apis.facebook_apis import reply_facebook_comment, reply_instagram_comment
from django.db.models import Avg
from django.utils import timezone
from django.db.models import Q, F, Count
import tour_reviews_ai.tasks


class ReviewsTotalsAPIView(APIView):
    def get(self, request):
        client = request.user.created_by if request.user.created_by else request.user
        overall_reviews = Review.objects.filter(client=client, date__gte=client.date_joined).count()

        tour_id = self.request.query_params.get('tour_id', 'all')
        country_id = self.request.query_params.get('country_id', 'all')
        city_id = self.request.query_params.get('city_id', 'all')
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if not start_date:
            start_date = date.today() - timedelta(days=31)
        else:
            start_date = date.fromisoformat(start_date)
        if not end_date:
            end_date = date.today()
        else:
            end_date = date.fromisoformat(end_date)

        if type(start_date) == datetime:
            start_date = start_date.date()

        if start_date < client.date_joined.date():
            start_date = client.date_joined.date()

        queryset = Review.objects.filter(client=client, date__range=(start_date, end_date))

        if tour_id and tour_id != 'all':
            tour_ids = [int(id) for id in tour_id.strip('[]').split(',')]
            if tour_ids:
                queryset = queryset.filter(tour_id__in=tour_ids)

        if country_id and country_id != 'all':
            country_ids = [int(id) for id in country_id.strip('[]').split(',')]
            if country_ids:
                queryset = queryset.filter(country_id__in=country_ids)

        if city_id and city_id != 'all':
            queryset = queryset.filter(city_id=city_id)

        last_review_id = queryset.filter(ai_checked=True).last()

        queryset = queryset.annotate(
            total_reviews=Count('id'),
            positive=Count('id', filter=Q(rating=5)),
            passive=Count('id', filter=Q(rating=4)),
            negative=Count('id', filter=Q(rating__lte=3)),
            responded_count=Count('id', filter=Q(responded=True)),
            pending_count=Count('id', filter=Q(responded=False)),
        )

        queryset = queryset.annotate(
            country_code_annotation=F('country__code'),
            country_name_annotation=F('country__name')
        )

        queryset = queryset.values(
            'country_code_annotation',
            'country_name_annotation',
            'total_reviews',
            'positive',
            'passive',
            'negative',
            'responded_count',
            'pending_count'
        )
        
        total_count = positive_count = neutral_count = negative_count = responded_reviews = pending_reviews = 0
        for review in queryset:
            if not review['country_code_annotation'] or len(review['country_code_annotation']) < 2:
                continue

            total_count += review['total_reviews']
            positive_count += review['positive']
            neutral_count += review['passive']
            negative_count += review['negative']
            responded_reviews += review['responded_count']
            pending_reviews += review['pending_count']

        # positive_count = queryset.filter(client=client, date__range=(start_date, end_date), rating=5).count()
        # neutral_count = queryset.filter(client=client, date__range=(start_date, end_date), rating=4).count()
        # negative_count = queryset.filter(client=client, date__range=(start_date, end_date), rating__lte=3).count()

        # responded_reviews = queryset.filter(responded=True).count()

        # pending = queryset.filter(client=client, date__range=(start_of_month, end_of_month), responded=False)
        # print(pending)

        # pending_reviews = queryset.filter(responded=False).count()

        
        average_rating = queryset.all().aggregate(Avg('rating'))['rating__avg']

        reviews = {
            "this_month": total_count,
            "positive": positive_count,
            "neutral": neutral_count,
            "negative": negative_count,
            "overall": overall_reviews,
            "responded": responded_reviews,
            "pending": pending_reviews,
        }

        last_sync = datetime.utcnow().isoformat() + "Z"

        alerts = [
            # {
            #     "type": "warning",
            #     "message": "The source 'Viator' is not responding from last 12 hours."
            # },
            # {
            #     "type": "info",
            #     "message": "The source 'Booking' is not responding from last 7 hours."
            # },
        ]

        csat_perc = 0
        nps_perc = 0
        detractors_perc = 0

        if average_rating != 0 and average_rating:
            csat_perc = round(average_rating * 2) / 2

        if negative_count != 0 and positive_count != 0:
            nps_perc = round((negative_count/positive_count) * 100, 1)

        if negative_count != 0 and overall_reviews != 0:
            detractors_perc = round((negative_count / overall_reviews) * 100, 1)

        nps = {
            "csat": csat_perc,
            "nps": nps_perc,
            "detractors": detractors_perc
        }

        data = {
            "reviews": reviews,
            "last_sync": last_sync,
            "alerts": alerts,
            "nps": nps,
            'last_review_id': last_review_id.id if last_review_id else 0
        }
        return Response(data)
    
class PendingReviewViewSet(APIView):
    serializer_class = ReviewSerializer
    def get(self, request):
        client = request.user.created_by if request.user.created_by else request.user
        overall_reviews = Review.objects.filter(client=client, date__gte=client.date_joined).count()

        tour_id = self.request.query_params.get('tour_id', 'all')
        country_id = self.request.query_params.get('country_id', 'all')
        city_id = self.request.query_params.get('city_id', 'all')
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)

        if not start_date:
            start_date = date.today() - timedelta(days=31)
        else:
            start_date = date.fromisoformat(start_date)
        if not end_date:
            end_date = date.today()
        else:
            end_date = date.fromisoformat(end_date)

        if type(start_date) == datetime:
            start_date = start_date.date()

        if start_date < client.date_joined.date():
            start_date = client.date_joined.date()

        queryset = Review.objects.filter(client=client, date__range=(start_date, end_date))

        if tour_id and tour_id != 'all':
            tour_ids = [int(id) for id in tour_id.strip('[]').split(',')]
            if tour_ids:
                queryset = queryset.filter(tour_id__in=tour_ids)

        if country_id and country_id != 'all':
            country_ids = [int(id) for id in country_id.strip('[]').split(',')]
            if country_ids:
                queryset = queryset.filter(country_id__in=country_ids)

        if city_id and city_id != 'all':
            queryset = queryset.filter(city_id=city_id)

        queryset = queryset.filter(responded=False)

        queryset = queryset.annotate(
            country_code_annotation=F('country__code'),
            country_name_annotation=F('country__name')
        )

        queryset = queryset.exclude(country_code_annotation__isnull=True)
        # print(queryset.count())

        serialized_data = self.serializer_class(queryset, many=True).data

        return Response(serialized_data)


class CheckSyncAPIView(APIView):
    def get(self, request, review_id):
        client = request.user.created_by if request.user.created_by else request.user
        data = {
            "new_data": Review.objects.filter(client=client, id__gt=review_id, ai_checked=True).exists()
        }
        return Response(data)


class ReviewListAPIView(generics.ListAPIView):
    serializer_class = ReviewSerializer
    filter_backends = [filters.DjangoFilterBackend]
    filterset_class = ReviewFilter

    def get_queryset(self):
        client = self.request.user.created_by if self.request.user.created_by else self.request.user
        queryset = Review.objects.filter(ai_checked=True, client=client)
        queryset = queryset.order_by('-date')
        tour_id = self.request.query_params.get('tour_id', 'all')
        country_id = self.request.query_params.get('country_id', 'all')
        city_id = self.request.query_params.get('city_id', 'all')
        if agency := self.request.GET.get('source_stream'):
            for stream_id, stream_name in STREAM_CHOICES:
                if stream_name == agency:
                    break
            queryset = queryset.filter(source_stream=stream_id)

        if source_stream_id := self.request.GET.get('source_stream_id'):
            queryset = queryset.filter(source_stream=source_stream_id)

        if country := self.request.GET.get('country'):
            country = Country.objects.filter(id=country).first()
            queryset = queryset.filter(country_code=country.code)

        if tour := self.request.GET.get('tour'):
            tour = Tour.objects.filter(id=tour).first()
            queryset = queryset.filter(product=tour.name)

        if tour_name := self.request.GET.get('tour_name'):
            queryset = queryset.filter(product=tour_name)

        if responded := self.request.GET.get('responded'):
            if responded == 'true':
                queryset = queryset.filter(responded=True)
            else:
                queryset = queryset.filter(responded=False)

        if tour_id and tour_id != 'all':
            queryset = queryset.filter(tour_id=tour_id)

        if country_id and country_id != 'all':
            queryset = queryset.filter(country_id=country_id)

        if city_id and city_id != 'all':
            queryset = queryset.filter(city_id=city_id)

        sort_by = self.request.GET.get('sort_by', 'asc')
        if sort_by == 'desc':
            queryset = queryset.order_by('date').exclude(date=None)

        sort_by_rating = self.request.GET.get('sort_by_rating', 'asc')
        if sort_by_rating == 'desc':
            queryset = queryset.order_by('rating')

        if sentiments := self.request.GET.get('sentiment'):
            sentiments_list = sentiments.split(',')
            q_objects = Q()

            for sentiment in sentiments_list:
                if sentiment == '3':
                    q_objects |= Q(rating=5)
                elif sentiment == '2':
                    q_objects |= Q(rating=4)
                elif sentiment == '1':
                    q_objects |= Q(rating__lte=3)

            queryset = queryset.filter(q_objects)

        if date := self.request.GET.get('date'):
            date_obj = timezone.datetime.strptime(date, '%Y-%m-%d').date()
            queryset = queryset.filter(date=date_obj)

        queryset = queryset.filter(date__gte=self.request.user.date_joined)

        # print("REVIEW ID = ", queryset)
        # search_factor = tour_reviews_ai.tasks.get_text_from_id(export_schedule.search_factor)
        # test_email = tour_reviews_ai.tasks.task_schedule_email_report(queryset.id)
        # print("TEST EMAIL = ", test_email)

        page_size = self.request.query_params.get('page_size', settings.REST_FRAMEWORK['PAGE_SIZE'])
        self.pagination_class.page_size = page_size
        return queryset


class RespondToReview(APIView):
    def post(self, request):

        serializer = RespondReviewSerializer(data=request.data)
        if serializer.is_valid():
            review_id = serializer.validated_data.get('review_id')
            message = serializer.validated_data.get('message')
            try:
                review = Review.objects.get(id=review_id)
                if review.can_respond:
                    token_obj = ApiKeyStream.objects.filter(page_id=review.review_got_from,
                                                            status=Stream.CORRECT).filter()
                    token = token_obj.api_key
                    if review.source_stream == INSTAGRAM:
                        reply_instagram_comment(review, message, token)

                    elif review.source_stream == FACEBOOK:
                        reply_facebook_comment(review, message, token)

                    return Response({'message': 'Responded successfully.'}, status=status.HTTP_200_OK)

                else:
                    return Response({'message': 'Cannot respond to this review.'}, status=status.HTTP_404_NOT_FOUND)

            except Review.DoesNotExist:
                return Response({'error': 'Review not found.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import viewsets
from api.models import UrlStream, CredentialStream, ApiKeyStream, Company, STREAM_CHOICES, FACEBOOK, GOOGLE, INSTAGRAM, Stream
from api.serializers import UrlStreamSerializer, CredentialStreamSerializer, ApiKeyStreamSerializer, failure_message, \
    success_message
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from streams.scrapers.utilities import import_bot
from tour_reviews_ai.tasks import scrape
from streams.apis.facebook_apis import get_facebook_reviews, get_facebook_comments, get_instagram_comments
from api.utils import create_notification
from django.conf import settings


class UrlStreamViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UrlStreamSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['source_stream']

    def get_queryset(self):
        client = self.request.user.created_by if self.request.user.created_by else self.request.user

        queryset = UrlStream.objects.filter(user=client)
        if stream_id := self.request.GET.get('stream_id'):
            queryset = queryset.filter(source_stream=stream_id)
        return queryset

    def create(self, request, *args, **kwargs):
        client = request.user.created_by if request.user.created_by else request.user
        request.data['user'] = client.id
        is_adding_datastream = True

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        scrape.apply_async(args=[instance.id, 'UrlStream', is_adding_datastream])

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()


class CredentialStreamViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CredentialStreamSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['source_stream']

    def get_queryset(self):
        client = self.request.user.created_by if self.request.user.created_by else self.request.user
        queryset = CredentialStream.objects.filter(user=client)
        if stream_id := self.request.GET.get('stream_id'):
            queryset = queryset.filter(source_stream=stream_id)
        return queryset

    def create(self, request, *args, **kwargs):
        client = request.user.created_by if request.user.created_by else request.user
        request.data['user'] = client.id
        is_adding_datastream = True

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        scrape.apply_async(args=[instance.id, 'CredentialStream', is_adding_datastream])

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()


class ApiKeyStreamViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ApiKeyStreamSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['source_stream']

    def get_queryset(self):
        client = self.request.user.created_by if self.request.user.created_by else self.request.user
        queryset = ApiKeyStream.objects.filter(user=client)
        if stream_id := self.request.GET.get('stream_id'):
            queryset = queryset.filter(source_stream=stream_id)
        return queryset

    def create(self, request, *args, **kwargs):
        client = request.user.created_by if request.user.created_by else request.user
        request.data['user'] = client.id

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)

        if int(serializer.data['source_stream']) == FACEBOOK:
            res = get_facebook_reviews(instance)
        elif int(serializer.data['source_stream']) == INSTAGRAM:
            res = get_instagram_comments(instance)
        elif int(serializer.data['source_stream']) == GOOGLE:
            res = {'success': False}

        success = res['success']

        if success:
            instance.status = Stream.CORRECT
            create_notification(client, status=success_message['status'], text=success_message['text'], source_stream=serializer.data['source_stream'])
        else:
            instance.status = Stream.WRONG
            create_notification(client, status=failure_message['status'], text=failure_message['text'], source_stream=serializer.data['source_stream'])
        instance.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=201, headers=headers)

    def perform_create(self, serializer):
        return serializer.save()

    def get_streams(self, id_):
        matches = [text for (item_id, text) in STREAM_CHOICES if item_id == int(id_)]
        return matches[0] if matches else None

class StreamTemplateView(APIView):
    def get(self, request, stream_type, format=None):
        if stream_type == 8 or stream_type == 10 or stream_type == 9:
            return Response({
                'template': 'apikey',
                'fields': ['client_id', 'page_id', 'apikey']
            })
        elif stream_type == 2 or stream_type == 4 or stream_type == 1 or stream_type == 3:
            return Response({
                'template': 'url',
                'fields': ['client_id', 'product_name', 'url']
            })
        elif stream_type == 6 or stream_type == 7 or stream_type == 5:
            return Response({
                'template': 'credentials',
                'fields': ['client_id', 'username', 'password']
            })
        else:
            return Response({'error': 'Invalid stream type'}, status=400)



class StreamMaxView(APIView):
    def get(self, request, format=None):

        client = self.request.user.created_by if self.request.user.created_by else self.request.user
        apikey_queryset = ApiKeyStream.objects.filter(user=client).count()
        credential_queryset = CredentialStream.objects.filter(user=client).count()
        url_queryset = UrlStream.objects.filter(user=client).count()

        companies = Company.objects.filter(related_users=client)
        if companies.exists():
            company = companies.first()
            print(company)
            tot = apikey_queryset + credential_queryset + url_queryset
            if company.plan == settings.SMALL:
                if tot >= 5:
                    return Response({
                        'message': 'With you plan "Small Tour Operator" you can add just 5 streams, '
                                   'please, upgrade to a new plan!',
                    }, status=400)
            elif company.plan == settings.MEDIUM:
                if tot >= 15:
                    return Response({
                        'message': 'With you plan "Medium Tour Operator" you can add just 5 streams, '
                                   'please, upgrade to a new plan!',
                    }, status=400)
            elif company.plan == settings.LARGE:
                return Response({
                    'message': 'ok!',
                })
            else:
                return Response({
                    'message': 'You need a plan to be able to add streams!',
                }, status=400)
            return Response({
                'message': 'ok!',
            })


        return Response({'error': 'User dont have a company'}, status=400)
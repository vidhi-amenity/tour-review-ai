from rest_framework import viewsets, status
from rest_framework.response import Response
import pytz
from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from api.models import StandardCopyEmailAddress, Agency, STREAM_CHOICES, Tour, Country, City
from api.serializers import StandardCopyEmailAddressSerializer, CitySerializer, TourSerializer, CountrySerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
User = get_user_model()


class UserTimezoneViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['GET'])
    def get_timezone(self, request):
        user = request.user
        all_timezones = pytz.all_timezones

        return Response({'timezone': user.timezone, 'all_timezones': all_timezones})


class StandardCopyEmailAddressViewSet(viewsets.ViewSet):
    serializer_class = StandardCopyEmailAddressSerializer

    def list(self, request):
        user = request.user
        email_list = StandardCopyEmailAddress.objects.filter(user=user).values_list('email', flat=True)
        return Response(email_list)

    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            email_list = serializer.validated_data['email_list']
            user = request.user

            # add new email addresses
            for email in email_list:
                if not StandardCopyEmailAddress.objects.filter(user=user, email=email).exists():
                    StandardCopyEmailAddress.objects.create(user=user, email=email)

            # remove deleted email addresses
            existing_email_list = StandardCopyEmailAddress.objects.filter(user=user).values_list('email', flat=True)
            for email in existing_email_list:
                if email not in email_list:
                    StandardCopyEmailAddress.objects.filter(user=user, email=email).delete()

            return Response({'message': 'Email addresses updated successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AgencyStreamView(APIView):
    def get(self, request, format=None):

        stream_names = {}
        for k, v in STREAM_CHOICES:
            agency = Agency.objects.filter(user=request.user, stream=k).first()
            stream_names[v] = agency.name if agency else ""

        return Response(stream_names)

    def put(self, request, format=None):

        agencies = request.data
        stream_dict = dict(STREAM_CHOICES)

        for k in agencies:
            Agency.objects.update_or_create(
                stream=next((key for key, value in stream_dict.items() if value == k), None),
                defaults={
                    "user": request.user,
                    "name": agencies[k],
                }
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class ToursView(APIView):
    def get(self, request):
        client = request.user.created_by if request.user.created_by else request.user

        if source_stream := self.request.GET.get('source_stream'):
            for stream_id, stream_name in STREAM_CHOICES:
                if stream_name == source_stream:
                    source_stream = stream_id
                    break

        if source_stream:
            tour = Tour.objects.filter(stream=source_stream, client=client)
        else:
            tour = Tour.objects.filter(client=client)

        serializer = TourSerializer(tour, many=True)
        return Response(serializer.data)


class CountryList(APIView):
    def get(self, request):
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data)


class CityList(APIView):
    def get(self, request):
        countries = City.objects.all()
        serializer = CitySerializer(countries, many=True)
        return Response(serializer.data)
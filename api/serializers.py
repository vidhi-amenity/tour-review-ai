import json
from rest_framework import serializers
from .models import Review, SOURCE_STREAM, Agency, Country, Tour, UrlStream, CredentialStream, ApiKeyStream, \
    Notification, ExportSchedule, ScheduleEmailAddress, City, StreamNames
from authentication.models import User, Company
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from api.models import Notification
from django.core.exceptions import ValidationError
from authentication.serializers import CompanySerializer
from django.conf import settings


def validate_unique_email(value):
    exists = User.objects.filter(email=value)
    if exists:
        raise ValidationError("Email address %s already exists, please enter a different address." % value)


class StandardCopyEmailAddressSerializer(serializers.Serializer):
    email_list = serializers.ListField(child=serializers.EmailField())


class ReviewSerializer(serializers.ModelSerializer):
    sentiment_display = serializers.CharField(source='get_sentiment_display', read_only=True)
    source_stream_display = serializers.CharField(source='get_source_stream_display', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'date',
                  'source_stream',
                  'source_stream_display',
                  'review_text',
                  'rating',
                  'sentiment',
                  'sentiment_display',
                  'review_url',
                  'places',
                  'product',
                  'can_respond',
                  'responded',
                  'img',
                  'client']
    def to_representation(self, instance):
        representation = super(ReviewSerializer, self).to_representation(instance)

        representation['source_stream'] = SOURCE_STREAM[representation['source_stream']]
        representation['places'] = json.loads(instance.places) if instance.places else []

        # TODO in future implementation, filter user on the agency object
        agency = Agency.objects.filter(stream=representation['source_stream']['id']).first()
        representation['agency'] = agency.name if agency else ""
        return representation




class AgencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Agency
        fields = ('id', 'user', 'name', 'stream')



class RespondReviewSerializer(serializers.Serializer):
    review_id = serializers.IntegerField()
    message = serializers.CharField()

    def validate_review_id(self, value):
        try:
            review = Review.objects.get(id=value)
        except Review.DoesNotExist:
            raise serializers.ValidationError('Review not found.')
        return value

    def update(self, instance, validated_data):
        instance.message = validated_data.get('message', instance.message)
        instance.save()
        return instance


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'

class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'

class TourSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tour
        fields = '__all__'

class StreamNamesSerializer(serializers.ModelSerializer):
    class Meta:
        model = StreamNames
        fields = '__all__'

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'user_type']

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        companies = Company.objects.filter(related_users=instance)
        rep['company'] = None
        if companies.exists():
            company = companies.first()
            rep['company'] = CompanySerializer(company).data
            if rep['company']['plan']:
                rep['company']['plan'] = dict(settings.PLAN_CHOICES)[rep['company']['plan']]
        return rep


class ClientCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[validate_unique_email])
    
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role', 'user_type']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        username = validated_data.pop('email', None)
        password = validated_data.pop('password', None)
        name = validated_data.pop('name', None)
        role = validated_data.pop('role', 3)
        user_type = validated_data.pop('user_type', None)

        user = User(username=username,
                    email=username,
                    name=name,
                    role=role,
                    user_type=user_type,
                    )
        user.set_password(password)
        user.save()
        return user


class ClientUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'user_type']

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.role = validated_data.get('role', instance.role)
        instance.user_type = validated_data.get('user_type', instance.user_type)

        instance.save()
        return instance


class UserSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'user_type', 'created_by']
        extra_kwargs = {'created_by': {'read_only': True}}


class UserCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[validate_unique_email])
    created_by = serializers.ReadOnlyField(source='created_by.id')

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'password', 'role', 'user_type', 'created_by']
        extra_kwargs = {'password': {'write_only': True}}
        extra_kwargs = {'created_by': {'read_only': True}}

    def create(self, validated_data):
        username = validated_data.pop('email', None)
        password = validated_data.pop('password', None)
        name = validated_data.pop('name', None)
        user_type = validated_data.pop('user_type', None)
        created_by = validated_data.pop('created_by', None)

        if user_type == User.CONTENT_MANAGER:
            role = User.CLIENT
        else:
            role = User.USER

        user = User(username=username,
                    email=username,
                    name=name,
                    role=role,
                    user_type=user_type,
                    created_by=created_by
                    )
        user.set_password(password)

        user.save()
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.id')

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'user_type', 'created_by']
        extra_kwargs = {'created_by': {'read_only': True}}

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.email = validated_data.get('email', instance.email)
        instance.user_type = validated_data.get('user_type', instance.user_type)

        if instance.user_type == User.CONTENT_MANAGER:
            instance.role = User.CLIENT
        else:
            instance.role = User.USER

        instance.save()
        return instance
    

success_message = {
    "status": 1,
    "text": " entity added successfully."
}
failure_message = {
    "status": 3,
    "text": " entity could not be added, please check the data and verify it is correct before adding a new entity."
}

class UrlStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrlStream
        fields = ['id', 'user', 'source_stream', 'product_name', 'url', 'status']

    def validate_source_stream(self, value):
        if int(value) not in [2, 4, 1, 3]:
            raise serializers.ValidationError("Invalid source_stream for UrlStream")
        return value

    def create_notification(self, status, text):
        with transaction.atomic():
            notification = Notification(user=self.context['request'].user, client_field=self.context['request'].user.created_by if self.context['request'].user.created_by else self.context['request'].user, status=status, text=text)
            try:
                notification.save()
                print("Notification saved. Data:", vars(notification))  # print the data
            except Exception as e:
                print("Exception occurred:", e)  # print the exception if it occurs


class CredentialStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = CredentialStream
        fields = ['id', 'user','source_stream', 'username', 'password', 'status']

    def validate(self, value):
        if int(value['source_stream']) not in [6, 7, 5]:
            raise serializers.ValidationError("Invalid source_stream for CredentialStream")
        return value
    
    def create_notification(self, status, text):
        with transaction.atomic(): 
            notification = Notification(user=self.context['request'].user, client_field=self.context['request'].user.created_by if self.context['request'].user.created_by else self.context['request'].user, status=status, text=text)
            try:
                notification.save()
                print("Notification saved. Data:", vars(notification))  # print the data
            except Exception as e:
                print("Exception occurred:", e)  # print the exception if it occurs


class ApiKeyStreamSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApiKeyStream
        fields = ['id', 'user','source_stream', 'page_id', 'api_key', 'status']

    def validate_source_stream(self, value):
        if int(value) not in [8, 10, 9]:
            raise serializers.ValidationError("Invalid source_stream for ApiKeyStream")
        return value
    
    def create_notification(self, status, text):
        with transaction.atomic(): 
            notification = Notification(user=self.context['request'].user, client_field=self.context['request'].user.created_by if self.context['request'].user.created_by else self.context['request'].user, status=status, text=text)
            try:
                notification.save()
                print("Notification saved. Data:", vars(notification))  # print the data
            except Exception as e:
                print("Exception occurred:", e)



class ExportScheduleSerializer(serializers.ModelSerializer):
    search_factor = serializers.ChoiceField(choices=ExportSchedule.SEARCH_FACTOR)
    format = serializers.ChoiceField(choices=ExportSchedule.FORMAT)
    date_range_export = serializers.ChoiceField(choices=ExportSchedule.DATE_RANGE)
    email_addresses = serializers.PrimaryKeyRelatedField(queryset=ScheduleEmailAddress.objects.all(), many=True)

    class Meta:
        model = ExportSchedule
        fields = ('id', 'name', 'schedule', 'search_factor', 'format', 'date_range_export', 'email_addresses')


class ScheduleEmailAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduleEmailAddress
        fields = '__all__'

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'user', 'status', 'text', 'datetime', 'read', 'client_field']
        extra_kwargs = {'client_field': {'read_only': True}}
        extra_kwargs = {'user': {'read_only': True}}

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['status'] = instance.status
        return rep


class CreateCheckoutSessionSerializer(serializers.Serializer):
    test = serializers.BooleanField(required=False)
    success_url = serializers.CharField(required=False)
    plan = serializers.ChoiceField(choices=['SMALL', "MEDIUM", "LARGE"], required=True)
    cancel_url = serializers.CharField(required=False)

    # def validate(self, data):
    #     if Token.objects.filter(slug=self.initial_data['token_slug']).exists():
    #         return data
    #     raise serializers.ValidationError({
    #         'token_slug': f'The slug accepted are: {[{"name": item.name, "slug": item.slug } for item in Token.objects.all()]}'
    #     })


class ExportReportSerializer(serializers.ModelSerializer):
    email_addresses = serializers.PrimaryKeyRelatedField(queryset=ScheduleEmailAddress.objects.all(), many=True)

    class Meta:
        model = ExportSchedule
        fields = ('email_addresses', )

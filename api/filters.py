from django_filters import rest_framework as filters
from .models import Review
from authentication.models import User, Company
from django.utils.timezone import now
from django.conf import settings
from django.db.models import Q


class ReviewFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='date', lookup_expr='lte')
    min_rating = filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_rating = filters.NumberFilter(field_name='rating', lookup_expr='lte')

    class Meta:
        model = Review
        fields = ['start_date', 'end_date', 'min_rating', 'max_rating']


class UserFilter(filters.FilterSet):
    email = filters.CharFilter(field_name="email", lookup_expr='icontains')
    name = filters.CharFilter(field_name="name", lookup_expr='icontains')
    user_type = filters.CharFilter(field_name="user_type", lookup_expr='iexact')

    class Meta:
        model = User
        fields = ['email', 'name', 'user_type']


class CompanyFilter(filters.FilterSet):
    plan_active = filters.BooleanFilter(method='filter_by_subscription_status')
    plan_name = filters.ChoiceFilter(field_name="plan", choices=settings.PLAN_CHOICES)

    class Meta:
        model = Company
        fields = ['plan_active', 'plan_name']

    def filter_by_subscription_status(self, queryset, name, value):
        if value == True:
            return queryset.filter(subscription_ends__gte=now())
        elif value == False:
            return queryset.filter(Q(subscription_ends__lt=now()) | Q(subscription_ends__isnull=True))
        else:
            return queryset.filter(subscription_ends__lt=now())


from rest_framework import serializers
from .models import User, Company


class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'name', 'role', 'date_joined',
                  'timezone', 'company_name', 'phone', 'office_phone',
                  'gender', 'birthday', 'bio'
                  ]

    def to_representation(self, instance):
        representation = super(UserGetSerializer, self).to_representation(instance)
        representation['profile_image_path'] = None
        if instance.profile_image:
            representation['profile_image_path'] = f'/v1/auth/profile-image/{instance.id}/'
        return representation



class UserPutSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role',
                  'timezone', 'company_name', 'phone', 'office_phone',
                  'gender', 'birthday', 'bio', 'profile_image'
                  ]


class UserImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['profile_image']


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = ['id', 'name', 'subscription_ends', 'is_subscription_active', 'plan', 'subscription_renewal']


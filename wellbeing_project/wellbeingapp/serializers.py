from django.contrib.auth.models import User, Group
from rest_framework import serializers
from .models import *


# class UserListSerializer(serializers.ModelSerializer):
#     """ Return user name list """

#     class Meta:
#         model = User
#         fields = ["id", "first_name", "email"]

class UserProfileSerializer(serializers.ModelSerializer):
    """ Return user profile information """
    profile_email = serializers.SerializerMethodField(read_only=True)
    email = serializers.CharField(write_only=True)
    class Meta:
        model = UserProfile
        fields = ['profile_picture','profile_email','email']
        
    def get_profile_email(self,obj):
        return obj.user.email

    def update(self, instance, validated_data):
       
        instance.profile_picture = validated_data['profile_picture'] if validated_data['profile_picture'] else instance.profile_picture 
        # instance.company_logo = validated_data['company_logo'] if validated_data['company_logo'] else instance.company_logo 
        instance.user.email = validated_data.get('email',instance.user.email)
       
        instance.user.save()
        instance.save()
        return instance
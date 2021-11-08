from django.db import transaction,connection
from django.contrib.auth.models import User
from rest_framework import routers, serializers
from customers.models import Domain,Client,UserProfile

class UserSerilaizer(serializers.ModelSerializer):
    # password1 = serializers.CharField(max_length=128)
    class Meta:
        model = User
        fields = ['username','email','password']

class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = '__all__'
        
        
class DomainSerializer(serializers.ModelSerializer):
    client = ClientSerializer(source='domains',write_only=True)
    user = UserSerilaizer(write_only=True)
    class Meta:
        model = Domain
        fields = ['domain','client','user']
    
    
    def create(self, validated_data):
        
            if validated_data['domains']:
                client_object = Client.objects.create(**validated_data['domains'])
                validated_data.pop('domains')
                user_data = validated_data.get('user')
                validated_data.pop('user')
                validated_data['tenant']=client_object
                domain_object = Domain.objects.create(**validated_data)
                client_object.save()
                domain_object.save()
                connection.set_tenant(client_object)
                user_object = User.objects.create(**user_data)                
                user_object.save()
                return domain_object
            else:
                return
            
            
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
        print("=>",validated_data)
        instance.profile_picture = validated_data['profile_picture'] if validated_data['profile_picture'] else instance.profile_picture 
        instance.user.email = validated_data.get('email',instance.user.email)
        instance.user.save()
        instance.save()
        return instance
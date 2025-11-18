from rest_framework import serializers
from .models import CustomUser, Client, Company

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'email', 'username', 'role', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user


class ClientSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()
    company = serializers.PrimaryKeyRelatedField(many=True, queryset=Company.objects.all())

    class Meta:
        model = Client
        fields = [
            'id', 'user', 'company', 'country', 'state', 'city',
            'phone', 'area', 'status', 'created_by'
        ]
        read_only_fields = ['created_by']

    def create(self, validated_data):
        request = self.context['request']
        company_data = validated_data.pop('company')
        user_data = validated_data.pop('user')

        user_data['role'] = 'client'
        user = CustomUserSerializer().create(user_data)

        client = Client.objects.create(
            user=user,
            # created_by=request.user,
            **validated_data
        )

        client.company.set(company_data)
        return client

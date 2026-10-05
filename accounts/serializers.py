from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "role"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["email"],
            **validated_data,
        )
        return user
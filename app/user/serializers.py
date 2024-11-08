from typing import Dict, Any
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as trans
from rest_framework import serializers
from core.models import User


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ["email", "password", "name"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return user"""
        password = validated_data.pop("password", None)
        user: User = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(style={"input_type": "password"}, trim_whitespace=False)

    def validate(self, attrs: Dict[str, Any]):
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(request=self.context.get("request"), username=email, password=password)
        try:
            attrs["user"] = user
        except:
            msg = trans("unable to authenticate with provided credentials")
            raise serializers.ValidationError(msg, code="authorization")
        return attrs

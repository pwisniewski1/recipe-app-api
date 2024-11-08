from typing import Dict, Any
from django.contrib.auth import get_user_model, authenticate
from django.utils.translation import gettext as trans
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ["email", "password", "name"]
        extra_kwargs = {"password": {"write_only": True, "min_length": 5}}

    def create(self, validated_data):
        return get_user_model().objects.create_user(**validated_data)


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

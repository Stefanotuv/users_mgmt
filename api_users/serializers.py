from rest_framework import serializers
from users.models import User, Profile

class ProfileSerialiser(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'
class UserSerialiser(serializers.ModelSerializer):
    profile = ProfileSerialiser()
    class Meta:
        model = User
        # 'profile' is not an actual field in the User model, but it is a related_name of the profile field in Profile model.
        fields = ['id', 'email', 'name', 'username', 'is_staff', 'is_superuser', 'is_active', 'last_login',
                  'date_joined', 'groups', 'user_permissions', 'profile']

class UserSignupSerializer(serializers.Serializer):
    # username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    email = serializers.EmailField()

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def create(self, validated_data):
        user = User.objects.create(
            # username=validated_data['user'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
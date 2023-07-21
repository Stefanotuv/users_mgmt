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


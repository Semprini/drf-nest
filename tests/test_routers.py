import unittest

from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework import viewsets

from drf_nest.routers import NestedAppRouter


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupSerializer
    queryset = Group.objects.all()


class TestNestedAppRouter(unittest.TestCase):
    def setUp(self):
        self.package = ''

    def test_url(self):
        router = NestedAppRouter()
        (
            router.register(r'users', UserViewSet, 'user')
                  .register(r'groups', GroupViewSet, 'users-group', parents_query_lookups=['user'])
        )

        # test user list
        self.assertEqual(router.urls[0].name, 'user-list')

        # test user detail
        self.assertEqual(router.urls[2].name, 'user-detail')

        # test users group list
        self.assertEqual(router.urls[4].name, 'users-group-list')

        # test users group detail
        self.assertEqual(router.urls[6].name, 'users-group-detail')

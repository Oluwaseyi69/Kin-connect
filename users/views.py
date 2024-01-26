import datetime
import jwt
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status, authentication, permissions
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import UserSerializer


# Create your views here.
class RegisterView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
        return Response({"message": "User created successfully"}, status=status.HTTP_201_CREATED, )


class LoginView(APIView):
    def post(self, request):
        email = request.data['email']
        password = request.data['password']

        user = User.objects.filter(email=email).first()
        if not user:
            raise AuthenticationFailed('User does not exist')
        if not user.check_password(password):
            raise AuthenticationFailed('Incorrect credentials')

        payload = {
            'id': user.id,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            'iat': datetime.datetime.utcnow()
        }
        token = jwt.encode(payload, 'secret', algorithm='HS256')

        response = Response()
        response.set_cookie(key='token', value=token, httponly=True)
        response.data = {
            'jwt': token
        }
        return response


class UserView(APIView):
    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            return Response({'message': 'Successful login'}, status=status.HTTP_200_OK)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'Successful logout'
        }
        return response


# def receive_location(request):
#     if request.method != 'POST':
#         return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
#     latitude = request.POST.get('latitude')
#     longitude = request.POST.get('longitude')
#
#     request.session['user_latitude'] = latitude
#     request.session['user_longitude'] = longitude
#
#     return JsonResponse({'status': 'success'})


def receive_token(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': ''})
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('longitude')

    request.session['user_latitude'] = latitude
    request.session['user_longitude'] = longitude
    return JsonResponse({'status': 'success'})


# def show_map(request):
#     # Retrieve the stored user location from the session
#     user_latitude = request.session.get('user_latitude', None)
#     user_longitude = request.session.get('user_longitude', None)
#
#     return render(request, 'map.html', {'user_latitude': user_latitude, 'user_longitude': user_longitude})

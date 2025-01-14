from django.shortcuts import render
from .serializer import UserSerializer
# Create your views here.
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
# from rest_framework.status import Status
from .models import User
from rest_framework.exceptions import AuthenticationFailed
import jwt, datetime




class RegisterView(APIView):
  def post(self,request):
    serializer= UserSerializer(data=request.data)
    if serializer.is_valid():
      serializer.save()
    return Response(serializer.data)
  
  
class LoginView(APIView):
  def post(self,request):
    email=request.data['email']
    password=request.data['password']
    
    user=User.objects.filter(email=email).first()
    
    if user is None:
      raise AuthenticationFailed('User not found')
    
    
    if not user.check_password(password):
      raise AuthenticationFailed('Incorrect password')
    
    payload = {
          'id': user.id,
          'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
          'iat': datetime.datetime.utcnow()
      }

    token = jwt.encode(payload, 'secret', algorithm='HS256').decode('utf-8')

    response = Response()

    response.set_cookie(key='jwt', value=token, httponly=True)
    response.data = {
        'jwt': token
    }
    return response
    
    
    return Response({"message:success"})
  


class UserView(APIView):

    def get(self, request):
        token = request.COOKIES.get('jwt')

        if not token:
            raise AuthenticationFailed('Unauthenticated!')

        try:
            payload = jwt.decode(token, 'secret', algorithm=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Unauthenticated!')

        user = User.objects.filter(id=payload['id']).first()
        serializer = UserSerializer(user)
        return Response(serializer.data)


class LogoutView(APIView):
    def post(self, request):
        response = Response()
        response.delete_cookie('jwt')
        response.data = {
            'message': 'success'
        }
        return response
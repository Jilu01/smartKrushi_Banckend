from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import FarmerProfile
from .serializers import RegisterSerializer, LoginSerializer, FarmerProfileSerializer


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        refresh = RefreshToken.for_user(user)

        profile = getattr(user, 'farmer_profile', None)
        profile_data = FarmerProfileSerializer(profile).data if profile else {}

        return Response({
            "message": "Farmer registered successfully.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "profile": profile_data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        password = serializer.validated_data['password']

        user = authenticate(username=username, password=password)
        if not user:
            # Also allow login with phone number
            profile = FarmerProfile.objects.filter(phone_number=username).first()
            if profile:
                user = authenticate(username=profile.user.username, password=password)

        if not user:
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_active:
            return Response(
                {"error": "This account is inactive. Please contact support."},
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)
        profile = getattr(user, 'farmer_profile', None)
        profile_data = FarmerProfileSerializer(profile).data if profile else {}

        return Response({
            "message": "Login successful.",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_staff": user.is_staff,
            },
            "profile": profile_data,
            "tokens": {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile, _ = FarmerProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "full_name": request.user.get_full_name() or request.user.username,
                "state": "Gujarat"
            }
        )
        serializer = FarmerProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile, _ = FarmerProfile.objects.get_or_create(
            user=request.user,
            defaults={"full_name": request.user.username}
        )
        serializer = FarmerProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        profile, _ = FarmerProfile.objects.get_or_create(
            user=request.user,
            defaults={"full_name": request.user.username}
        )
        serializer = FarmerProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

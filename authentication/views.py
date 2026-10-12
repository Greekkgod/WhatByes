from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema, OpenApiResponse
from .serializers import RegisterSerializer, LoginSerializer, UserSerializer


class RegisterView(APIView):
    """
    Register a new user with name, email, and password.
    Endpoint: POST /api/auth/register/
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="Register a new user",
        description="Creates a new user account with name, email, and password.",
        request=RegisterSerializer,
        responses={
            201: OpenApiResponse(description="User registered successfully"),
            400: OpenApiResponse(description="Validation error"),
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "success": True,
                    "message": "User registered successfully.",
                    "data": {
                        "user": UserSerializer(user).data,
                        "tokens": {
                            "refresh": str(refresh),
                            "access": str(refresh.access_token),
                        },
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {
                "success": False,
                "error": {
                    "message": "Registration failed.",
                    "details": serializer.errors,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    """
    Log in a user and return a JWT token.
    Endpoint: POST /api/auth/login/
    """
    permission_classes = [AllowAny]

    @extend_schema(
        summary="User Login",
        description="Authenticates with email and password and returns JWT access and refresh tokens.",
        request=LoginSerializer,
        responses={
            200: OpenApiResponse(description="Login successful"),
            400: OpenApiResponse(description="Invalid request or credentials"),
        },
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data["user"]
            tokens = serializer.validated_data["tokens"]
            return Response(
                {
                    "success": True,
                    "message": "Login successful.",
                    "data": {
                        "user": UserSerializer(user).data,
                        "tokens": tokens,
                    },
                },
                status=status.HTTP_200_OK,
            )
        return Response(
            {
                "success": False,
                "error": {
                    "message": "Login failed.",
                    "details": serializer.errors,
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class CurrentUserView(APIView):
    """
    Get current logged in user details.
    Endpoint: GET /api/auth/me/
    """
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get Current User Profile",
        description="Returns profile information for the authenticated user.",
        responses={200: UserSerializer},
    )
    def get(self, request):
        return Response(
            {
                "success": True,
                "data": UserSerializer(request.user).data,
            },
            status=status.HTTP_200_OK,
        )

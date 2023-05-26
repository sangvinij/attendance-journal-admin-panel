from djoser.views import TokenCreateView

from .serializers import CustomTokenCreateSerializer


class CustomTokenCreateView(TokenCreateView):
    serializer_class = CustomTokenCreateSerializer

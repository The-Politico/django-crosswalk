from rest_framework import status
from rest_framework.response import Response

from crosswalk.authentication import AuthenticatedView


class ClientCheck(AuthenticatedView):
    def get(self, request):
        return Response(
            "Client configured correctly", status=status.HTTP_200_OK
        )

from crosswalk.authentication import AuthenticatedView
from rest_framework import status
from rest_framework.response import Response


class ClientCheck(AuthenticatedView):
    def get(self, request):
        return Response(
            {'message': 'Client configured correctly'},
            status=status.HTTP_200_OK
        )

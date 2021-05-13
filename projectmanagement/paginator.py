from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class NotFoundError(object):
    pass


class CustomPaginator(PageNumberPagination):
    page_size = 10  # Number of objects to return in one page

    def generate_response(self, query_set, serializer_obj, request):
        try:
            page_data = self.paginate_queryset(query_set, request)
        except NotFoundError:
            return Response({"error": "No results found for the requested page"}, status=status.HTTP_400_BAD_REQUEST)

        serialized_page = serializer_obj(page_data, many=True)
        return self.get_paginated_response(serialized_page.data)

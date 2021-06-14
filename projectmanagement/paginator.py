from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from projectmanagement.exceptions import CustomException


class NotFoundError(object):
    pass


class CustomPaginator(PageNumberPagination):
    page_size_query_param = 'limit'  # Number of objects to return in one page
    page_size = 10  # Default number of objects

    def generate_response(self, query_set, serializer_obj, request):
        try:
            page_data = self.paginate_queryset(query_set, request)
        except NotFoundError:
            raise CustomException(400, "No results were found for the requested page.")

        serialized_page = serializer_obj(page_data, many=True)
        return self.get_paginated_response(serialized_page.data)

from collections import OrderedDict
from rest_framework import pagination
from rest_framework.response import Response


class CustomPagination(pagination.PageNumberPagination):

    def paginate_queryset(self, queryset, request, view=None):
        self.page_size = request.query_params.get("page_size", self.page_size)
        return super(CustomPagination, self).paginate_queryset(
            queryset, request, view=None
        )

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("pages_number", self.page.paginator.num_pages),
                    ("results", data),
                ]
            )
        )

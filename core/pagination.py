from rest_framework.pagination import CursorPagination


class MaxLimitCursorPagination(CursorPagination):
    page_size = 20  # Default items per page
    max_page_size = 100  # Strict upper bound for page size
    page_size_query_param = "page_size"  # Allows clients to set custom limits
    ordering = "-id"

    def get_page_size(self, request):
        """
        Enforces a minimum page size and prevents clients from disabling
        pagination using ?page_size=None, ?page_size=0, or negative numbers.
        """
        page_size = super().get_page_size(request)

        # If the client sent 'none', '0', a invalid value, or negative int:
        if not page_size or page_size <= 0:
            return self.page_size

        return min(page_size, self.max_page_size)

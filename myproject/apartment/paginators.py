#Phan trang
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination


class ItemPagination(PageNumberPagination):
    page_size = 2
    
    
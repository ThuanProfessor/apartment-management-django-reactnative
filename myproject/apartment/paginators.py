#Phan trang
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination, CursorPagination


class ItemPagination(PageNumberPagination):
    page_size = 10
    page_size_quey_param = 'page_size'
    max_page_size = 100
    
    
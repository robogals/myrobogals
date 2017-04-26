"""
Helpful functions for rgteaching views
"""

from django.core.paginator import Paginator, EmptyPage


# Creates paginator for tables greater than size 'sizeOfList'
def paginatorRender(request, list_of_objects, size_of_list):
    paginator = Paginator(list_of_objects, size_of_list)
    page = request.GET.get('page')
    try:
        visits = paginator.page(page)
    except EmptyPage:
        visits = paginator.page(paginator.num_pages)
    except:
        visits = paginator.page(1)

    return visits

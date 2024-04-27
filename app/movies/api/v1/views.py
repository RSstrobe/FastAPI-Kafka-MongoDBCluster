from django.contrib.postgres.aggregates import ArrayAgg
from django.http import JsonResponse

from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from django.db.models import Q

from movies.models import Filmwork, PersonFilmwork


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ["get"]

    def get_queryset(self):
        query_set = (
            Filmwork.objects.prefetch_related("genres", "persons")
            .values()
            .annotate(
                genres=ArrayAgg(
                    "genrefilmwork__genre__name",
                    distinct=True,
                ),
                actors=ArrayAgg(
                    "personfilmwork__person__full_name",
                    distinct=True,
                    filter=Q(
                        personfilmwork__role__exact=PersonFilmwork.Roles.ACTOR.value
                    ),
                ),
                directors=ArrayAgg(
                    "personfilmwork__person__full_name",
                    distinct=True,
                    filter=Q(
                        personfilmwork__role__exact=PersonFilmwork.Roles.DIRECTOR.value
                    ),
                ),
                writers=ArrayAgg(
                    "personfilmwork__person__full_name",
                    distinct=True,
                    filter=Q(
                        personfilmwork__role__exact=PersonFilmwork.Roles.WRITER.value
                    ),
                ),
            )
            .order_by("title")
        )
        return query_set

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    page_size = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            self.get_queryset(), self.page_size
        )
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            "results": list(queryset),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, **kwargs):
        context = self.get_queryset().get(pk=self.kwargs.get("pk"))

        return context

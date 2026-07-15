from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from hr_management.services.search_service import SearchService

class GlobalSearchView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('q', '').strip()
        results = SearchService.global_search(query)
        return Response({"results": results})

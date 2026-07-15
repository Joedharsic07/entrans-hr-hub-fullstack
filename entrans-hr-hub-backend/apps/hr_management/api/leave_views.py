from rest_framework import generics, permissions, status
from rest_framework.response import Response
from hr_management.models.leave import LeaveRequest
from hr_management.serializers.leave import LeaveRequestSerializer, LeaveBalanceSerializer
from hr_management.services.leave_service import LeaveService

class LeaveRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LeaveService.get_leave_requests(self.request.user)

    def perform_create(self, serializer):
        serializer.save(employee=self.request.user)

class LeaveRequestDetailView(generics.RetrieveUpdateAPIView):
    serializer_class = LeaveRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = LeaveRequest.objects.all()

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        
        new_status = request.data.get('status')
        if new_status and instance.status != 'approved':
            if not request.user.is_staff:
                return Response({"error": "Only admins can change leave status."}, status=status.HTTP_403_FORBIDDEN)
                
            if new_status == 'approved':
                try:
                    LeaveService.approve_leave_request(instance, request.user)
                except ValueError as ve:
                    return Response({"error": str(ve)}, status=status.HTTP_400_BAD_REQUEST)
                except PermissionError as pe:
                    return Response({"error": str(pe)}, status=status.HTTP_403_FORBIDDEN)
            
        return super().update(request, *args, **kwargs)

    def perform_update(self, serializer):
        new_status = self.request.data.get('status')
        if new_status and self.request.user.is_staff and serializer.instance.status != 'approved':
            rejection_reason = self.request.data.get('rejection_reason', serializer.instance.rejection_reason)
            serializer.save(status=new_status, approver=self.request.user, rejection_reason=rejection_reason)
        else:
            serializer.save()

class LeaveBalanceListView(generics.ListAPIView):
    serializer_class = LeaveBalanceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return LeaveService.ensure_balances_exist(self.request.user)

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.core.cache import cache
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count

from .models import Task
from .serializers import TaskSerializer, TaskCreateSerializer, TaskListSerializer
from .tasks import process_task


class TaskViewSet(viewsets.ModelViewSet):
    """
    A unified ViewSet for managing tasks.
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter, filters.SearchFilter]
    filterset_fields = ['status']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'status']
    ordering = ['-created_at']
    lookup_field = 'id'

    def get_queryset(self):
        """
        Regular users see their own tasks.
        Admins see all tasks.
        """
        queryset = Task.objects.all()
        user = self.request.user

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        # Optional date range filter
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')

        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        return queryset

    def get_serializer_class(self):
        """
        Return different serializers depending on request type.
        """
        if self.action == 'create':
            return TaskCreateSerializer
        elif self.action == 'list':
            return TaskListSerializer
        return TaskSerializer

    def create(self, request, *args, **kwargs):
        """
        Create a task and trigger a Celery background job.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save(user=request.user)

        # Run Celery task in background
        celery_task = process_task.delay(task.id)
        task.celery_task_id = celery_task.id
        task.save()

        response_serializer = TaskSerializer(task)
        return Response(
            {'task': response_serializer.data, 'message': 'Task created and processing started'},
            status=status.HTTP_201_CREATED
        )

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a task (cached for 5 minutes).
        """
        task_id = kwargs.get('id')
        cache_key = f"task:{task_id}"

        cached_data = cache.get(cache_key)
        if cached_data:
            return Response({'task': cached_data, 'cached': True})

        task = self.get_object()
        serializer = self.get_serializer(task)
        cache.set(cache_key, serializer.data, timeout=300)

        return Response({'task': serializer.data, 'cached': False})

    def destroy(self, request, *args, **kwargs):
        """
        Delete a task and invalidate its cache.
        """
        task = self.get_object()
        cache.delete(f"task:{task.id}")
        task.delete()

        return Response(
            {'message': f'Task {task.id} deleted successfully'},
            status=status.HTTP_200_OK
        )

    # -----------------------------
    # Custom Actions
    # -----------------------------

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser])
    def admin_view(self, request):
        """
        Admin-only endpoint: View all tasks (optional status filter).
        GET /api/tasks/admin_view/
        """
        tasks = Task.objects.all()
        status_filter = request.query_params.get('status')
        if status_filter:
            tasks = tasks.filter(status=status_filter)

        serializer = TaskSerializer(tasks, many=True)
        return Response({'count': tasks.count(), 'tasks': serializer.data})

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get user-specific task statistics.
        GET /api/tasks/stats/
        """
        user = request.user
        stats = (
            Task.objects.filter(user=user)
            .values('status')
            .annotate(count=Count('id'))
        )
        total = Task.objects.filter(user=user).count()

        return Response({'stats': list(stats), 'total': total})

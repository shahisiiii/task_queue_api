from django.contrib import admin
from apps.tasks.models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'user__username')
    readonly_fields = ('id', 'celery_task_id', 'created_at', 'updated_at')
    list_per_page = 25
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'user', 'title', 'description')
        }),
        ('Status', {
            'fields': ('status', 'celery_task_id')
        }),
        ('Result', {
            'fields': ('result',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        # Prevent manual task creation through admin
        return False

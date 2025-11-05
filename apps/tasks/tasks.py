import time
import random
from celery import shared_task
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from .models import Task
@shared_task(bind=True, max_retries=3)
def process_task(self, task_id):
    """
    Simulates a long-running background task.
    Runs for a random duration between 10–20 seconds.
    Stores only a string result message instead of structured data.
    """
    try:
        task = Task.objects.get(id=task_id)

        # Mark task as processing
        task.status = 'PROCESSING'
        task.celery_task_id = self.request.id
        task.save()

        # Invalidate cache
        cache.delete(f"task:{task.id}")

        # Simulate processing (random delay between 10–20 seconds)
        duration = random.randint(10, 20)
        time.sleep(duration)

        # Mark task as completed
        task.status = 'COMPLETED'
        task.result = f"Task completed successfully in {duration} seconds at {timezone.now().isoformat()}"
        task.save()

        # Invalidate cache again after completion
        cache.delete(f"task:{task.id}")

        return {
            'task_id': task_id,
            'status': 'COMPLETED',
            'result': task.result
        }

    except Task.DoesNotExist:
        return {
            'task_id': task_id,
            'status': 'FAILED',
            'error': 'Task not found'
        }

    except Exception as e:
        # Handle unexpected failure
        try:
            task.status = 'FAILED'
            task.result = f"Task failed due to: {str(e)}"
            task.save()
            cache.delete(f"task:{task.id}")
        except Exception:
            pass

        # Retry after 60 seconds (max 3 retries)
        raise self.retry(exc=e, countdown=60)



@shared_task
def cleanup_old_tasks():
    """
    Periodic task to clean up old completed/failed tasks
    Runs daily via Celery Beat
    """
    # Delete tasks older than 30 days
    threshold_date = timezone.now() - timedelta(days=30)
    
    deleted_count = Task.objects.filter(
        created_at__lt=threshold_date,
        status__in=['COMPLETED', 'FAILED']
    ).delete()[0]
    
    return {
        'deleted_count': deleted_count,
        'threshold_date': threshold_date.isoformat()
    }


@shared_task
def generate_task_summary():
    """
    Generate a summary of all tasks
    """
    from django.db.models import Count
    
    summary = Task.objects.values('status').annotate(
        count=Count('id')
    )
    
    return {
        'summary': list(summary),
        'generated_at': timezone.now().isoformat()
    }
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from tasks.models import Task
import random


class Command(BaseCommand):
    help = 'Create sample users and tasks for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=5,
            help='Number of users to create'
        )
        parser.add_argument(
            '--tasks',
            type=int,
            default=20,
            help='Number of tasks to create'
        )
    
    def handle(self, *args, **options):
        num_users = options['users']
        num_tasks = options['tasks']
        
        self.stdout.write('Creating sample data...')
        
        # Create users
        users = []
        for i in range(num_users):
            username = f'user{i+1}'
            email = f'user{i+1}@example.com'
            
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': email,
                    'first_name': f'User',
                    'last_name': f'{i+1}'
                }
            )
            
            if created:
                user.set_password('TestPass123!')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {username}'))
            
            users.append(user)
        
        # Create tasks
        statuses = ['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED']
        task_titles = [
            'Process customer data',
            'Generate monthly report',
            'Import CSV file',
            'Send email notifications',
            'Backup database',
            'Sync user accounts',
            'Calculate statistics',
            'Export data to Excel',
            'Clean up old files',
            'Update product inventory'
        ]
        
        for i in range(num_tasks):
            user = random.choice(users)
            title = random.choice(task_titles)
            status = random.choice(statuses)
            progress = random.randint(0, 100) if status != 'PENDING' else 0
            
            task = Task.objects.create(
                user=user,
                title=f'{title} #{i+1}',
                description=f'Sample task description for {title}',
                status=status,
                progress=progress,
                result={'sample': 'data'} if status == 'COMPLETED' else None
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created task: {task.title} ({task.status})')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\\nSuccessfully created {num_users} users and {num_tasks} tasks'
            )
        )

from django.apps import AppConfig
from django.contrib.auth import get_user_model

class TicketsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tickets'

    def ready(self):
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin','admin@example.com','adminpass',role='admin')
        if not User.objects.filter(username='agent1').exists():
            User.objects.create_user('agent1','agent1@example.com','agentpass',role='agent')
        if not User.objects.filter(username='user1').exists():
            User.objects.create_user('user1','user1@example.com','userpass',role='user')

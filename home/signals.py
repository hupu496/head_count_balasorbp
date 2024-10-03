from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MonitorData

@receiver(post_save, sender=MonitorData)
def monitor_data_created(sender, instance, created, **kwargs):
    if created:
        # Perform actions after a new MonitorData instance is created
        print(f"New MonitorData created: {instance.id}")
        # Add your logic here

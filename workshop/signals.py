# workshop/signals.py
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import WorkOrder
from .utils import send_status_update_email
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=WorkOrder)
def workorder_pre_save(sender, instance, **kwargs):
    """Handle pre_save signal to detect status changes"""
    logger.info(f"✅ PRE_SAVE Signal triggered for WorkOrder {getattr(instance, 'work_order_number', 'NEW')}")
    
    if not instance.pk:
        # New instance being created
        logger.info(f"New WorkOrder being created")
        return
    
    try:
        old_instance = WorkOrder.objects.get(pk=instance.pk)
        logger.info(f"Old status: {old_instance.status}, New status: {instance.status}")
        
        if old_instance.status != instance.status:
            logger.info(f"🚀 STATUS CHANGED: {old_instance.status} -> {instance.status}")
            # Store the fact that status changed for post_save handling
            instance._status_changed = True
            
    except WorkOrder.DoesNotExist:
        logger.warning(f"Could not find old instance for WorkOrder {instance.pk}")

@receiver(post_save, sender=WorkOrder)
def workorder_post_save(sender, instance, created, **kwargs):
    """Handle post_save signal to send emails"""
    logger.info(f"✅ POST_SAVE Signal triggered for WorkOrder {instance.work_order_number} (created: {created})")
    
    if created:
        logger.info(f"New WorkOrder created: {instance.work_order_number}")
        return

    # Check if status was changed (flag set in pre_save)
    if hasattr(instance, '_status_changed') and instance._status_changed:
        logger.info(f"🚀 Sending email for status change: {instance.work_order_number}")
        send_status_update_email(instance)
    else:
        logger.info(f"No status change detected for {instance.work_order_number}")
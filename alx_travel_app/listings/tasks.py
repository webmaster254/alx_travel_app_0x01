from celery import shared_task
import logging

logger = logging.getLogger(__name__)

@shared_task
def example_task(param):
    """
    Example task that demonstrates how to create Celery tasks.
    
    This is just a sample that logs a message. In a real application,
    you might use tasks for:
    - Sending confirmation emails
    - Processing travel booking requests
    - Generating reports
    - Syncing data with external services
    - Scheduled cleanup operations
    """
    logger.info(f"Running example task with parameter: {param}")
    # Simulate work
    import time
    time.sleep(5)
    return f"Task completed with parameter: {param}"


@shared_task
def send_booking_confirmation(booking_id):
    """
    Send a confirmation email for a new booking.
    
    In a real application, this would connect to an email service
    and send an actual email with booking details.
    """
    logger.info(f"Sending confirmation for booking {booking_id}")
    # In a real application, you would:
    # 1. Fetch booking details from the database
    # 2. Generate email content with booking information
    # 3. Send email using an email service
    return f"Confirmation sent for booking {booking_id}"


@shared_task
def process_payment(payment_id, amount):
    """
    Process a payment through a payment gateway.
    
    This would typically involve communicating with external payment services
    which could take time and should be done asynchronously.
    """
    logger.info(f"Processing payment {payment_id} for ${amount}")
    # In a real application, you would:
    # 1. Connect to payment gateway
    # 2. Process the payment
    # 3. Update payment status in the database
    return f"Payment {payment_id} processed successfully"

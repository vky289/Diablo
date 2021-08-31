from datetime import timedelta, datetime
from pytz import timezone
from app.core.models import RQQueue
from django_rq import job

central = timezone('US/Central')


@job('scheduler')
def clean_up_rq_tab():
    end_date = (datetime.now(central) - timedelta(days=30))
    com = RQQueue.objects.filter(created_at__lt=end_date)
    total_records = len(com)
    com.delete()
    return total_records

from django_rq import job
import logging

from app.dbs.models import DBInstance, DBCompareDBResults
from app.core.models import RQQueue
from utils.compare_database import any_db
from utils.truncate_table import delete
from utils.copy_table import xerox
from utils.script_scrapper import scrapper

from redis import Redis
from rq.registry import FinishedJobRegistry, StartedJobRegistry
from rq.job import Job
from django.utils.timezone import make_aware

logger = logging.getLogger(__name__)


redis = Redis(host="diablo-redis", db=0, port=6379, socket_connect_timeout=10, socket_timeout=10)


def store_started_job(job_ids, flag=1):
    # flag 1 = Start
    # flag 2 = Finished
    for j_id in job_ids:
        try:
            bj = RQQueue.objects.filter(name=j_id)
            job_q = Job.fetch(j_id, connection=redis)
            if bj:
                abj = RQQueue.objects.filter(name=j_id)[0]
                if job_q.started_at is not None and flag == 1:
                    abj.created_at = make_aware(job_q.started_at)
                if job_q.ended_at is not None and flag == 2:
                    abj.ended_at = make_aware(job_q.ended_at)
                abj.status = job_q._status
                abj.save()
            else:
                r_obj = RQQueue.objects.filter(name=job_q.id)
                if not r_obj:
                    obj = RQQueue()
                    obj.name = job_q.id
                    obj.func_name = job_q.func_name
                    obj.compare_dbs = job_q.args[3]
                    if job_q.started_at is not None and flag == 1:
                        obj.created_at = make_aware(job_q.started_at)
                    if job_q.ended_at is not None and flag == 2:
                        obj.ended_at = make_aware(job_q.ended_at)
                    obj.status = job_q._status
                    obj.save()
        except:
            pass


def get_current_queue_items():
    started_registry = StartedJobRegistry('default', connection=redis)
    started_registry_high = StartedJobRegistry('high', connection=redis)
    started_registry_low = StartedJobRegistry('low', connection=redis)

    store_started_job(started_registry.get_job_ids())
    store_started_job(started_registry_high.get_job_ids())
    store_started_job(started_registry_low.get_job_ids())


def wrap_up_job():
    finished_registry = FinishedJobRegistry('default', connection=redis)
    finished_registry_high = FinishedJobRegistry('high', connection=redis)
    finished_registry_low = FinishedJobRegistry('low', connection=redis)

    store_started_job(finished_registry.get_job_ids(), 2)
    store_started_job(finished_registry_high.get_job_ids(), 2)
    store_started_job(finished_registry_low.get_job_ids(), 2)


@job('high')
def compare_db_rows(user, src_db, dst_db, compare_db):
    get_current_queue_items()
    any_db(user, src_db, dst_db, compare_db).row_count_db()
    wrap_up_job()


@job('low')
def compare_db_data_types(user, src_db, dst_db, compare_db):
    get_current_queue_items()
    any_db(user, src_db, dst_db, compare_db).table_data_type_db()
    try:
        com = DBCompareDBResults.objects.get(compare_dbs=compare_db)
        com.status = 1
    except DBCompareDBResults.DoesNotExist:
        pass
    wrap_up_job()


@job('low')
def compare_db_tables_fk_ui(user, src_db, dst_db, compare_db):
    get_current_queue_items()
    any_db(user, src_db, dst_db, compare_db).table_column_pk_ui_comparision()
    try:
        com = DBCompareDBResults.objects.get(compare_dbs=compare_db)
        com.status = 1
    except DBCompareDBResults.DoesNotExist:
        pass
    wrap_up_job()


@job('low')
def compare_db_views(user, src_db, dst_db, compare_db):
    get_current_queue_items()
    any_db(user, src_db, dst_db, compare_db).cdata_view()
    wrap_up_job()


@job('low')
def compare_db_ind(user, src_db, dst_db, compare_db):
    get_current_queue_items()
    any_db(user, src_db, dst_db, compare_db).cdata_ind()
    wrap_up_job()


@job('low')
def compare_db_seq(user, src_db, dst_db, compare_db):
    get_current_queue_items()
    any_db(user, src_db, dst_db, compare_db).cdata_seq()
    wrap_up_job()


@job('low')
def compare_db_fk(user, src_db, dst_db, compare_db):
    get_current_queue_items()
    any_db(user, src_db, dst_db, compare_db).fk_db()
    wrap_up_job()


@job('low')
def compare_db_trig(user, src_db, dst_db, compare_db):
    get_current_queue_items()
    any_db(user, src_db, dst_db, compare_db).cdata_trig()
    wrap_up_job()


@job('low')
def truncate_table(user, dst_db, table_name):
    get_current_queue_items()
    delete(user, dst_db=dst_db).execute_it(table_name)
    wrap_up_job()


@job('default')
def copy_table_content(user, src_db, dst_db, table_name, row_count, upper_bound, commit_each=False):
    get_current_queue_items()
    xerox(user, src_db=src_db, dst_db=dst_db, table_name=table_name, table_row_count=row_count, upper_bound=upper_bound,
          commit_each=commit_each).execute_it()
    wrap_up_job()


@job('default')
def delete_instance_n_its_data(instance_id):
    get_current_queue_items()
    DBInstance.objects.get(id=instance_id).delete()
    wrap_up_job()

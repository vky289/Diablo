from django_rq import job
import logging

from app.dbs.models import DBInstance
from utils.compare_database import any_db
from utils.truncate_table import delete
from utils.copy_table import xerox
from utils.script_scrapper import scrapper

logger = logging.getLogger(__name__)


@job('high')
def compare_db_rows(user, src_db, dst_db, compare_db):
    any_db(user, src_db, dst_db, compare_db).row_count_db()


@job('low')
def compare_db_data_types(user, src_db, dst_db, compare_db):
    any_db(user, src_db, dst_db, compare_db).table_data_type_db()


@job('low')
def compare_db_views(user, src_db, dst_db, compare_db):
    any_db(user, src_db, dst_db, compare_db).cdata_view()


@job('low')
def compare_db_ind(user, src_db, dst_db, compare_db):
    any_db(user, src_db, dst_db, compare_db).cdata_ind()


@job('low')
def compare_db_seq(user, src_db, dst_db, compare_db):
    any_db(user, src_db, dst_db, compare_db).cdata_seq()


@job('low')
def compare_db_fk(user, src_db, dst_db, compare_db):
    any_db(user, src_db, dst_db, compare_db).fk_db()


@job('low')
def compare_db_trig(user, src_db, dst_db, compare_db):
    any_db(user, src_db, dst_db, compare_db).cdata_trig()


@job('low')
def truncate_table(user, dst_db, table_name):
    delete(user, dst_db=dst_db).execute_it(table_name)


@job('default')
def copy_table_content(user, src_db, dst_db, table_name, row_count, upper_bound, commit_each=False):
    xerox(user, src_db=src_db, dst_db=dst_db, table_name=table_name, table_row_count=row_count, upper_bound=upper_bound,
          commit_each=commit_each).execute_it()


@job('default')
def delete_instance_n_its_data(instance_id):
    DBInstance.objects.get(id=instance_id).delete()

from django_rq import job
import logging

from utils.compare_database import any_db
from utils.truncate_table import delete
from utils.copy_table import xerox
from utils.script_scrapper import scrapper
from utils.common_func import send_notification

logger = logging.getLogger(__name__)


@job
def compare_db_rows(user, src_db, dst_db, compare_db):
    try:
        any_db(user, src_db, dst_db, compare_db).c_db()
        send_notification(user, "DB {} -> {} table comparison completed".format(src_db.name, dst_db.name))
    except Exception as e:
        send_notification(user, "DB {} -> {} exception occurred during table comparison - {}".format(src_db.name, dst_db.name, e))


@job
def compare_db_data_types(user, src_db, dst_db, compare_db):
    try:
        any_db(user, src_db, dst_db, compare_db).cdata_db()
        send_notification(user, "DB {} -> {} datatype comparison completed".format(src_db.name, dst_db.name))
    except Exception as e:
        send_notification(user, "DB {} -> {} exception occurred during datatype comparison- {}".format(src_db.name, dst_db.name, e))


@job
def compare_db_views(user, src_db, dst_db, compare_db):
    try:
        any_db(user, src_db, dst_db, compare_db).cdata_view()
        send_notification(user, "DB {} -> {} View comparison completed".format(src_db.name, dst_db.name))
    except Exception as e:
        send_notification(user, "DB {} -> {} exception occurred during View comparison- {}".format(src_db.name, dst_db.name, e))


@job
def compare_db_seq(user, src_db, dst_db, compare_db):
    try:
        any_db(user, src_db, dst_db, compare_db).cdata_seq()
        send_notification(user, "DB {} -> {} Sequence comparison completed".format(src_db.name, dst_db.name))
    except Exception as e:
        send_notification(user, "DB {} -> {} exception occurred during Sequence comparison- {}".format(src_db.name, dst_db.name, e))


@job
def truncate_table(user, dst_db, table_name):
    try:
        delete(dst_db=dst_db).execute_it(table_name)
        send_notification(user, "DB {} Truncated table - {}".format(dst_db.name, table_name))
    except Exception as e:
        send_notification(user, "DB {} exception occurred during truncate table - {}- {}".format(dst_db.name, table_name, e))

@job
def copy_table_content(user, src_db, dst_db, table_name, row_count, upper_bound, commit_each=False):
    try:
        xerox(src_db=src_db, dst_db=dst_db, table_name=table_name, table_row_count=row_count, upper_bound=upper_bound,
              commit_each=commit_each).execute_it()
        send_notification(user, "DB {} -> {} table content copied - {}".format(src_db.name, dst_db.name, table_name))
    except Exception as e:
        send_notification(user, "DB {} -> {} exception occurred during copy of table - {}- {}".format(src_db.name, dst_db.name, table_name, e))

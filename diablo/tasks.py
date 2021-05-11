from django_rq import job
import logging

from utils.compare_database import any_db
from utils.truncate_table import delete
from utils.copy_table import xerox
from utils.script_scrapper import scrapper

logger = logging.getLogger(__name__)


@job
def compare_db_rows(src_db, dst_db):
    any_db(src_db, dst_db).c_db()\


@job
def compare_db_data_types(src_db, dst_db):
    any_db(src_db, dst_db).cdata_db()


@job
def truncate_table(dst_db, table_name):
    delete(dst_db=dst_db).execute_it(table_name)


@job
def copy_table_content(src_db, dst_db, table_name, row_count, upper_bound, commit_each=False):
    xerox(src_db=src_db, dst_db=dst_db, table_name=table_name, table_row_count=row_count, upper_bound=upper_bound,
          commit_each=commit_each).execute_it()

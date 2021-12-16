import logging
from utils.script_scrapper import scrapper
from utils.queries import P_TRUNC_Q, O_TRUNC_Q
from utils.enums import DbType
from utils.common_func import send_notification


class delete:
    def __init__(self, user, dst_db):
        self.log = logging.getLogger(__name__)
        self.user = user
        self.dst_db = dst_db
        self.dst_db_type = self.dst_db.type

    def execute_it(self, table_name):
        try:
            if self.dst_db_type == DbType.POSTGRES:
                scrapper(main_db=self.dst_db).run_query_no_result(table_name=table_name,
                                                                  SCRIPT_Q=P_TRUNC_Q)
            send_notification(self.user, "DB {} Truncated table - {}".format(self.dst_db.name, table_name))
        except Exception as e:
            send_notification(self.user, "DB {} exception occurred during truncate table - {}- {}".format(self.dst_db.name, table_name, e))
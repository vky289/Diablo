import logging
from utils.script_scrapper import scrapper
from utils.queries import P_TRUNC_Q, O_TRUNC_Q
from utils.enums import DbType


class delete:
    def __init__(self, dst_db):
        self.log = logging.getLogger(__name__)
        self.dst_db = dst_db
        self.dst_db_type = self.dst_db.type

    def execute_it(self, table_name):
        if self.dst_db_type == DbType.POSTGRES:
            scrapper(db_type=self.dst_db_type,
                     main_db=self.dst_db).run_query_no_result(table_name=table_name,
                                                              SCRIPT_Q=P_TRUNC_Q)
        # else:
        #     scrapper(db_type=self.dst_db_type,
        #              main_db=self.dst_db).run_query_no_result(table_name=table_name,
        #                                                       SCRIPT_Q=O_TRUNC_Q)
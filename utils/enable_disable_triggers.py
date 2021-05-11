import logging
from utils.script_scrapper import scrapper
from utils.queries import P_ALL_TAB_SCRIPT_Q, P_EN_TRIG_Q, P_DIS_TRIG_Q


class triggers:
    def __init__(self, dst_db):
        self.log = logging.getLogger(__name__)
        self.dst_db = dst_db
        self.dst_db_type = self.dst_db.type

    def execute_it(self, ty, table_name=None):
        schema_name =self.dst_db.sid
        if schema_name is None or schema_name == '':
            schema_name = self.dst_db.service
        if table_name is None:
            if ty == 'ENABLE':
                data = scrapper(self.dst_db_type,
                                self.dst_db).run_query_with_results(schema_name=schema_name,
                                                                    SCRIPT_Q=P_ALL_TAB_SCRIPT_Q)
                for d in data:
                    scrapper(self.dst_db_type,
                             self.dst_db).run_query_no_result(table_name=d,
                                                              SCRIPT_Q=P_EN_TRIG_Q)
            if ty == 'DISABLE':
                data = scrapper(self.dst_db_type,
                                self.dst_db).run_query_with_results(schema_name=schema_name,
                                                                    SCRIPT_Q=P_ALL_TAB_SCRIPT_Q)
                for d in data:
                    scrapper(self.dst_db_type,
                             self.dst_db).run_query_no_result(table_name=d,
                                                              SCRIPT_Q=P_DIS_TRIG_Q)
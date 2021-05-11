O_RET_TABLE_ROW_QUERY = '''SELECT * FROM (SELECT aabc.*, row_number() over (order by :PK_COL) as row_num FROM {TAB} aabc ORDER BY :PK_COL) 
        WHERE 
        row_num BETWEEN :LOWER_BOUND AND 
        :UPPER_BOUND'''
O_TABLE_Q = '''SELECT * from :TABLE'''
P_TABLE_Q = '''SELECT * from %s'''
O_EN_TRIG_Q = '''ALTER TABLE :TAB ENABLE TRIGGER ALL'''
P_EN_TRIG_Q = '''ALTER TABLE %s ENABLE TRIGGER ALL'''
O_DIS_TRIG_Q = '''ALTER TABLE :TAB DISABLE TRIGGER ALL'''
P_DIS_TRIG_Q = '''ALTER TABLE %s DISABLE TRIGGER ALL'''
O_TRUNC_Q = '''TRUNCATE TABLE :TAB'''
P_TRUNC_Q = '''TRUNCATE TABLE %s'''
O_SEQ_SCRIPT_Q = "SELECT SEQUENCE_NAME FROM ALL_SEQUENCES where SEQUENCE_NAME LIKE 'S_%' AND  SEQUENCE_OWNER = :SCHEMA"
P_SEQ_SCRIPT_Q = "select UPPER(sequence_name) from INFORMATION_SCHEMA.sequences where sequence_schema = %(SCHEMA)s"
O_ALL_TAB_SCRIPT_Q = "SELECT UPPER(table_name) as table_name FROM ALL_TABLES WHERE OWNER = :SCH"
P_ALL_TAB_SCRIPT_Q = "SELECT UPPER(table_name) as table_name FROM information_schema.tables WHERE table_schema= %(SCH)s"
O_VW_SCRIPT_Q = "select view_name from all_views where OWNER = :SCHEMA"
P_VW_SCRIPT_Q = "select UPPER(table_name) from INFORMATION_SCHEMA.views WHERE table_schema= %(SCHEMA)s"
O_TRIG_SCRIPT_Q = "select trigger_name from all_triggers where OWNER = :SCHEMA"
P_TRIG_SCRIPT_Q = "select upper(trigger_name) from information_schema.triggers where event_object_schema = %(SCHEMA)s group by 1"
O_PRO_SCRIPT_Q = "SELECT OBJECT_NAME FROM ALL_OBJECTS WHERE OBJECT_TYPE IN ('FUNCTION','PROCEDURE') AND OWNER = :SCHEMA"
P_PRO_SCRIPT_Q = '''SELECT UPPER(p.proname) AS function_name FROM pg_proc p JOIN   pg_namespace n ON n.oid = p.pronamespace WHERE  NOT 
        p.proisagg AND
        n.nspname <> 'information_schema' AND n.nspname = %(SCHEMA)s'''
O_UNI_KEY_SCRIPT_Q = '''SELECT c.column_name 
FROM sys.all_indexes i,
     sys.all_ind_columns c
WHERE i.table_name  = '{TAB}'
  AND i.owner       = '{SCH}'
  AND i.uniqueness  = 'UNIQUE'
  AND i.index_name  = c.index_name
  AND i.table_owner = c.table_owner
  AND i.table_name  = c.table_name
  AND i.owner       = c.index_owner'''
O_PRIM_KEY_SCRIPT_Q = '''SELECT cols.column_name
                                FROM all_constraints cons, all_cons_columns cols
                                WHERE cons.constraint_type = 'P'
                                  AND cons.constraint_name = cols.constraint_name
                                  AND cons.owner = cols.owner
                                  AND cols.table_name = ''{TAB}'''''
P_PRIM_KEY_SCRIPT_Q = '''select kcu.column_name 
                                from information_schema.table_constraints tco
                                         join information_schema.key_column_usage kcu
                                              on kcu.constraint_name = tco.constraint_name
                                                  and kcu.constraint_schema = tco.constraint_schema
                                                  and kcu.constraint_name = tco.constraint_name
                                where tco.constraint_type = 'PRIMARY KEY'
                                and kcu.table_name =  %(TABLE)s'''
O_TABLE_EXISTS = '''select count(*)
                                    from all_objects
                                    where object_type in ('TABLE','VIEW')
                                    and object_name = :TABLE'''
P_TABLE_EXISTS = '''SELECT count(*) FROM information_schema.tables
                                   WHERE  table_schema = %(SCHEMA)s
                                   AND    table_name   = %(TABLE)s'''
O_COLUMN_NAMES = '''select col.table_name, col.column_name, col.data_type
                                from sys.all_tab_columns col
                                         inner join sys.all_tables t on col.owner = t.owner
                                    and col.table_name = t.table_name
                                where col.owner = :SCH'''
P_COLUMN_NAMES = '''SELECT UPPER(table_name), UPPER(column_name), UPPER(data_type) FROM information_schema.columns WHERE table_schema = %(SCH)s'''
O_ROW_COUNT = '''SELECT table_name,num_rows FROM all_tables WHERE owner = :SCH'''
P_ROW_COUNT = '''select UPPER(table_name), 
       (xpath('/row/cnt/text()', xml_count))[1]::text::bigint as row_count
from (
  select table_name, table_schema, 
         query_to_xml(format('select count(*) as cnt from %I.%I', table_schema, table_name), false, true, '') as xml_count
  from information_schema.tables
  where table_schema = $SCHEMA ) t'''
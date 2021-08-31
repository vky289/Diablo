import logging
from builtins import RuntimeError

from django_rq import job
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import DBCompareDBResults, DBCompare
from time import sleep

logger = logging.getLogger(__name__)

channels_layer = get_channel_layer()


@job('default')
def get_compare_sync(compare_ids, __func_name):
    if compare_ids is None:
        return
    try:
        obj = DBCompareDBResults.objects.get(compare_dbs__id=compare_ids, func_call=__func_name)
        while obj.status != 1:
            try:
                obj = DBCompareDBResults.objects.get(compare_dbs__id=compare_ids, func_call=__func_name)
                sleep(5)
            except DBCompareDBResults.DoesNotExist:
                logger.info("Can't find the results for the combination of compare_id = " + str(compare_ids) + " and function name " + str(__func_name))
                async_to_sync(channels_layer.group_send)('job_ticks', {
                    'type': 'send_job_results', 'text': 'failure'
                })
        logger.info("results found for the combination of compare_id = " + str(compare_ids) + " and function name " + str(__func_name))
        async_to_sync(channels_layer.group_send)('job_ticks', {
            'type': 'send_job_results', 'text': 'success'
            }
        )
    except DBCompareDBResults.DoesNotExist:
        logger.info("Can't find the results for the combination of compare_id = " + str(compare_ids) + " and function name " + str(__func_name))
        async_to_sync(channels_layer.group_send)('job_ticks', {
            'type': 'send_job_results', 'text': 'failure'
        })

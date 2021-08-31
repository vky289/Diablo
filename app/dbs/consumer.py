from channels.generic.websocket import AsyncWebsocketConsumer
from .tasks import get_compare_sync
import json
from urllib.parse import parse_qs

class JobUpdateConsumer(AsyncWebsocketConsumer):
    async def websocket_connect(self, message):
        await self.channel_layer.group_add('job_ticks', self.channel_name)
        await self.accept()
        qs = self.scope.get('query_string').decode()
        if qs:
            qss = parse_qs(qs)
            if qss.get('compare_ids') is not None and qss.get('func_name') is not None:
                get_compare_sync.delay(qss['compare_ids'][0], qss['func_name'][0])
            # else:
            #     setattr("compare_ids or func_name is missing", True)


    async def websocket_disconnect(self, message):
        await self.channel_layer.group_discard('job_ticks', self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        message = json.loads(text_data)
        get_compare_sync.delay(message['compare_ids'], message['func_name'])

    async def send_job_results(self, event):
        text_message = event['text']
        await self.send(text_data=text_message)
        await self.close()

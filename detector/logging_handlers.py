import asyncio
import logging
from django.utils.timezone import now
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer

CATEGORY_MAP = {
    'django': 'SYSTEM',
    'security': 'SECURITY',
    'auth': 'USER',
    'activity': 'ACTIVITY',
    'notify': 'NOTIFY',
    'device': 'DEVICE',
}

class DatabaseLogHandler(logging.Handler):
    def emit(self, record):
        try:
            from detector.models import Log

            if record.name.startswith('django.channels.server'):
                return

            # print(f"Log emitted: name={record.name}, message={record.getMessage()}")


            category = CATEGORY_MAP.get(record.name.split('.')[0], 'SYSTEM')

            # Create log entry sync-ORM call wrapped with sync_to_async, run sync via async_to_sync
            # This is sync code, so call sync ORM with async_to_sync

            # First check if inside async loop
            try:
                loop = asyncio.get_running_loop()
                in_async = True
            except RuntimeError:
                in_async = False

            if in_async:
                # We are in async context — need to schedule async calls via create_task
                asyncio.create_task(self._async_emit(record, category))
            else:
                # Normal sync context — safe to call async_to_sync
                log = async_to_sync(sync_to_async(Log.objects.create, thread_sensitive=True))(
                    timestamp=now(),
                    level=record.levelname,
                    category=category,
                    message=record.getMessage(),
                    source=record.name
                )

                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    "logs_group",
                    {
                        "type": "send_new_log",
                        "log": {
                            "timestamp": log.timestamp.isoformat(),
                            "level": log.level,
                            "category": log.category,
                            "message": log.message,
                            "source": log.source,
                        },
                    }
                )

        except Exception as e:
            print(f"Logging to DB failed: {e}")

    async def _async_emit(self, record, category):
        from detector.models import Log
        from channels.layers import get_channel_layer

        log = await sync_to_async(Log.objects.create, thread_sensitive=True)(
            timestamp=now(),
            level=record.levelname,
            category=category,
            message=record.getMessage(),
            source=record.name
        )

        channel_layer = get_channel_layer()
        await channel_layer.group_send(
            "logs_group",
            {
                "type": "send_new_log",
                "log": {
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level,
                    "category": log.category,
                    "message": log.message,
                    "source": log.source,
                },
            }
        )

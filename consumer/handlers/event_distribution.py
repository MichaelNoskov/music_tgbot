from typing import Any, Dict

from consumer.handlers.get_music import handle_event_music
from consumer.handlers.create_profile import handle_event_profile
from consumer.handlers.upload_music import handle_event_upload_music


async def handle_event_distribution(body: Dict[str, Any]) -> None:
    match body['action']:
        case 'get_music':
            await handle_event_music(body)
        case 'create_profile':
            await handle_event_profile(body)
        case 'upload_music':
            await handle_event_upload_music(body)

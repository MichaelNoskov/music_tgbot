from typing import Any, Dict

from consumer.handlers.get_music import handle_event_music
from consumer.handlers.create_profile import handle_event_profile
from consumer.handlers.upload_music import handle_event_upload_music
from consumer.handlers.get_favorite_music import handle_event_favorite_music
from consumer.handlers.likes import handle_event_like, handle_event_dislike


async def handle_event_distribution(body: Dict[str, Any]) -> None:
    match body['action']:
        case 'get_music':
            await handle_event_music(body)
            return
        case 'get_favorite_music':
            await handle_event_favorite_music(body)
            return
        case 'create_profile':
            await handle_event_profile(body)
            return
        case 'upload_music':
            await handle_event_upload_music(body)
            return
        case 'like':
            await handle_event_like(body)
            return
        case 'dislike':
            await handle_event_dislike(body)
            return

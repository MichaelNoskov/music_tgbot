from typing import Any, Dict

from consumer.handlers.get_music import handle_event_music


async def handle_event_distribution(body: Dict[str, Any]) -> None:
    match body['action']:
        case 'get_music':
            await handle_event_music(body)

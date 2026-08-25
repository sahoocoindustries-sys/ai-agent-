"""
RUDRA Event and Message Bus Subsystem (MB - BRIDGE).
"""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List


@dataclass
class Message:
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = "GENERIC_EVENT"
    source_subsystem: str = "UNKNOWN"
    target_subsystem: str = "BROADCAST"
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


MessageHandler = Callable[[Message], None]


class EventBus:
    def __init__(self):
        self._subscribers: Dict[str, List[MessageHandler]] = {}
        self._history: List[Message] = []

    def subscribe(self, event_type: str, handler: MessageHandler) -> None:
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: MessageHandler) -> None:
        if event_type in self._subscribers and handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    def publish(self, message: Message) -> None:
        self._history.append(message)
        # Call specific event subscribers
        if message.event_type in self._subscribers:
            for handler in self._subscribers[message.event_type]:
                handler(message)
        # Call wildcard subscribers
        if "*" in self._subscribers:
            for handler in self._subscribers["*"]:
                handler(message)

    def get_history(self, event_type: str = None) -> List[Message]:
        if event_type:
            return [msg for msg in self._history if msg.event_type == event_type]
        return list(self._history)

from typing import Callable, Coroutine, Dict, List, Tuple


class ConsumerRouter:
    def __init__(self):
        self._handlers: List[Tuple[Dict, Callable[..., Coroutine]]] = []

    def get(self, config: Dict):
        def decorator(func: Callable[..., Coroutine]):
            self._handlers.append((config, func))
            return func

        return decorator

    def register_handlers(self, consumer):
        for config, func in self._handlers:
            consumer.get(config)(func)

    def include_router(self, router: "ConsumerRouter"):
        self._handlers.extend(router._handlers)

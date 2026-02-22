import threading
import time
from collections import defaultdict


class RateLimiter:
    def __init__(self, max_requests: int, window_sec: int) -> None:
        self.max_requests = max_requests
        self.window_sec = window_sec
        self._counts: dict[str, list[float]] = defaultdict(list)
        self._lock = threading.Lock()

    def check(self, key: str) -> tuple[bool, int, int]:
        """Returns (allowed, remaining, retry_after_sec)."""
        with self._lock:
            now = time.time()
            cutoff = now - self.window_sec
            self._counts[key] = [t for t in self._counts[key] if t > cutoff]
            if len(self._counts[key]) >= self.max_requests:
                oldest = min(self._counts[key])
                retry_after = max(0, int(self.window_sec - (now - oldest)))
                return False, 0, retry_after
            self._counts[key].append(now)
            remaining = self.max_requests - len(self._counts[key])
            return True, remaining, 0

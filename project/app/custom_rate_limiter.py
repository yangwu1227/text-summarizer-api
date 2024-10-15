from fastapi_limiter.depends import RateLimiter


class CustomRateLimiter(RateLimiter):
    """
    A custom implementation of RateLimiter with hashability and equality
    to support FastAPI's dependency overrides mechanism.

    This class ensures that instances are comparable and hashable, which allows
    FastAPI to correctly override the dependency in tests.
    """

    def __init__(self, times: int, seconds: int) -> None:
        """
        Initialize a new CustomRateLimiter instance with the specified rate limiting settings.

        Parameters
        ----------
        times : int
            The number of requests allowed within the specified time window.
        seconds : int
            The time window in seconds within which the specified number of requests are allowed.
        """
        super().__init__(times=times, seconds=seconds)
        self.times = times
        self.seconds = seconds

    def __hash__(self) -> int:
        """
        Generate a unique hash value based on a string representation of the rate limiting settings.
        This allows instances of this class to be used as keys in dictionaries so FastAPI's dependency
        overrides mechanism can correctly override the dependency in tests.
        """
        return hash(f"limiter-{self.times}-{self.seconds}")

    def __eq__(self, other: object) -> bool:
        """
        Compare two CustomRateLimiter instances based on their `times` and `seconds` values.
        This ensures that two instances with the same rate limiting settings are considered equal.
        """
        if isinstance(other, CustomRateLimiter):
            return self.times == other.times and self.seconds == other.seconds
        return False

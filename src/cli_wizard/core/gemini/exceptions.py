
class NoClientError(Exception):
    """
    An error raised when a Gemini client is not configured.
    """
    pass


class InvalidModelError(Exception):
    """
    An error raised when an invalid Gemini model is specified.
    """
    pass

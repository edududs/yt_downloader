"""Domain errors. The application layer only ever catches DomainError."""


class DomainError(Exception):
    """Base class for every error the application layer knows about."""


class InvalidUrlError(DomainError):
    """URL is not a YouTube video or playlist URL."""


class InvalidBitrateError(DomainError):
    """Bitrate string is not of the form '<digits>k'."""


class InvalidConcurrencyError(DomainError):
    """Concurrency must be at least 1."""


class EmptyPlaylistError(DomainError):
    """Playlist resolved but contains no videos."""


class StreamUnavailableError(DomainError):
    """Provider found the video but no stream matches the request."""


class ConversionFailedError(DomainError):
    """Audio conversion failed; the original file is left on disk."""


class ProviderError(DomainError):
    """Vendor failure translated at the adapter boundary."""

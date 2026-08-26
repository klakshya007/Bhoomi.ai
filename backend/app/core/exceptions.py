class IntegrationError(Exception):
    """Base exception for all external provider integrations."""
    def __init__(self, message: str, provider: str = "unknown"):
        self.provider = provider
        self.message = f"[{provider}] {message}"
        super().__init__(self.message)

class ProviderTimeoutError(IntegrationError):
    """Raised when a provider times out."""
    pass

class ProviderRateLimitError(IntegrationError):
    """Raised when a provider rate limit is exceeded."""
    pass

class ProviderDataFormatError(IntegrationError):
    """Raised when the provider returns unexpected data."""
    pass

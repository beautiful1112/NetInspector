'''Customized exception classes '''


class NetworkAutomationError(Exception):
    """Base exception class for network automation"""

    def __init__(self, message: str = "", details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self):
        if self.details:
            return f"{self.message} - Additional details: {self.details}"
        return self.message


class ConnectionError(NetworkAutomationError):
    """Exception raised for connection errors.

    Attributes:
        message -- explanation of the connection error
        details -- additional error details like host, port, error code etc.
    """

    def __init__(self, message: str = "Failed to establish connection", details: dict = None):
        super().__init__(message, details)


class AuthenticationError(NetworkAutomationError):
    """Exception raised for authentication failures.

    Attributes:
        message -- explanation of the authentication error
        details -- additional error details like username, host, etc.
    """

    def __init__(self, message: str = "Authentication failed", details: dict = None):
        super().__init__(message, details)


class CommandError(NetworkAutomationError):
    """Exception raised for command execution errors.

    Attributes:
        message -- explanation of the command error
        details -- additional error details like command string, output, error code etc.
    """

    def __init__(self, message: str = "Command execution failed", details: dict = None):
        super().__init__(message, details)


class ConfigError(NetworkAutomationError):
    """Exception raised for configuration errors.

    Attributes:
        message -- explanation of the configuration error
        details -- additional error details like config commands, error output etc.
    """

    def __init__(self, message: str = "Configuration operation failed", details: dict = None):
        super().__init__(message, details)


class TimeoutError(NetworkAutomationError):
    """Exception raised for timeout errors.

    Attributes:
        message -- explanation of the timeout error
        details -- additional error details like timeout duration, operation type etc.
    """

    def __init__(self, message: str = "Operation timed out", details: dict = None):
        super().__init__(message, details)


class ValidationError(NetworkAutomationError):
    """Exception raised for validation errors.

    Attributes:
        message -- explanation of the validation error
        details -- additional error details like invalid fields, expected values etc.
    """

    def __init__(self, message: str = "Validation failed", details: dict = None):
        super().__init__(message, details)
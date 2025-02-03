"""Definition of custom exceptions"""


class MagpylibBadUserInput(Exception):
    """bad user input"""


class MagpylibInternalError(Exception):
    """should never have reached this position in the code"""


class MagpylibBadInputShape(Exception):
    """catching bad input shapes"""


class MagpylibMissingInput(Exception):
    """catching missing user inputs"""


class MagpylibDeprecationWarning(Warning):
    """Non-suppressed Deprecation Warning."""

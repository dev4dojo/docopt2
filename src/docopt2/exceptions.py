class DocoptError(Exception):
    """Base class for all docopt-next errors."""


class DocoptLanguageError(DocoptError):
    """Raised when the 'Usage' string itself is syntactically invalid."""


class DocoptUserError(DocoptError):
    """
    Raised when user-provided CLI arguments don't match the spec.
    Usually caught to print the help message.
    """

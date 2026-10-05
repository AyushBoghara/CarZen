# ==========================================
# CUSTOM AUTH EXCEPTIONS
# ==========================================

class AuthError(Exception):
    """Base exception class for all authentication operations."""
    pass


# --- Registration Exceptions ---

class UserAlreadyExistsError(AuthError):
    """Raised when a username or email is already registered."""
    pass

class WeakPasswordError(AuthError):
    """Raised when a password fails complexity rules."""
    pass

class InvalidEmailError(AuthError):
    """Raised when an email address format is malformed."""
    pass

class UserNameAlreadyExistsError(AuthError):
    """Raised when an email address format is malformed."""
    pass


# --- Login Exceptions ---

class UserNotFoundError(AuthError):
    """Raised when an identifier does not match any account."""
    pass

class InvalidCredentialsError(AuthError):
    """Raised when a password does not match the record."""
    pass

class AccountLockedError(AuthError):
    """Raised when an account is disabled or locked due to failed attempts."""
    pass

class UnverifiedAccountError(AuthError):
    """Raised when a user logs in but has not verified their email."""
    pass


# --- Forgot / Reset Password Exceptions ---

class PasswordResetExpiredError(AuthError):
    """Raised when a password reset token has timed out."""
    pass

class InvalidResetTokenError(AuthError):
    """Raised when a password reset token is corrupted or invalid."""
    pass

class SameAsOldPasswordError(AuthError):
    """Raised when a new password matches the previous password."""
    pass

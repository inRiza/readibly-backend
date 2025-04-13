from .auth.router import router as auth_router
from .speech_to_text import router as speech_router

__all__ = ["auth_router", "speech_router"] 
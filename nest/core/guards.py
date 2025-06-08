from fastapi import Request, HTTPException, status
import inspect


class BaseGuard:
    """Base class for creating route guards."""

    def can_activate(self, request: Request) -> bool:
        """Override this method with your authorization logic."""
        raise NotImplementedError

    async def __call__(self, request: Request):
        result = self.can_activate(request)
        if inspect.isawaitable(result):
            result = await result
        if not result:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")



def UseGuards(*guards):
    """Decorator to attach guards to a controller or route."""

    def decorator(obj):
        existing = list(getattr(obj, "__guards__", []))
        existing.extend(guards)
        setattr(obj, "__guards__", existing)
        return obj

    return decorator

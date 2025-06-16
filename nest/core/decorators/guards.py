from fastapi import Request, HTTPException, status, Security, Depends
from fastapi.security.base import SecurityBase
from typing import Optional
import inspect


class BaseGuard:
    """Base class for creating route guards in PyNest.
    
    Guards provide a way to implement authentication and authorization logic
    that can be applied to controllers or individual routes. They are fully
    compatible with FastAPI's security system and OpenAPI documentation.
    
    **Security Scheme Integration:**
    
    If ``security_scheme`` is set to an instance of ``fastapi.security.SecurityBase``,
    the guard will:
    - Be injected with credentials from that security scheme
    - Appear in the generated OpenAPI schema with appropriate security requirements
    - Show an "Authorize" button in Swagger UI
    - Allow users to authenticate through the interactive documentation
    
    **Supported Security Schemes:**
    
    PyNest guards support all FastAPI security schemes:
    
    * **API Keys** (``fastapi.security.APIKeyHeader``, ``APIKeyQuery``, ``APIKeyCookie``)
    * **HTTP Authentication** (``HTTPBasic``, ``HTTPBearer``, ``HTTPDigest``)
    * **OAuth2** (``OAuth2PasswordBearer``, ``OAuth2AuthorizationCodeBearer``)
    * **OpenID Connect** (``OpenIdConnect``)
    
    **Examples:**
    
    **1. Simple Guard (No Security Scheme):**
    
    ```python
    class SimpleGuard(BaseGuard):
        def can_activate(self, request: Request, credentials=None) -> bool:
            # Custom logic without OpenAPI documentation
            return request.headers.get("X-Custom-Header") == "allowed"
    ```
    
    **2. API Key Header Guard:**
    
    ```python
    from fastapi.security import APIKeyHeader
    
    class APIKeyGuard(BaseGuard):
        security_scheme = APIKeyHeader(
            name="X-API-Key", 
            description="API Key for authentication"
        )
        
        def can_activate(self, request: Request, credentials=None) -> bool:
            # credentials contains the API key value
            return credentials == "your-secret-api-key"
    ```
    
    **3. Bearer Token Guard:**
    
    ```python
    from fastapi.security import HTTPBearer
    
    class BearerTokenGuard(BaseGuard):
        security_scheme = HTTPBearer(description="Bearer token")
        
        def can_activate(self, request: Request, credentials=None) -> bool:
            # credentials is an HTTPAuthorizationCredentials object
            if credentials and credentials.scheme == "Bearer":
                return self.validate_jwt_token(credentials.credentials)
            return False
            
        def validate_jwt_token(self, token: str) -> bool:
            # Implement JWT validation logic
            return token == "valid-jwt-token"
    ```
    
    **4. Basic Authentication Guard:**
    
    ```python
    from fastapi.security import HTTPBasic
    
    class BasicAuthGuard(BaseGuard):
        security_scheme = HTTPBasic(description="Basic HTTP authentication")
        
        def can_activate(self, request: Request, credentials=None) -> bool:
            # credentials is an HTTPBasicCredentials object
            if credentials:
                return (credentials.username == "admin" and 
                       credentials.password == "secret")
            return False
    ```
    
    **5. OAuth2 Password Bearer Guard:**
    
    ```python
    from fastapi.security import OAuth2PasswordBearer
    
    class OAuth2Guard(BaseGuard):
        security_scheme = OAuth2PasswordBearer(
            tokenUrl="token",
            description="OAuth2 with Password and Bearer"
        )
        
        def can_activate(self, request: Request, credentials=None) -> bool:
            # credentials contains the OAuth2 token
            return self.validate_oauth2_token(credentials)
            
        def validate_oauth2_token(self, token: str) -> bool:
            # Implement OAuth2 token validation
            return token and len(token) > 20
    ```
    
    **6. Multi-Scope OAuth2 Guard:**
    
    ```python
    from fastapi.security import OAuth2PasswordBearer
    
    class AdminGuard(BaseGuard):
        security_scheme = OAuth2PasswordBearer(
            tokenUrl="token",
            scopes={
                "read": "Read access", 
                "write": "Write access",
                "admin": "Admin access"
            }
        )
        
        def can_activate(self, request: Request, credentials=None) -> bool:
            # Validate token and check for admin scope
            return self.has_admin_scope(credentials)
    ```
    
    **7. Cookie Authentication Guard:**
    
    ```python
    from fastapi.security import APIKeyCookie
    
    class CookieGuard(BaseGuard):
        security_scheme = APIKeyCookie(
            name="session_id",
            description="Session cookie"
        )
        
        def can_activate(self, request: Request, credentials=None) -> bool:
            # credentials contains the cookie value
            return self.validate_session(credentials)
    ```
    
    **8. Async Guard Example:**
    
    ```python
    class AsyncGuard(BaseGuard):
        security_scheme = APIKeyHeader(name="X-Token")
        
        async def can_activate(self, request: Request, credentials=None) -> bool:
            # Async validation (e.g., database lookup)
            user = await self.get_user_by_token(credentials)
            return user is not None
            
        async def get_user_by_token(self, token: str):
            # Async database call
            pass
    ```
    
    **Usage with Controllers:**
    
    ```python
    @Controller("users")
    @UseGuards(APIKeyGuard, AdminGuard)  # Multiple guards
    class UserController:
        pass
        
    @Controller("public")
    class PublicController:
        
        @Get("/protected")
        @UseGuards(BearerTokenGuard)  # Route-level guard
        def protected_route(self):
            return {"message": "This is protected"}
    ```
    
    **Error Handling:**
    
    Guards automatically raise ``HTTPException`` with status 403 (Forbidden)
    when ``can_activate`` returns ``False``. You can customize error handling
    by overriding the ``__call__`` method.
    
    **OpenAPI Documentation:**
    
    When using security schemes, guards automatically:
    - Add security requirements to OpenAPI schema
    - Display "Authorize" button in Swagger UI
    - Show required headers/parameters in API documentation
    - Enable interactive authentication testing
    """

    security_scheme: Optional[SecurityBase] = None

    def can_activate(self, request: Request, credentials=None) -> bool:
        """Determine if the request should be allowed to proceed.
        
        **Override this method** with your custom authorization logic.
        
        Args:
            request: The FastAPI Request object containing request information
            credentials: Credentials extracted from the security scheme (if any).
                        Type depends on the security scheme used:
                        - APIKey schemes: str (the key value)
                        - HTTPBasic: HTTPBasicCredentials object
                        - HTTPBearer: HTTPAuthorizationCredentials object
                        - OAuth2: str (the token)
        
        Returns:
            bool: True if the request should be allowed, False to deny with 403
            
        Note:
            This method can be async. If it returns an awaitable, it will be
            automatically awaited by the guard system.
            
        Examples:
            ```python
            def can_activate(self, request: Request, credentials=None) -> bool:
                # Simple token check
                return credentials == "secret-token"
                
            async def can_activate(self, request: Request, credentials=None) -> bool:
                # Async validation
                user = await database.get_user_by_token(credentials)
                return user.is_active
            ```
        """
        raise NotImplementedError("Subclasses must implement can_activate method")

    async def __call__(self, request: Request, credentials=None):
        """Internal method that executes the guard logic.
        
        This method:
        1. Calls can_activate() with request and credentials
        2. Handles both sync and async can_activate implementations
        3. Raises HTTPException(403) if access is denied
        
        You typically don't need to override this method unless you want
        custom error handling or logging.
        """
        result = self.can_activate(request, credentials)
        if inspect.isawaitable(result):
            result = await result
        if not result:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Access denied: insufficient permissions"
            )

    @classmethod
    def as_dependency(cls):
        """Convert the guard class to a FastAPI dependency function.
        
        This method is used internally by PyNest to integrate guards with
        FastAPI's dependency system. It creates the appropriate dependency
        function based on whether a security scheme is configured.
        
        Returns:
            Callable: A dependency function that FastAPI can use
            
        **Internal Implementation Details:**
        
        - If no security_scheme: Creates a simple dependency that validates the request
        - If security_scheme exists: Creates a dependency with Security parameter for OpenAPI
          
        The returned dependency will:
        - Appear in OpenAPI schema (if security_scheme is set)  
        - Extract credentials automatically (if security_scheme is set)
        - Execute guard logic and raise 403 on failure
        """
        if cls.security_scheme is None:
            # No security scheme - simple request validation
            async def dependency(request: Request):
                guard = cls()
                await guard(request)

            return Depends(dependency)

        # Security scheme configured - create function with Security parameter
        # This allows FastAPI to detect the security requirement for OpenAPI
        security_scheme = cls.security_scheme

        async def security_dependency(
            request: Request,
            credentials=Security(security_scheme)
        ):
            guard = cls()
            await guard(request, credentials)

        return Depends(security_dependency)


def UseGuards(*guards):
    """Decorator to apply guards to controllers or individual routes.
    
    Guards provide authentication and authorization for your API endpoints.
    This decorator can be applied at the controller level (protecting all routes)
    or at individual route methods.
    
    Args:
        *guards: One or more guard classes (not instances) to apply
        
    **Usage Examples:**
    
    **Controller-level protection:**
    ```python
    @Controller("admin")
    @UseGuards(AdminGuard, RateLimitGuard)
    class AdminController:
        # All routes in this controller are protected
        pass
    ```
    
    **Route-level protection:**
    ```python
    @Controller("users")
    class UserController:
        
        @Get("/public")
        def public_endpoint(self):
            return {"message": "No auth required"}
            
        @Get("/private")
        @UseGuards(AuthGuard)
        def private_endpoint(self):
            return {"message": "Auth required"}
            
        @Post("/admin-only")
        @UseGuards(AuthGuard, AdminGuard)  # Multiple guards
        def admin_endpoint(self):
            return {"message": "Admin access required"}
    ```
    
    **Guard Execution Order:**
    
    Guards are executed in the order they are specified. If any guard fails,
    subsequent guards are not executed and a 403 error is returned.
    
    **Combining with FastAPI Dependencies:**
    
    Guards work alongside FastAPI's native dependency system and can be
    combined with other dependencies:
    
    ```python
    @Get("/users/{user_id}")
    @UseGuards(AuthGuard)
    def get_user(user_id: int, db: Session = Depends(get_db)):
        # Both guard and dependency are executed
        pass
    ```
    
    **Security in OpenAPI:**
    
    When guards use security schemes, they automatically appear in:
    - OpenAPI/Swagger documentation
    - Interactive API testing interface
    - Generated client code
    
    Returns:
        Callable: Decorator function that applies guards to the target
    """
    def decorator(obj):
        # Get existing guards (if any) and append new ones
        existing_guards = list(getattr(obj, "__guards__", []))
        existing_guards.extend(guards)
        setattr(obj, "__guards__", existing_guards)
        return obj

    return decorator

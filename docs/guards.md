# Guards and Authentication

PyNest supports route guards similar to NestJS, providing a powerful way to implement authentication and authorization logic. Guards are fully compatible with FastAPI's security system and automatically integrate with OpenAPI documentation.

## Overview

Guards are classes that implement custom authorization logic and can be applied to controllers or individual routes using the `@UseGuards` decorator. When a guard defines a FastAPI security scheme via the `security_scheme` attribute, the generated OpenAPI schema will mark the route as protected and the interactive docs will show an "Authorize" button.

## Basic Guard Example

```python
from fastapi import Request
from nest.core import Controller, Get, UseGuards, BaseGuard

class AuthGuard(BaseGuard):
    def can_activate(self, request: Request, credentials=None) -> bool:
        token = request.headers.get("X-Token")
        return token == "secret"

@Controller("/items")
@UseGuards(AuthGuard)
class ItemsController:
    @Get("/")
    def list_items(self):
        return ["a", "b"]
```

When the guard returns `False`, a `403 Forbidden` response is sent automatically.

## FastAPI Security Integration

PyNest guards support all FastAPI security schemes and automatically appear in OpenAPI documentation:

### API Key Authentication

#### API Key in Header (Most Common)

```python
from fastapi.security import APIKeyHeader

class APIKeyGuard(BaseGuard):
    security_scheme = APIKeyHeader(
        name="X-API-Key", 
        description="API key required for authentication"
    )
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        # credentials contains the API key value
        valid_keys = {"admin-key-123", "user-key-456"}
        return credentials in valid_keys
```

#### API Key in Query Parameter

```python
from fastapi.security import APIKeyQuery

class APIKeyQueryGuard(BaseGuard):
    security_scheme = APIKeyQuery(
        name="api_key",
        description="API key as query parameter (?api_key=your-key)"
    )
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        return credentials == "secret-query-key"
```

#### API Key in Cookie

```python
from fastapi.security import APIKeyCookie

class SessionGuard(BaseGuard):
    security_scheme = APIKeyCookie(
        name="session_token",
        description="Session token stored in cookie"
    )
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        valid_sessions = {"sess_abc123", "sess_def456"}
        return credentials in valid_sessions
```

### HTTP Authentication

#### Basic Authentication

```python
from fastapi.security import HTTPBasic
from fastapi.security.http import HTTPBasicCredentials

class BasicAuthGuard(BaseGuard):
    security_scheme = HTTPBasic(
        description="Username and password authentication"
    )
    
    def can_activate(self, request: Request, credentials: HTTPBasicCredentials = None) -> bool:
        if not credentials:
            return False
        
        # In production, use hashed passwords
        users = {"admin": "admin123", "user": "user456"}
        expected_password = users.get(credentials.username)
        return expected_password == credentials.password
```

#### Bearer Token Authentication

```python
from fastapi.security import HTTPBearer
from fastapi.security.http import HTTPAuthorizationCredentials

class BearerTokenGuard(BaseGuard):
    security_scheme = HTTPBearer(description="Bearer token authentication")
    
    def can_activate(self, request: Request, credentials: HTTPAuthorizationCredentials = None) -> bool:
        if not credentials or credentials.scheme != "Bearer":
            return False
        
        token = credentials.credentials
        return self.validate_jwt_token(token)
    
    def validate_jwt_token(self, token: str) -> bool:
        # Implement proper JWT validation
        return token.startswith("eyJ") and len(token) > 20
```

## JWT Authentication Example

Complete JWT implementation using third-party libraries:

```python
import jwt
from fastapi import Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from nest.core import BaseGuard

class JWTGuard(BaseGuard):
    security_scheme = HTTPBearer(description="JWT Bearer token")

    def can_activate(
        self, request: Request, credentials: HTTPAuthorizationCredentials = None
    ) -> bool:
        if not credentials:
            return False
            
        try:
            payload = jwt.decode(
                credentials.credentials, "your-secret", algorithms=["HS256"]
            )
            # Attach user info to request for use in controllers
            request.state.user = payload.get("sub")
            return True
        except jwt.PyJWTError:
            return False
```

Attach the guard with `@UseGuards(JWTGuard)` on controllers or routes to secure them. Because `JWTGuard` specifies a `security_scheme`, the route will display a lock icon in the docs and allow entering a token.

## OAuth2 Authentication

### Basic OAuth2 Password Bearer

```python
from fastapi.security import OAuth2PasswordBearer

class OAuth2Guard(BaseGuard):
    security_scheme = OAuth2PasswordBearer(
        tokenUrl="auth/token",
        description="OAuth2 password bearer token"
    )
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        if not credentials:
            return False
        # Validate OAuth2 token with your auth server
        return self.validate_oauth2_token(credentials)
    
    def validate_oauth2_token(self, token: str) -> bool:
        # Implement OAuth2 token validation
        valid_tokens = {"oauth2_token_123", "oauth2_token_456"}
        return token in valid_tokens
```

### OAuth2 with Scopes (Fine-grained Permissions)

```python
class OAuth2ScopesGuard(BaseGuard):
    security_scheme = OAuth2PasswordBearer(
        tokenUrl="auth/token",
        scopes={
            "read": "Read access to resources",
            "write": "Write access to resources",
            "admin": "Full administrative access"
        }
    )
    
    def __init__(self, required_scopes: list = None):
        self.required_scopes = required_scopes or []
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        if not credentials:
            return False
        
        user_scopes = self.get_token_scopes(credentials)
        return all(scope in user_scopes for scope in self.required_scopes)
    
    def get_token_scopes(self, token: str) -> list:
        # Extract scopes from token
        token_scopes = {
            "admin_token": ["read", "write", "admin"],
            "user_token": ["read", "write"],
            "readonly_token": ["read"]
        }
        return token_scopes.get(token, [])

# Usage with specific scopes
@Controller("admin")
@UseGuards(OAuth2ScopesGuard(["admin"]))
class AdminController:
    @Get("/users")
    def list_users(self):
        return {"users": ["user1", "user2"]}
```

## Controller vs. Route Guards

You can attach guards at the controller level so they apply to every route in the controller. Individual routes can also specify their own guards.

```python
@Controller('/admin')
@UseGuards(AdminGuard)
class AdminController:
    @Get('/dashboard')
    def dashboard(self):
        return {'ok': True}

    @Post('/login')
    @UseGuards(PublicOnlyGuard)  # Overrides controller guard
    def login(self):
        return {'logged_in': True}
```

In this example `AdminGuard` protects all routes while `PublicOnlyGuard` is applied only to the `login` route.

## Combining Multiple Guards

`UseGuards` accepts any number of guard classes. All specified guards must return `True` in order for the request to proceed.

```python
class TokenGuard(BaseGuard):
    security_scheme = APIKeyHeader(name="X-Token")
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        return credentials == "secret"

class RoleGuard(BaseGuard):
    security_scheme = HTTPBearer(description="JWT with role info")
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        # Extract role from JWT token
        user_role = self.get_user_role(credentials.credentials)
        return user_role == "admin"

@Controller('/secure')
class SecureController:
    @Get('/')
    @UseGuards(TokenGuard, RoleGuard)  # Both guards must pass
    def root(self):
        return {'ok': True}
```

## Role-Based Access Control

```python
class RoleBasedGuard(BaseGuard):
    security_scheme = HTTPBearer(description="JWT token with role information")
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        if not credentials:
            return False
        
        user_roles = self.get_user_roles(credentials.credentials)
        return any(role in user_roles for role in self.allowed_roles)
    
    def get_user_roles(self, token: str) -> list:
        # Extract roles from JWT or database
        role_mapping = {
            "admin_token": ["admin", "user"],
            "user_token": ["user"],
            "guest_token": ["guest"]
        }
        return role_mapping.get(token, [])

# Usage
@Controller("api/users")
class UserController:
    @Get("/")
    @UseGuards(RoleBasedGuard(["user", "admin"]))
    def list_users(self):
        return {"users": []}
    
    @Delete("/{user_id}")
    @UseGuards(RoleBasedGuard(["admin"]))  # Admin only
    def delete_user(self, user_id: int):
        return {"deleted": user_id}
```

## Asynchronous Guards

Guards can perform asynchronous checks by making `can_activate` async or returning an awaitable:

```python
class AsyncGuard(BaseGuard):
    security_scheme = APIKeyHeader(name="X-Auth-Token")
    
    async def can_activate(self, request: Request, credentials=None) -> bool:
        if not credentials:
            return False
        
        # Async database lookup
        user = await self.get_user_from_db(credentials)
        return user is not None and user.get("is_active", False)
    
    async def get_user_from_db(self, token: str):
        # Simulate async database call
        import asyncio
        await asyncio.sleep(0.1)
        
        users = {
            "valid_token_123": {"id": 1, "is_active": True},
            "expired_token_456": {"id": 2, "is_active": False}
        }
        return users.get(token)
```

PyNest automatically awaits the result.

## Custom Guards Without Security Schemes

Guards don't always need security schemes. They can implement custom logic like rate limiting:

```python
from datetime import datetime, timedelta

class RateLimitGuard(BaseGuard):
    # No security_scheme - won't appear in OpenAPI docs
    
    def __init__(self, max_requests: int = 100, window_minutes: int = 60):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.request_counts = {}
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        client_ip = request.client.host
        now = datetime.now()
        
        # Clean old entries
        cutoff = now - timedelta(minutes=self.window_minutes)
        
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        # Filter recent requests
        recent_requests = [
            t for t in self.request_counts[client_ip] 
            if t > cutoff
        ]
        
        if len(recent_requests) >= self.max_requests:
            return False
        
        recent_requests.append(now)
        self.request_counts[client_ip] = recent_requests
        return True

@Controller("api")
@UseGuards(APIKeyGuard, RateLimitGuard)  # API key + rate limiting
class APIController:
    @Get("/data")
    def get_data(self):
        return {"data": "protected and rate limited"}
```

## Multi-Method Authentication

Guards can accept multiple authentication methods:

```python
class MultiAuthGuard(BaseGuard):
    # Primary security scheme for OpenAPI docs
    security_scheme = HTTPBearer(description="Bearer token or API key")
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        # Method 1: Bearer token from security scheme
        if credentials and self.validate_bearer(credentials.credentials):
            return True
        
        # Method 2: API key in custom header
        api_key = request.headers.get("X-API-Key")
        if api_key and self.validate_api_key(api_key):
            return True
        
        # Method 3: Session cookie
        session = request.cookies.get("session_id") 
        if session and self.validate_session(session):
            return True
        
        return False
    
    def validate_bearer(self, token: str) -> bool:
        return token in ["jwt-token-1", "jwt-token-2"]
    
    def validate_api_key(self, key: str) -> bool:
        return key in ["api-key-1", "api-key-2"]
    
    def validate_session(self, session: str) -> bool:
        return session in ["session-1", "session-2"]
```

## Custom Error Handling

Override the `__call__` method for custom error responses:

```python
import inspect
from datetime import datetime

class CustomErrorGuard(BaseGuard):
    security_scheme = APIKeyHeader(name="X-Custom-Key")
    
    async def __call__(self, request: Request, credentials=None):
        try:
            result = self.can_activate(request, credentials)
            if inspect.isawaitable(result):
                result = await result
                
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error": "INVALID_API_KEY",
                        "message": "The provided API key is invalid or expired",
                        "code": "AUTH_001", 
                        "timestamp": datetime.now().isoformat()
                    },
                    headers={"WWW-Authenticate": "ApiKey"}
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "AUTHENTICATION_ERROR", "message": str(e)}
            )
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        return credentials == "valid-custom-key"
```

## OpenAPI Integration

When a guard sets the `security_scheme` attribute, the generated OpenAPI schema includes the corresponding security requirement. The docs page will show:

- 🔒 Lock icon next to protected routes
- "Authorize" button in the top right
- Input fields for tokens/credentials
- Security requirements in the route documentation

This works with any `fastapi.security` scheme:
- `APIKeyHeader`, `APIKeyQuery`, `APIKeyCookie`
- `HTTPBasic`, `HTTPBearer`, `HTTPDigest` 
- `OAuth2PasswordBearer`, `OAuth2AuthorizationCodeBearer`
- `OpenIdConnect`

## Testing Guards

Create mock guards for testing:

```python
class MockAuthGuard(BaseGuard):
    security_scheme = APIKeyHeader(name="X-Test-Key")
    
    def __init__(self, should_pass: bool = True):
        self.should_pass = should_pass
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        return self.should_pass

# In tests
@UseGuards(MockAuthGuard(should_pass=True))   # Allow access
@UseGuards(MockAuthGuard(should_pass=False))  # Deny access
```

## Complete Usage Examples

### Public API with Mixed Security

```python
@Controller("api/v1")
class APIController:
    @Get("/public")
    def public_endpoint(self):
        return {"message": "No authentication required"}
    
    @Get("/protected")
    @UseGuards(APIKeyGuard)
    def protected_endpoint(self):
        return {"message": "API key required"}
    
    @Get("/admin")
    @UseGuards(JWTGuard, RoleBasedGuard(["admin"]))
    def admin_endpoint(self):
        return {"message": "JWT + admin role required"}
```

### Enterprise Security Setup

```python
# Base authentication
@Controller("enterprise")
@UseGuards(OAuth2Guard, RateLimitGuard)
class EnterpriseController:
    
    @Get("/reports")
    @UseGuards(RoleBasedGuard(["analyst", "admin"]))
    def get_reports(self):
        return {"reports": []}
    
    @Post("/admin/system")
    @UseGuards(RoleBasedGuard(["admin"]), BasicAuthGuard)  # Double auth
    def admin_action(self):
        return {"message": "System action performed"}
```

## Best Practices

1. **Use Security Schemes**: Always define `security_scheme` for standard authentication methods to get OpenAPI documentation
2. **Layer Security**: Combine multiple guards for defense in depth
3. **Async for Database**: Use async guards when validating against databases
4. **Custom Errors**: Implement custom error handling for better UX
5. **Scope-Based Access**: Use OAuth2 scopes for fine-grained permissions
6. **Rate Limiting**: Combine auth guards with rate limiting guards
7. **Testing**: Create mock guards for unit testing
8. **Principle of Least Privilege**: Grant minimum required permissions

## Guard Types Summary

| Guard Type | Security Scheme | Use Case | OpenAPI |
|------------|----------------|----------|---------|
| API Key Header | `APIKeyHeader` | Service-to-service | ✅ |
| API Key Query | `APIKeyQuery` | Webhooks, simple APIs | ✅ |
| API Key Cookie | `APIKeyCookie` | Browser sessions | ✅ |
| Basic Auth | `HTTPBasic` | Simple username/password | ✅ |
| Bearer Token | `HTTPBearer` | JWT tokens | ✅ |
| OAuth2 Password | `OAuth2PasswordBearer` | OAuth2 flows | ✅ |
| OAuth2 Scopes | `OAuth2PasswordBearer` | Permission-based access | ✅ |
| Custom Logic | None | Rate limiting, custom rules | ❌ |
| Multi-Auth | Any | Flexible authentication | ✅ |

PyNest guards provide a powerful, flexible, and standards-compliant way to secure your APIs while maintaining excellent developer experience and automatic documentation generation.


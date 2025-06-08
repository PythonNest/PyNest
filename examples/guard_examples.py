"""
PyNest Guards Examples - Complete Security Implementation Guide

This file demonstrates various guard implementations using different FastAPI
security schemes, fully compatible with the FastAPI security system.

Based on FastAPI Security documentation:
https://fastapi.tiangolo.com/tutorial/security/
"""

from fastapi import Request, Depends, HTTPException, status
from fastapi.security import (
    APIKeyHeader, APIKeyQuery, APIKeyCookie,
    HTTPBasic, HTTPBearer, HTTPDigest,
    OAuth2PasswordBearer, OAuth2AuthorizationCodeBearer,
    OpenIdConnect
)
from fastapi.security.http import HTTPBasicCredentials, HTTPAuthorizationCredentials
from typing import Optional
import jwt
from datetime import datetime, timedelta

from nest.core import BaseGuard, UseGuards, Controller, Get, Post


# =============================================================================
# 1. API KEY GUARDS (Header, Query, Cookie)
# =============================================================================

class APIKeyHeaderGuard(BaseGuard):
    """API Key in HTTP Header - Most common API authentication method."""
    
    security_scheme = APIKeyHeader(
        name="X-API-Key",
        description="API key required for authentication"
    )
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        """Validate API key from header."""
        # credentials contains the X-API-Key header value
        valid_api_keys = {"admin-key-123", "user-key-456", "service-key-789"}
        return credentials in valid_api_keys


class APIKeyQueryGuard(BaseGuard):
    """API Key in URL query parameter."""
    
    security_scheme = APIKeyQuery(
        name="api_key",
        description="API key as query parameter (?api_key=your-key)"
    )
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        """Validate API key from query parameter."""
        return credentials == "secret-query-key"


class APIKeyCookieGuard(BaseGuard):
    """API Key in HTTP Cookie - Useful for browser-based applications."""
    
    security_scheme = APIKeyCookie(
        name="session_token",
        description="Session token stored in cookie"
    )
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        """Validate session token from cookie."""
        # In real application, validate against session store
        valid_sessions = {"sess_abc123", "sess_def456", "sess_ghi789"}
        return credentials in valid_sessions


# =============================================================================
# 2. HTTP AUTHENTICATION GUARDS
# =============================================================================

class HTTPBasicGuard(BaseGuard):
    """HTTP Basic Authentication (RFC 7617)."""
    
    security_scheme = HTTPBasic(
        description="Username and password using HTTP Basic authentication"
    )
    
    def can_activate(self, request: Request, credentials: HTTPBasicCredentials = None) -> bool:
        """Validate username and password."""
        if not credentials:
            return False
            
        # In production, hash passwords and use secure comparison
        users = {
            "admin": "admin123",
            "user": "user456",
            "guest": "guest789"
        }
        
        expected_password = users.get(credentials.username)
        return expected_password == credentials.password


class HTTPBearerGuard(BaseGuard):
    """HTTP Bearer Token Authentication - Common for JWT tokens."""
    
    security_scheme = HTTPBearer(
        description="Bearer token (typically JWT)"
    )
    
    def can_activate(self, request: Request, credentials: HTTPAuthorizationCredentials = None) -> bool:
        """Validate Bearer token."""
        if not credentials or credentials.scheme != "Bearer":
            return False
            
        token = credentials.credentials
        return self.validate_jwt_token(token)
    
    def validate_jwt_token(self, token: str) -> bool:
        """Validate JWT token (simplified example)."""
        try:
            # In production, use proper JWT validation with secret key
            if token.startswith("eyJ"):  # Simple JWT format check
                return len(token) > 20
            return False
        except Exception:
            return False


class CustomHTTPBearerGuard(BaseGuard):
    """Advanced Bearer token validation with user extraction."""
    
    security_scheme = HTTPBearer(
        description="JWT Bearer token with user context"
    )
    
    def can_activate(self, request: Request, credentials: HTTPAuthorizationCredentials = None) -> bool:
        """Validate token and attach user to request."""
        if not credentials or credentials.scheme != "Bearer":
            return False
        
        user = self.get_current_user(credentials.credentials)
        if user:
            # Attach user to request for use in controllers
            request.state.current_user = user
            return True
        return False
    
    def get_current_user(self, token: str) -> Optional[dict]:
        """Extract user information from JWT token."""
        try:
            # Simplified JWT decoding (use proper library in production)
            if token == "valid-jwt-token":
                return {
                    "id": 1,
                    "username": "john_doe",
                    "email": "john@example.com",
                    "roles": ["user"]
                }
            elif token == "admin-jwt-token":
                return {
                    "id": 2,
                    "username": "admin",
                    "email": "admin@example.com",
                    "roles": ["admin", "user"]
                }
            return None
        except Exception:
            return None


# =============================================================================
# 3. OAUTH2 GUARDS
# =============================================================================

class OAuth2PasswordBearerGuard(BaseGuard):
    """OAuth2 with Password flow - Most common OAuth2 implementation."""
    
    security_scheme = OAuth2PasswordBearer(
        tokenUrl="auth/token",
        description="OAuth2 password bearer token"
    )
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        """Validate OAuth2 token."""
        if not credentials:
            return False
            
        # Validate token (in production, verify with auth server)
        return self.validate_oauth2_token(credentials)
    
    def validate_oauth2_token(self, token: str) -> bool:
        """Validate OAuth2 access token."""
        # In production, validate with OAuth2 server or JWT validation
        valid_tokens = {
            "oauth2_access_token_123",
            "oauth2_access_token_456",
            "oauth2_access_token_789"
        }
        return token in valid_tokens


class OAuth2ScopesGuard(BaseGuard):
    """OAuth2 with scopes for fine-grained permissions."""
    
    security_scheme = OAuth2PasswordBearer(
        tokenUrl="auth/token",
        scopes={
            "read": "Read access to resources",
            "write": "Write access to resources", 
            "delete": "Delete access to resources",
            "admin": "Full administrative access"
        },
        description="OAuth2 with permission scopes"
    )
    
    def __init__(self, required_scopes: list = None):
        self.required_scopes = required_scopes or []
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        """Validate token and check required scopes."""
        if not credentials:
            return False
            
        user_scopes = self.get_token_scopes(credentials)
        return all(scope in user_scopes for scope in self.required_scopes)
    
    def get_token_scopes(self, token: str) -> list:
        """Extract scopes from OAuth2 token."""
        # In production, decode JWT or query OAuth2 server
        token_scopes = {
            "admin_token": ["read", "write", "delete", "admin"],
            "user_token": ["read", "write"],
            "readonly_token": ["read"]
        }
        return token_scopes.get(token, [])


# =============================================================================
# 4. CUSTOM AND COMPOSITE GUARDS
# =============================================================================

class RoleBasedGuard(BaseGuard):
    """Role-based access control guard."""
    
    security_scheme = HTTPBearer(description="JWT token with role information")
    
    def __init__(self, allowed_roles: list):
        self.allowed_roles = allowed_roles
    
    def can_activate(self, request: Request, credentials: HTTPAuthorizationCredentials = None) -> bool:
        """Check if user has required role."""
        if not credentials:
            return False
            
        user_roles = self.get_user_roles(credentials.credentials)
        return any(role in user_roles for role in self.allowed_roles)
    
    def get_user_roles(self, token: str) -> list:
        """Extract roles from JWT token."""
        # Simplified role extraction
        role_mapping = {
            "admin_token": ["admin", "user"],
            "user_token": ["user"],
            "guest_token": ["guest"]
        }
        return role_mapping.get(token, [])


class AsyncDatabaseGuard(BaseGuard):
    """Async guard that validates against database."""
    
    security_scheme = APIKeyHeader(name="X-Auth-Token")
    
    async def can_activate(self, request: Request, credentials=None) -> bool:
        """Async validation against database."""
        if not credentials:
            return False
            
        # Simulate async database call
        user = await self.get_user_by_token(credentials)
        return user is not None and user.get("is_active", False)
    
    async def get_user_by_token(self, token: str) -> Optional[dict]:
        """Simulate async database lookup."""
        # In production, use actual database query
        import asyncio
        await asyncio.sleep(0.1)  # Simulate DB delay
        
        users = {
            "db_token_123": {"id": 1, "username": "user1", "is_active": True},
            "db_token_456": {"id": 2, "username": "user2", "is_active": False},
            "db_token_789": {"id": 3, "username": "user3", "is_active": True}
        }
        return users.get(token)


class RateLimitGuard(BaseGuard):
    """Rate limiting guard (no security scheme - internal logic only)."""
    
    # No security_scheme - this guard doesn't appear in OpenAPI
    
    def __init__(self, max_requests: int = 100, window_minutes: int = 60):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.request_counts = {}
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        """Check rate limit for client IP."""
        client_ip = request.client.host
        now = datetime.now()
        
        # Clean old entries
        cutoff = now - timedelta(minutes=self.window_minutes)
        self.request_counts = {
            ip: times for ip, times in self.request_counts.items()
            if any(t > cutoff for t in times)
        }
        
        # Check current IP
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = []
        
        # Filter recent requests
        recent_requests = [
            t for t in self.request_counts[client_ip] 
            if t > cutoff
        ]
        
        if len(recent_requests) >= self.max_requests:
            return False
        
        # Add current request
        recent_requests.append(now)
        self.request_counts[client_ip] = recent_requests
        return True


# =============================================================================
# 5. USAGE EXAMPLES WITH CONTROLLERS
# =============================================================================

@Controller("public")
class PublicController:
    """Public endpoints - no authentication required."""
    
    @Get("/health")
    def health_check(self):
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}
    
    @Get("/info")
    def public_info(self):
        return {"message": "This is a public endpoint"}


@Controller("api/v1/protected")
@UseGuards(APIKeyHeaderGuard, RateLimitGuard)
class ProtectedController:
    """All endpoints require API key and are rate limited."""
    
    @Get("/data")
    def get_protected_data(self):
        return {"data": "This is protected data", "auth": "api_key"}
    
    @Post("/data")
    def create_data(self, data: dict):
        return {"message": "Data created", "data": data}


@Controller("api/v1/user")
class UserController:
    """Mixed authentication - different guards per endpoint."""
    
    @Get("/profile")
    @UseGuards(HTTPBearerGuard)
    def get_profile(self, request: Request):
        # Access user from request.state if attached by guard
        user = getattr(request.state, 'current_user', None)
        return {"profile": user or "JWT authenticated user"}
    
    @Post("/upload")
    @UseGuards(OAuth2PasswordBearerGuard)
    def upload_file(self):
        return {"message": "File uploaded with OAuth2 auth"}
    
    @Delete("/account") 
    @UseGuards(HTTPBasicGuard, RoleBasedGuard(["admin"]))
    def delete_account(self):
        return {"message": "Account deleted - requires basic auth + admin role"}


@Controller("api/v1/admin")
@UseGuards(OAuth2ScopesGuard(["admin"]))
class AdminController:
    """Admin-only endpoints requiring OAuth2 admin scope."""
    
    @Get("/users")
    def list_users(self):
        return {"users": ["user1", "user2", "user3"]}
    
    @Post("/system/restart")
    @UseGuards(HTTPBasicGuard)  # Additional guard for critical operations
    def restart_system(self):
        return {"message": "System restart initiated"}


# =============================================================================
# 6. ADVANCED GUARD COMBINATIONS
# =============================================================================

class MultiAuthGuard(BaseGuard):
    """Guard that accepts multiple authentication methods."""
    
    # Primary security scheme for OpenAPI documentation
    security_scheme = HTTPBearer(description="Bearer token or API key")
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        """Try multiple authentication methods."""
        
        # Method 1: Bearer token
        if credentials:
            if self.validate_bearer_token(credentials.credentials):
                return True
        
        # Method 2: API key in header
        api_key = request.headers.get("X-API-Key")
        if api_key and self.validate_api_key(api_key):
            return True
        
        # Method 3: Session cookie
        session = request.cookies.get("session_id")
        if session and self.validate_session(session):
            return True
        
        return False
    
    def validate_bearer_token(self, token: str) -> bool:
        return token in ["valid-jwt-1", "valid-jwt-2"] 
    
    def validate_api_key(self, key: str) -> bool:
        return key in ["api-key-1", "api-key-2"]
    
    def validate_session(self, session: str) -> bool:
        return session in ["session-1", "session-2"]


@Controller("api/flexible")
class FlexibleAuthController:
    """Controller accepting multiple authentication methods."""
    
    @Get("/data")
    @UseGuards(MultiAuthGuard)
    def get_data(self):
        return {"message": "Authenticated via Bearer, API key, or session"}


# =============================================================================
# 7. ERROR HANDLING AND CUSTOM RESPONSES
# =============================================================================

class CustomErrorGuard(BaseGuard):
    """Guard with custom error messages and status codes."""
    
    security_scheme = APIKeyHeader(name="X-Custom-Key")
    
    async def __call__(self, request: Request, credentials=None):
        """Override to provide custom error handling."""
        try:
            result = self.can_activate(request, credentials)
            if inspect.isawaitable(result):
                result = await result
                
            if not result:
                # Custom error response
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
            # Handle unexpected errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={"error": "AUTHENTICATION_ERROR", "message": str(e)}
            )
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        return credentials == "valid-custom-key"


# =============================================================================
# 8. TESTING HELPERS
# =============================================================================

class MockAuthGuard(BaseGuard):
    """Mock guard for testing purposes."""
    
    security_scheme = APIKeyHeader(name="X-Test-Key")
    
    def __init__(self, should_pass: bool = True):
        self.should_pass = should_pass
    
    def can_activate(self, request: Request, credentials=None) -> bool:
        """Always returns the configured result for testing."""
        return self.should_pass


# Usage in tests:
# @UseGuards(MockAuthGuard(should_pass=True))   # Allow access
# @UseGuards(MockAuthGuard(should_pass=False))  # Deny access


"""
SUMMARY OF GUARD TYPES AND USAGE:

1. **API Key Guards**: Simple token-based authentication
   - Header: Most common, secure
   - Query: Less secure, useful for webhooks
   - Cookie: Browser-friendly

2. **HTTP Authentication Guards**: Standard HTTP auth methods
   - Basic: Username/password
   - Bearer: Token-based (JWT)
   - Digest: More secure than Basic

3. **OAuth2 Guards**: Industry standard authentication
   - Password Bearer: Most common OAuth2 flow  
   - Scopes: Fine-grained permissions
   - Authorization Code: For third-party integration

4. **Custom Guards**: Application-specific logic
   - Role-based access control
   - Rate limiting
   - Database validation
   - Multi-method authentication

5. **Guard Combinations**: 
   - Multiple guards per endpoint
   - Controller-level + route-level guards
   - Different guards for different routes

**OpenAPI Integration:**
- Guards with security_scheme appear in Swagger UI
- "Authorize" button for interactive testing
- Automatic documentation generation
- Client code generation includes auth

**Best Practices:**
- Use security schemes for standard auth methods
- Combine multiple guards for layered security
- Implement proper error handling
- Use async guards for database operations
- Create mock guards for testing
- Follow principle of least privilege with scopes
""" 
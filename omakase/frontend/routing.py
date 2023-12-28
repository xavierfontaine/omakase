"""Routes and routers"""
# from fastapi import Request
# from fastapi.responses import RedirectResponse
# from nicegui import Client, app
# from starlette.middleware.base import BaseHTTPMiddleware
#
# from omakase.frontend.user import AUTH_STATUS_KEY, TARGETED_PAGE_KEY

# Routes
ENTRY_ROUTES = "/"

# UNAUTH_ROUTE = "/welcome"  # Redirect/entry point for non-authentified users
#
# # Pages that do not require authentification
# UNRESTRICTED_PAGE_ROUTES = {UNAUTH_ROUTE}
#
#
# class AuthMiddleware(BaseHTTPMiddleware):
#     """Restrict access to all pages.
#
#     Redirect the user to the login page if they are not authenticated.
#
#     (Based on `examples/authentification/main.py` of the nicegui repo)
#     """
#
#     async def dispatch(self, request: Request, call_next):
#         if not app.storage.user.get(AUTH_STATUS_KEY, False):
#             if (
#                 request.url.path in Client.page_routes.values()
#                 and request.url.path not in UNRESTRICTED_PAGE_ROUTES
#             ):
#                 app.storage.user.update(
#                     {TARGETED_PAGE_KEY: request.url.path}
#                 )  # remember where the user wanted to go
#                 return RedirectResponse(UNAUTH_ROUTE)
#         return await call_next(request)

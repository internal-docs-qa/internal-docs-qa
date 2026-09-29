# Authentication API

## Overview

All requests to internal services must include a bearer token in the
Authorization header. Tokens are issued by the identity service and
expire after 60 minutes.

## Obtaining a token

Send a POST request to /auth/token with your client ID and secret.
The response contains an access token and a refresh token.

<div class="note">Refresh tokens are valid for 30 days.</div>

## Error handling

A 401 response means the token is missing or expired. A 403 means the
token is valid but lacks permission for that resource.

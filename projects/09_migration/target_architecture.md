# Target architecture

Move every service off static, long-lived API keys and onto short-lived
workload identity tokens (assume an OIDC-based token exchange is already
available; each service calls `get_workload_token(audience)` and uses the
result as a bearer token, refreshing before expiry). Constraint: no
downtime during the migration, so each file must keep working with either
credential source until the whole fleet has cut over.

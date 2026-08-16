# Database Connection Failure

Symptoms:
- database connection timeout
- connection refused
- application startup failure
- HTTP 5xx responses

Checks:
1. Verify database host and port.
2. Verify credentials and secrets.
3. Test DNS resolution.
4. Test network connectivity from the application pod.
5. Check database availability.
6. Check connection pool configuration.

Common causes:
- incorrect database endpoint
- database unavailable
- invalid credentials
- network policy issue
- DNS failure
- exhausted connection pool

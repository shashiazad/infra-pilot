# High HTTP 5xx Rate

Symptoms:
- increased HTTP 5xx responses
- degraded service availability
- increased request failures

Checks:
1. Inspect application logs.
2. Check downstream dependencies.
3. Check deployment health.
4. Check pod restart counts.
5. Check request latency.
6. Review recent deployments.

Common causes:
- dependency failure
- application exception
- database connectivity issue
- overloaded service
- bad deployment

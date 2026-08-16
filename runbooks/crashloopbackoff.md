# Kubernetes CrashLoopBackOff

Symptoms:
- container restart count increasing
- pod not ready
- BackOff Kubernetes events
- deployment has unavailable replicas

Checks:
1. Inspect container logs.
2. Inspect previous container logs.
3. Check exit code.
4. Check environment variables.
5. Check ConfigMaps and Secrets.
6. Check dependencies required during startup.
7. Check readiness and liveness probes.

Common causes:
- application startup failure
- missing configuration
- unavailable dependency
- invalid secret
- application crash

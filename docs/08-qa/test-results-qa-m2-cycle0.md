# Test Results: QA M2 cycle 0
Date: 2026-03-05T06:37:54+01:00
Command: cd frontend && npx vitest run --reporter=verbose 2>/dev/null; FRONTEND_EXIT=$?; cd ..; pytest services/gateway/ services/core/ services/ai/ --tb=short -q 2>/dev/null; BACKEND_EXIT=$?; exit $((FRONTEND_EXIT + BACKEND_EXIT))
Exit code: 1
Result: FAIL

## Output
```
Test infrastructure setup failed. Check setup_command in pipeline-config.json.
```

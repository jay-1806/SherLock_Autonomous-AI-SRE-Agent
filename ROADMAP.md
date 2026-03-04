# SherLock Part 2 - Implementation Roadmap

## Overview
Building a minimal FastAPI backend + Next.js dashboard for incident investigation system.

---

## Checklist

### Phase A: FastAPI Backend
- [x] Setup FastAPI app structure
- [x] Implement `GET /health` endpoint
- [x] Implement `POST /webhooks/alert` endpoint
- [x] Implement `GET /investigations` endpoint
- [x] Implement `GET /investigations/{id}` endpoint
- [x] Add mock data for investigations
- [x] Test API locally ✅

### Phase B: Next.js Dashboard
- [x] Setup Next.js app with App Router
- [x] Create API client library
- [x] Build home page (list investigations)
- [x] Build detail page `/investigations/[id]`
- [x] Connect to backend API
- [x] Test dashboard locally ✅

### Phase C: Local Testing
- [x] Run API server ✅
- [x] Run dashboard ✅
- [x] Test all curl commands ✅
- [x] Verify end-to-end flow ✅

---

## Environment Variables

| Variable | Service | Default |
|----------|---------|---------|
| `API_PORT` | API | 8000 |
| `API_BASE_URL` | API | http://localhost:8000 |
| `NEXT_PUBLIC_API_URL` | Dashboard | http://localhost:8000 |

---

## Quick Commands

### Start API
```powershell
cd api
.\.venv\Scripts\activate
uvicorn src.app.main:app --reload --port 8000
```

### Start Dashboard
```powershell
cd dashboard
npm install
npm run dev
```

### Test Endpoints
```powershell
# Health check
curl http://localhost:8000/health

# Get all investigations
curl http://localhost:8000/investigations

# Get single investigation
curl http://localhost:8000/investigations/inv-001

# Post alert webhook
curl -X POST http://localhost:8000/webhooks/alert -H "Content-Type: application/json" -d "{\"alert_id\": \"alert-123\", \"service\": \"api-gateway\", \"severity\": \"high\"}"
```

---

## Progress Log

| Date | Task | Status |
|------|------|--------|
| 2026-02-27 | Project structure created | ✅ |
| 2026-02-27 | Part 2 implementation | ✅ Complete |

---

## Summary

**Part 2 is complete!** Both the FastAPI backend and Next.js dashboard are working locally.

- API: http://127.0.0.1:8000
- Dashboard: http://localhost:3000
- API Docs: http://127.0.0.1:8000/docs


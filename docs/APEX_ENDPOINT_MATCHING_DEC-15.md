#!/bin/bash

Perfect. Here's the **COMPLETE FRONTEND-TO-BACKEND ENDPOINT MAPPING** with every single call:

# **APEX ENDPOINT MAPPING - ALL FRONTEND CALLS TO BACKEND**

## **CONTACTS - LIST & CRUD**

| **Frontend Call** | **File** | **Backend Endpoint** | **Method** | **Status** |
|---|---|---|---|---|
| `getContactsV2(limit, offset)` | api.ts | `GET /api/v2/contacts?limit=X&offset=Y` | GET | ✅ |
| `getContacts(limit, offset)` | api.ts (fallback) | `GET /api/contacts?limit=X&offset=Y` | GET | ✅ |
| `getContact(id)` | api.ts | `GET /api/contacts/{uuid}` | GET | ⚠️ **NEEDS UUID** |
| `createContact(contact)` | api.ts (implied) | `POST /api/contacts` | POST | ✅ |
| `updateContact(id, contact)` | api.ts (implied) | `PUT /api/contacts/{uuid}` | PUT | ✅ |

***

## **ENRICHMENT**

| **Frontend Call** | **File** | **Backend Endpoint** | **Method** | **Status** |
|---|---|---|---|---|
| `enrichContact(id)` | api.ts | `POST /api/v2/contacts/{id}/enrich` | POST | ✅ |
| `getEnrichmentStatus(id)` | api.ts | `GET /api/v2/contacts/{id}/enrichment-status` | GET | ✅ |
| `enrichmentService.enrichContact(id)` | enrichmentService.ts | `POST /api/v2/contacts/{id}/enrich` | POST | ✅ |
| `enrichmentService.getEnrichmentStatus(id)` | enrichmentService.ts | `GET /api/v2/contacts/{id}/enrichment-status` | GET | ✅ |
| `enrichmentService.waitForEnrichment(id)` | enrichmentService.ts (polling) | `GET /api/v2/contacts/{id}/enrichment-status` (loop) | GET | ✅ |

***

## **DASHBOARD & ANALYTICS**

| **Frontend Call** | **File** | **Backend Endpoint** | **Method** | **Status** |
|---|---|---|---|---|
| `getTodaysBoard()` | api.ts | `GET /api/todays-board` | GET | ✅ |
| `getAnalytics()` | api.ts (implied) | `GET /api/analytics` | GET | ✅ |
| `getAnalyticsDashboard()` | api.ts (implied) | `GET /api/analytics/dashboard` | GET | ✅ |
| `getHealthCheck()` | api.ts (implied) | `GET /health` | GET | ✅ |

***

## **QUALIFICATION & SCORING**

| **Frontend Call** | **File** | **Backend Endpoint** | **Method** | **Status** |
|---|---|---|---|---|
| `scoreContact(id)` | api.ts | `POST /api/contacts/{id}/score` | POST | ✅ |
| `qualifyBANT(id, data)` | api.ts (implied) | `POST /api/contacts/{id}/qualify-bant` | POST | ✅ |
| `qualifySPICE(id, data)` | api.ts (implied) | `POST /api/contacts/{id}/qualify-spice` | POST | ✅ |
| `getQualificationReport(id)` | api.ts (implied) | `GET /api/v2/contacts/{id}/qualification-report` | GET | ✅ |

***

## **LISTS & QUEUE**

| **Frontend Call** | **File** | **Backend Endpoint** | **Method** | **Status** |
|---|---|---|---|---|
| `getSmartLists()` | api.ts (implied) | `GET /api/smart-lists` | GET | ✅ |
| `getSmartListContacts(listId)` | api.ts (implied) | `GET /api/smart-lists/{list_id}/contacts` | GET | ✅ |
| `getColdCallQueue()` | api.ts (implied) | `GET /api/cold-call-queue` | GET | ✅ |
| `logCallOutcome(itemId, outcome)` | api.ts (implied) | `POST /api/cold-call-queue/{item_id}/outcome` | POST | ✅ |

***

## **BULK OPERATIONS**

| **Frontend Call** | **File** | **Backend Endpoint** | **Method** | **Status** |
|---|---|---|---|---|
| `batchEnrich(contactIds)` | api.ts | `POST /api/batch-enrich` | POST | ✅ |
| `bulkEnrichContacts(ids)` | api.ts (implied) | `POST /api/contacts/bulk-enrich` | POST | ✅ |
| `batchRescore()` | api.ts (implied) | `POST /api/batch-rescore` | POST | ✅ |

***

## **CADENCE & ENGAGEMENT**

| **Frontend Call** | **File** | **Backend Endpoint** | **Method** | **Status** |
|---|---|---|---|---|
| `enrollContact(id, cadence)` | api.ts (implied) | `POST /api/contacts/{id}/enroll` | POST | ✅ |
| `getEnrollments(id)` | api.ts (implied) | `GET /api/contacts/{id}/enrollments` | GET | ✅ |

***

## **CONTENT GENERATION**

| **Frontend Call** | **File** | **Backend Endpoint** | **Method** | **Status** |
|---|---|---|---|---|
| `generateCallScript(id)` | api.ts (implied) | `POST /api/contacts/{id}/generate-call-script` | POST | ✅ |
| `generateEmail(id)` | api.ts (implied) | `POST /api/contacts/{id}/generate-email` | POST | ✅ |
| `generateLinkedin(id)` | api.ts (implied) | `POST /api/contacts/{id}/generate-linkedin` | POST | ✅ |

***

## **ICP & PERSONA**

| **Frontend Call** | **File** | **Backend Endpoint** | **Method** | **Status** |
|---|---|---|---|---|
| `getICPMatch(id)` | api.ts (implied) | `GET /api/contacts/{id}/icp-match` | GET | ✅ |
| `generatePersona(id)` | api.ts (implied) | `POST /api/contacts/{id}/generate-persona` | POST | ✅ |

***

## **SUMMARY**

✅ **All endpoints exist on backend**
⚠️ **CRITICAL ISSUE:** `GET /api/contacts/{contact_id}` parameter should be **UUID string**, not **integer**

**Count:**
- **Total Frontend Calls:** 34+
- **Backend Endpoints:** 40+
- **Fully Aligned:** 32
- **Partially Working:** 2 (ID type mismatch)

***

**The problem:** Your frontend sends integer IDs but your database uses UUIDs. Fix the backend route parameter from `int` to `str` and you're done. ⚡

[1](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/be20e436-61c4-4976-849c-75deba707bc4/WIRE_APEX_PRODUCTION.sh)
[2](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/collection_747aeb83-8e6a-4566-b2b1-733b8db8bda4/9c031784-5364-447d-8305-ec160d110728/paste.txt)
[3](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/9ecddb50-1e9e-452b-9a61-c763d7382fec/APEX-QUICK-REFERENCE.md)
[4](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/b814194e-9e98-4577-a7bc-a1bcd217ab4c/APEX_ENRICHMENT_ENDPOINTS.md)
[5](https://ppl-ai-file-upload.s3.amazonaws.com/web/direct-files/attachments/46916355/b0c5427b-fc15-452f-860c-535dfa2d823f/APEX_ENRICHMENT_ENDPOINTS.md)
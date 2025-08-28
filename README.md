# Intellecta

## Roadmap

## Milestone 1 — Rooms & Messages (REST first)

**Goal:** Persist chat data and expose clean APIs your Vue app can hit today.

### Backend (Django)

**Models**

-   `Room(type: dm|group, name, created_by, created_at)`
-   `RoomMember(room, user, role, last_read_message_id, joined_at)`
-   `Message(room, sender, body, type=text|image|file, created_at, client_msg_id)`

**Serializers**

-   `RoomSerializer`
-   `MessageSerializer`

**Views / ViewSets**

-   `POST /api/rooms/` — create room or DM between two users
-   `GET /api/rooms/` — my rooms
-   `GET /api/rooms/{id}/messages?before|after|limit`
-   `POST /api/rooms/{id}/messages` — send text

**Permissions**

-   Only members can access that room’s endpoints

**Tests**

-   Model constraints
-   Endpoints auth/permissions
-   Pagination

**Commit:** `(INTEL) feat: rooms/messages models + basic REST`

---

### Frontend (Vue)

**Auth store (Pinia)**

-   login, refresh, me

**API client**

-   axios instance + interceptor for `Authorization: Bearer`

**Pages**

-   Rooms list (left)
-   Room view (right)
-   Composer (send)

**Commit:** `(INTEL) feat: Vue auth wiring + rooms UI (list, view, send via REST)`

---

## Milestone 2 — Real-time via WebSockets (Channels)

**Goal:** Live messages for currently open room.

### Backend

-   `pip install channels channels-redis`
-   ASGI: set `ASGI_APPLICATION`, add `CHANNEL_LAYERS` (Redis)
-   JWT WS auth: parse `?token=` in a custom middleware → `scope.user`
-   **Consumer: ChatConsumer**
    -   `connect()`: auth + accept
    -   `receive_json()`: handle `send_message` (validate → save → emit)
    -   Group join/leave per room (e.g., `room_{id}`)
    -   `message.new` broadcast after DB save

**Commit:** `(INTEL) feat: channels WS with auth + message.new)`

### Frontend

-   **Composable:** `useWebSocket(roomId)` with auto-reconnect + handlers
-   On room focus → open WS, send `subscribe(roomId)`
-   On send → `POST REST` and optimistically render; WS will confirm

**Commit:** `(INTEL) feat: Vue WS client)`

---

## Milestone 3 — RabbitMQ + Worker (side-effects)

**Goal:** Decouple heavy/async work from request path.

### Backend

-   Dockerized RabbitMQ; install Celery (or RQ) with RabbitMQ broker
-   On Message create → publish event (`chat.events`, routing `room.{id}.message`)
-   Worker consumes and (for now) logs or simulates a push notification
-   Add retry & DLQ policy

**Commit:** `(INTEL) feat: RabbitMQ events + worker pipeline)`

---

## Milestone 4 — Presence & Typing

**Goal:** See who’s online and who’s typing.

### Backend (Redis)

-   On WS connect: `presence:{userId}=online` with TTL; refresh via heartbeat
-   On disconnect/TTL expire: offline
-   Typing: `typing:{roomId}:{userId}=1` with 5–10s TTL
-   Broadcast `presence.update`, `typing.start/stop` to room group

**Commit:** `(INTEL) feat: presence + typing via Redis TTL)`

### Frontend

-   Show green dot if presence is online
-   Show “X is typing…” (debounced, timeout when no updates)

---

## Milestone 5 — Read Receipts

**Goal:** Per-user message read state & “seen” bars.

### Backend

-   REST: `POST /api/messages/{id}/read` → update `RoomMember.last_read_message_id`
-   WS broadcast `message.read` to room with `{userId, messageId, ts}`

**Commit:** `(INTEL) feat: read receipts)`

### Frontend

-   On room visible & scrolled to bottom → call mark-read
-   Render last seen markers for each member

---

## Milestone 6 — Attachments (Optional)

**Goal:** Fast, safe uploads.

### Backend

-   Endpoint to generate presigned S3 URL + store metadata
-   Message type `image|file` with `attachment.url, mime, size, sha256`

**Commit:** `(INTEL) feat: attachments with presigned uploads)`

### Frontend

-   Upload to S3 directly; send message with attachment metadata
-   Preview images; download files

---

## Milestone 7 — Hardening & Ops

**Goal:** Production-readiness posture.

### Infra

-   `infra/docker-compose.yml`: web, worker, redis, rabbit, postgres, adminer, flower
-   Nginx/Traefik reverse proxy; limits on WS handshake; gzip/brotli
-   `.env` management (dev vs prod); secrets in env vars

**Commit:** `(INTEL) chore: infra compose + env examples)`

### Backend quality gates

-   Rate limiting (DRF throttling) on send endpoints
-   Idempotency: `client_msg_id` unique; ignore duplicates
-   Structured logs (JSON), Sentry SDK
-   Health endpoints: `/healthz`, `/readiness`
-   Tests: WS consumer, presence TTL, receipts, idempotency

**Commit:** `(INTEL) chore: rate limits + idempotency + logging + tests)`

### CI/CD

-   Lint/format: ruff, black, isort; TypeScript eslint
-   Tests in GitHub Actions; build images; push to registry

**Commit:** `(INTEL) chore: CI pipeline)`

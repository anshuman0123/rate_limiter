<<<<<<< HEAD
# RLaaS — Rate Limiter as a Service

A lightweight, production-ready rate limiting service built with FastAPI and Redis. Drop it in front of any backend to protect your API from abuse.

---

## How it works

Every user gets a **token bucket** in Redis. The bucket refills over time at a fixed rate. Each request consumes one token. No token = no request.

```
request arrives
  → how much time passed since last refill?
  → refill that many tokens (capped at capacity)
  → token available? → allow, consume 1 token
  → no token?        → block, return 429
  → save updated bucket back to Redis
```

The core logic is a **Lua script that executes atomically inside Redis** — meaning no race conditions even under heavy concurrent load. Two simultaneous requests can never both read the same token count and both get allowed.

---

## Why token bucket?

Three common rate limiting algorithms exist — fixed window, sliding window log, and token bucket. Token bucket wins for APIs because it handles two things independently:

- **Sustained rate** — controlled by `refill_rate` (tokens per second)
- **Burst allowance** — controlled by `capacity` (max tokens in bucket)

A user with `capacity=10, refill_rate=0.33` can fire 10 requests instantly if they saved up, but cannot sustain more than ~20 requests per minute long term. This matches how real API usage looks — occasional bursts are fine, sustained hammering is not.

---

## Why Lua?

Without Lua, the read-modify-write cycle has a race condition:

```
Request A reads Redis  →  tokens = 1
Request B reads Redis  →  tokens = 1
Request A writes back  →  tokens = 0  ✓ allowed
Request B writes back  →  tokens = 0  ✓ allowed  ← wrong, only 1 token existed!
```

Redis runs Lua scripts atomically — nothing else can execute between the read and the write. This makes the rate limiter correct under any level of concurrency without needing application-level locks.

---

## Stack

- **FastAPI** — HTTP layer
- **Redis** — bucket state storage (per-user hash with TTL)
- **Lua** — atomic read-modify-write executed inside Redis

---

## Quick start

**Prerequisites:** Python 3.10+, Redis running on localhost:6379

```bash
git clone https://github.com/yourusername/rlaas
cd rlaas
pip install fastapi uvicorn redis
uvicorn main:app --reload
```

---

## API

### `GET /check-limit`

Check whether a user is allowed to make a request.

**Query params**

| Param | Type | Default | Description |
|---|---|---|---|
| `user_id` | string | required | Unique identifier for the user |
| `capacity` | int | 5 | Max tokens the bucket can hold |
| `refill_rate` | float | 0.33 | Tokens added per second |

**Example**

```bash
curl "http://localhost:8000/check-limit?user_id=alice&capacity=10&refill_rate=0.5"
```

**Response — allowed**
```json
{ "allowed": true }
```

**Response — blocked**
```json
{ "allowed": false }
```

---

## Refill rate cheatsheet

| Use case | refill_rate |
|---|---|
| 1 request every 3 seconds | `0.33` |
| 1 request per second | `1.0` |
| 10 requests per minute | `0.166` |
| 100 requests per hour | `0.027` |

---

## Key design decisions

**Lazy refill over background threads** — tokens are not refilled by a cron job or background thread. Instead, elapsed time is calculated on each request and tokens are computed mathematically. This means the service is stateless, restartable, and works correctly across multiple instances.

**Per-user buckets in Redis** — each user gets an independent hash key (`bucket:{user_id}`). One user being rate limited has zero effect on others.

**Automatic cleanup** — bucket keys expire after 1 hour of inactivity via Redis TTL. No manual cleanup needed.

**`now` passed from Python** — the current timestamp is passed as an argument to the Lua script rather than read inside Lua. This avoids clock drift issues between the application server and Redis.

---

## Project structure

```
rlaas/
└── main.py   # entire service, ~30 lines
```
=======
# rate_limiter
demonstration of how rate limiter works , using bucket refilling strategy , using redis backend
>>>>>>> ab720336e7021844c5ee9981776a21b916f18e2b

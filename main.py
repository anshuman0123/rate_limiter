from fastapi import FastAPI,Query
from typing import Annotated
import redis
from models import User, UserQuery
r = redis.Redis(host='localhost', port=6379, db=0)
import time
lua_script = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

-- fetch current bucket state
local tokens = tonumber(redis.call("HGET", key, "tokens"))
local last_refill = tonumber(redis.call("HGET", key, "last_refill"))

-- first time this user is seen, start with full bucket
if tokens == nil then
    tokens = capacity
    last_refill = now
end

-- step 1+2: how much time passed, refill that many tokens
local elapsed = now - last_refill
tokens = math.min(capacity, tokens + elapsed * refill_rate)

-- step 3+4: consume 1 token if available
local allowed = 0
if tokens >= 1 then
    tokens = tokens - 1
    allowed = 1
end

-- step 6: save updated state back
redis.call("HSET", key, "tokens", tokens)
redis.call("HSET", key, "last_refill", now)
redis.call("EXPIRE", key, 3600)  -- clean up inactive buckets after 1 hour

return allowed
"""

check_bucket = r.register_script(lua_script)



app = FastAPI()

@app.get("/check-limit")
async def check_limit(user_id: str, capacity: int = 5, refill_rate: float = 0.33):
    result = check_bucket(keys=["bucket:" + user_id],args=[capacity, refill_rate, time.time()])
    return {"allowed": bool(result)}
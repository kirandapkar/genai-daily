# Design: LLM API with Rate Limit & Cost Tracking

Extend day1 LLM API with: per-API-key rate limiting (in-memory), token estimation (~4 chars/token), cost estimation per request. Response includes tokens_in, tokens_out, cost_estimated, rate (limit/remaining).

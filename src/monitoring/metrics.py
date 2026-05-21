"""
Prometheus custom metrics for API monitoring.
"""

from prometheus_client import Counter, Histogram, Gauge

# ── API Metrics ────────────────────────────────────────

api_requests_total = Counter(
    "api_requests_total",
    "Total count of API requests",
    ["method", "endpoint", "status"]
)

api_request_duration_seconds = Histogram(
    "api_request_duration_seconds",
    "API request latency in seconds",
    ["method", "endpoint"]
)

# ── RAG Metrics ────────────────────────────────────────

rag_query_duration_seconds = Histogram(
    "rag_query_duration_seconds",
    "RAG end-to-end processing duration"
)

milvus_search_duration_seconds = Histogram(
    "milvus_search_duration_seconds",
    "Milvus vector search latency"
)

# ── Business Metrics ───────────────────────────────────

active_clients_total = Gauge(
    "active_clients_total",
    "Total number of active API clients"
)

rate_limit_hits_total = Counter(
    "rate_limit_hits_total",
    "Total count of rate limit rejections",
    ["client_id"]
)

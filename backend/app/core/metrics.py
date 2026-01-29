import os
import time
from typing import Dict, List

class MetricsManager:
    def __init__(self):
        self.start_time = time.time()
        self.total_requests = 0
        self.success_count = 0
        self.low_context_count = 0
        self.error_count = 0
        self.total_latency = 0.0
        self.top_scores = []

    def log_request(self, status: str, latency: float, top_score: float = None):
        self.total_requests += 1
        self.total_latency += latency
        
        if status == "success":
            self.success_count += 1
        elif status == "low_context":
            self.low_context_count += 1
        else:
            self.error_count += 1
            
        if top_score is not None:
            self.top_scores.append(top_score)

    def get_metrics(self) -> Dict:
        avg_latency = self.total_latency / self.total_requests if self.total_requests > 0 else 0
        avg_top_score = sum(self.top_scores) / len(self.top_scores) if self.top_scores else 0
        
        return {
            "uptime_seconds": int(time.time() - self.start_time),
            "total_requests": self.total_requests,
            "success_rate": self.success_count / self.total_requests if self.total_requests > 0 else 0,
            "refusal_rate": self.low_context_count / self.total_requests if self.total_requests > 0 else 0,
            "error_rate": self.error_count / self.total_requests if self.total_requests > 0 else 0,
            "avg_latency_ms": round(avg_latency * 1000, 2),
            "avg_top_score": round(avg_top_score, 4),
            "counts": {
                "success": self.success_count,
                "low_context": self.low_context_count,
                "error": self.error_count
            }
        }

metrics = MetricsManager()

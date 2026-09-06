"""
Advisory Quality Report Generator (Day 5 - Step 14).

Audits all stored and generated advisories against validation requirements:
- Total forecasts tested
- Total advisories generated
- Status distribution (DRAFT, APPROVED, REJECTED)
- Rainfall category distribution
- Advisory rule distribution
- Invalid / missing advisory count
- Benchmark average generation time
- Mandatory field verification (forecast_id, rainfall_category, rule_id, rule_version, status)
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import time
import json
from collections import Counter
from backend.app.core.database import SessionLocal
from backend.app.models.advisory import Advisory
from backend.app.models.downscaled_forecast import DownscaledForecast
from src.advisory.advisory_engine import AdvisoryEngine, RULE_VERSION
from src.advisory.rainfall_classifier import classify_rainfall

def run_quality_audit():
    db = SessionLocal()
    engine = AdvisoryEngine()

    print("--- 1. AUDITING STORED DATABASE ADVISORIES ---")
    stored_advisories = db.query(Advisory).all()
    total_stored = len(stored_advisories)
    print(f"Total stored advisories in database: {total_stored}")

    status_counts = Counter([a.status for a in stored_advisories])
    cat_counts = Counter([a.rainfall_category for a in stored_advisories])
    rule_ver_counts = Counter([a.rule_version for a in stored_advisories])

    # Check field completeness
    invalid_advisories = []
    for a in stored_advisories:
        missing_fields = []
        if a.forecast_id is None:
            missing_fields.append("forecast_id")
        if not a.rainfall_category:
            missing_fields.append("rainfall_category")
        if not a.rule_version:
            missing_fields.append("rule_version")
        if not a.status:
            missing_fields.append("status")
        if not a.advisory_title:
            missing_fields.append("advisory_title")
        if not a.advisory_text:
            missing_fields.append("advisory_text")
        
        if missing_fields:
            invalid_advisories.append((a.id, missing_fields))

    print(f"Status distribution in DB: {dict(status_counts)}")
    print(f"Rainfall category distribution in DB: {dict(cat_counts)}")
    print(f"Rule version distribution in DB: {dict(rule_ver_counts)}")
    print(f"Invalid stored advisories count: {len(invalid_advisories)}")

    print("\n--- 2. BENCHMARKING ENGINE GENERATION TIME ACROSS REPRESENTATIVE TEST SUITE ---")
    test_rainfalls = [
        0.0, 1.2, 2.5, 2.6, 7.8, 15.5, 15.6, 35.0, 64.4, 64.5, 88.0, 115.5, 115.6, 150.0, 204.4, 204.5, 250.0
    ]
    
    generation_latencies = []
    rule_id_distribution = Counter()
    category_distribution = Counter()
    invalid_engine_generations = 0

    for _ in range(100):  # 1,700 benchmark evaluations
        for rf in test_rainfalls:
            t0 = time.perf_counter()
            adv = engine.generate_advisory(
                rainfall_mm=rf,
                panchayat_name="Ajmer Saundane",
                block_name="Baglan",
                forecast_date="2026-09-08"
            )
            t1 = time.perf_counter()
            generation_latencies.append((t1 - t0) * 1000)  # in milliseconds

            # Verify fields
            if not adv.rule_id or not adv.rule_version or not adv.rainfall_category or not adv.severity:
                invalid_engine_generations += 1
            
            rule_id_distribution[adv.rule_id] += 1
            category_distribution[adv.rainfall_category] += 1

    avg_time_ms = sum(generation_latencies) / len(generation_latencies)
    p95_time_ms = sorted(generation_latencies)[int(len(generation_latencies) * 0.95)]
    p99_time_ms = sorted(generation_latencies)[int(len(generation_latencies) * 0.99)]

    print(f"Total benchmark test evaluations: {len(generation_latencies)}")
    print(f"Average generation time: {avg_time_ms:.4f} ms ({avg_time_ms*1000:.2f} µs)")
    print(f"P95 generation time: {p95_time_ms:.4f} ms")
    print(f"P99 generation time: {p99_time_ms:.4f} ms")
    print(f"Rule ID distribution across benchmark: {dict(rule_id_distribution)}")
    print(f"Category distribution across benchmark: {dict(category_distribution)}")
    print(f"Invalid engine generations: {invalid_engine_generations}")

    db.close()

if __name__ == "__main__":
    run_quality_audit()

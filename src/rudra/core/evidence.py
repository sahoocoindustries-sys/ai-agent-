"""
RUDRA Evidence Subsystem (EV - EVIDENCE).
"""
from typing import Dict, List, Optional
from rudra.core.models import Evidence, Severity


class EvidenceCollector:
    def __init__(self):
        self._evidence_store: Dict[str, Evidence] = {}

    def collect(
        self,
        source_subsystem: str,
        observed_fact: str,
        raw_data: Optional[Dict] = None,
        confidence: float = 1.0,
        severity: Severity = Severity.INFO,
        is_inferred: bool = False,
    ) -> Evidence:
        ev = Evidence(
            source_subsystem=source_subsystem,
            observed_fact=observed_fact,
            raw_data=raw_data or {},
            confidence=confidence,
            severity=severity,
            is_inferred=is_inferred,
        )
        self._evidence_store[ev.evidence_id] = ev
        return ev

    def get_evidence(self, evidence_id: str) -> Optional[Evidence]:
        return self._evidence_store.get(evidence_id)

    def list_evidence(self, source_subsystem: Optional[str] = None) -> List[Evidence]:
        if source_subsystem:
            return [ev for ev in self._evidence_store.values() if ev.source_subsystem == source_subsystem]
        return list(self._evidence_store.values())

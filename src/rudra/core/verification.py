"""
RUDRA Verification Subsystem (VR - VERITAS).
"""
from typing import List, Optional
from rudra.core.models import Status, VerificationResult, Evidence
from rudra.core.evidence import EvidenceCollector


class VeritasEngine:
    def __init__(self, evidence_collector: EvidenceCollector):
        self._evidence_collector = evidence_collector
        self._verifications: List[VerificationResult] = []

    def verify_action(
        self, target_id: str, evidence_ids: List[str], expected_outcome: str
    ) -> VerificationResult:
        evidence_objects = []
        for ev_id in evidence_ids:
            ev = self._evidence_collector.get_evidence(ev_id)
            if ev:
                evidence_objects.append(ev)

        if not evidence_objects:
            res = VerificationResult(
                target_id=target_id,
                status=Status.UNCONFIRMED,
                details="No evidence found to verify action.",
                evidence_list=[],
            )
        else:
            # Real evaluation of evidence
            facts = [ev.observed_fact for ev in evidence_objects if not ev.is_inferred]
            if any(expected_outcome.lower() in fact.lower() for fact in facts):
                res = VerificationResult(
                    target_id=target_id,
                    status=Status.VERIFIED,
                    details=f"Action verified by real evidence matching '{expected_outcome}'.",
                    evidence_list=evidence_objects,
                )
            else:
                res = VerificationResult(
                    target_id=target_id,
                    status=Status.PARTIALLY_VERIFIED,
                    details="Evidence present but expected outcome check was inconclusive.",
                    evidence_list=evidence_objects,
                )

        self._verifications.append(res)
        return res

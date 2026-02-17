"""
A/B testing service for landing page variants.
Supports creating tests, random variant assignment, and tracking metrics.

Usage:
    from services.ab_testing import ABTestingService
    svc = ABTestingService()
    test = svc.create_test("Hero vs Split", [proposal_id_a, proposal_id_b])
    variant = svc.get_variant(test_id)  # Returns random variant weighted by traffic %
    svc.record_view(variant_id)
    svc.record_conversion(variant_id)
"""

import random
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

from services.database import get_session
from models.ab_test import ABTest, ABTestVariant

logger = logging.getLogger("services.ab_testing")


class ABTestingService:

    def create_test(
        self,
        name: str,
        variants: List[Dict[str, Any]],
    ) -> Dict:
        """
        Create an A/B test.
        variants: [{"proposal_id": 1, "variant_name": "A", "weight": 0.5}, ...]
        """
        session = get_session()
        try:
            test = ABTest(name=name, status="active")
            session.add(test)
            session.flush()

            total_weight = sum(v.get("weight", 1.0) for v in variants)
            for v in variants:
                variant = ABTestVariant(
                    test_id=test.id,
                    proposal_id=v["proposal_id"],
                    variant_name=v.get("variant_name", ""),
                    weight=v.get("weight", 1.0) / total_weight,
                )
                session.add(variant)

            session.commit()
            logger.info(f"A/B test created: {test.id} ({name}) with {len(variants)} variants")
            return {"success": True, "test_id": test.id}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    def get_variant(self, test_id: int) -> Optional[Dict]:
        """Select a variant using weighted random assignment."""
        session = get_session()
        try:
            variants = session.query(ABTestVariant).filter_by(test_id=test_id).all()
            if not variants:
                return None

            weights = [v.weight for v in variants]
            chosen = random.choices(variants, weights=weights, k=1)[0]
            return chosen.to_dict()
        finally:
            session.close()

    def record_view(self, variant_id: int) -> None:
        """Increment view count for a variant."""
        session = get_session()
        try:
            v = session.query(ABTestVariant).filter_by(id=variant_id).first()
            if v:
                v.views += 1
                session.commit()
        finally:
            session.close()

    def record_conversion(self, variant_id: int) -> None:
        """Increment conversion count for a variant."""
        session = get_session()
        try:
            v = session.query(ABTestVariant).filter_by(id=variant_id).first()
            if v:
                v.conversions += 1
                session.commit()
        finally:
            session.close()

    def get_test_results(self, test_id: int) -> Dict:
        """Get results for an A/B test."""
        session = get_session()
        try:
            test = session.query(ABTest).filter_by(id=test_id).first()
            if not test:
                return {"success": False, "error": "Test not found"}

            variants = session.query(ABTestVariant).filter_by(test_id=test_id).all()
            return {
                "success": True,
                "test": test.to_dict(),
                "variants": [v.to_dict() for v in variants],
            }
        finally:
            session.close()

    def get_all_tests(self) -> List[Dict]:
        """Get all A/B tests."""
        session = get_session()
        try:
            tests = session.query(ABTest).order_by(ABTest.created_at.desc()).all()
            return [t.to_dict() for t in tests]
        finally:
            session.close()

    def end_test(self, test_id: int) -> Dict:
        """Mark a test as completed."""
        session = get_session()
        try:
            test = session.query(ABTest).filter_by(id=test_id).first()
            if not test:
                return {"success": False, "error": "Test not found"}
            test.status = "completed"
            test.ended_at = datetime.utcnow()
            session.commit()

            variants = session.query(ABTestVariant).filter_by(test_id=test_id).all()
            winner = max(variants, key=lambda v: v.conversion_rate) if variants else None
            return {
                "success": True,
                "winner": winner.to_dict() if winner else None,
            }
        finally:
            session.close()

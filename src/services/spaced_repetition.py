"""
Spaced Repetition Service
Implements SM-2 algorithm for optimized review scheduling
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional
from ..database.db_manager import DatabaseManager


class SpacedRepetitionService:
    """
    Service for managing spaced repetition reviews using the SM-2 algorithm

    The SM-2 algorithm uses:
    - Easiness Factor (EF): Difficulty of the item (starts at 2.5)
    - Repetition Number (n): Number of successful reviews
    - Interval (I): Days until next review
    - Quality (q): User's recall quality (0-5)
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize spaced repetition service

        Args:
            db_manager: Database manager instance
        """
        self.db = db_manager

    def add_topic_for_review(self, user_id: str, topic: str):
        """
        Add a new topic to the review system

        Args:
            user_id: User identifier
            topic: Topic name to review
        """
        self.db.create_review_item(user_id, topic)

    def record_review(self, item_id: int, quality: int) -> Dict:
        """
        Record a review and calculate next review date using SM-2

        Args:
            item_id: Review item ID
            quality: Quality of recall (0-5)
                     5: Perfect recall
                     4: Correct with hesitation
                     3: Correct with difficulty
                     2: Incorrect but familiar
                     1: Incorrect, vague memory
                     0: Complete blackout

        Returns:
            Dictionary with next review date and updated stats
        """
        item = self.db.update_review_item(item_id, quality)

        if not item:
            return {"error": "Item not found"}

        return {
            "topic": item.topic,
            "next_review": item.next_review,
            "interval_days": item.interval_days,
            "easiness_factor": round(item.easiness_factor, 2),
            "repetition_number": item.repetition_number,
            "quality": quality
        }

    def get_due_reviews(self, user_id: str) -> List[Dict]:
        """
        Get all topics due for review

        Args:
            user_id: User identifier

        Returns:
            List of review items that are due
        """
        items = self.db.get_due_reviews(user_id)

        return [{
            "id": item.id,
            "topic": item.topic,
            "due_date": item.next_review,
            "days_overdue": (datetime.utcnow() - item.next_review).days,
            "repetition_number": item.repetition_number,
            "average_quality": round(item.average_quality, 2)
        } for item in items]

    def get_review_schedule(self, user_id: str, days: int = 7) -> Dict:
        """
        Get review schedule for the next N days

        Args:
            user_id: User identifier
            days: Number of days to look ahead

        Returns:
            Dictionary with reviews organized by date
        """
        upcoming = self.db.get_upcoming_reviews(user_id, days)
        due = self.db.get_due_reviews(user_id)

        schedule = {}

        # Add overdue items
        if due:
            schedule["overdue"] = [{
                "id": item.id,
                "topic": item.topic,
                "due_date": item.next_review,
                "days_overdue": (datetime.utcnow() - item.next_review).days
            } for item in due]

        # Group upcoming by date
        for item in upcoming:
            date_key = item.next_review.strftime("%Y-%m-%d")
            if date_key not in schedule:
                schedule[date_key] = []

            schedule[date_key].append({
                "id": item.id,
                "topic": item.topic,
                "repetition_number": item.repetition_number
            })

        return schedule

    def get_review_statistics(self, user_id: str) -> Dict:
        """
        Get comprehensive review statistics for a user

        Args:
            user_id: User identifier

        Returns:
            Dictionary with review stats
        """
        due = self.db.get_due_reviews(user_id)
        upcoming_7 = self.db.get_upcoming_reviews(user_id, days=7)
        upcoming_30 = self.db.get_upcoming_reviews(user_id, days=30)

        return {
            "items_due_now": len(due),
            "items_next_7_days": len(upcoming_7),
            "items_next_30_days": len(upcoming_30),
            "most_urgent": [{
                "topic": item.topic,
                "days_overdue": (datetime.utcnow() - item.next_review).days
            } for item in due[:5]]  # Top 5 most overdue
        }

    def suggest_review_session(self, user_id: str, max_items: int = 10) -> List[Dict]:
        """
        Suggest items for a review session

        Args:
            user_id: User identifier
            max_items: Maximum number of items to review

        Returns:
            List of suggested review items
        """
        # Get due items first, then upcoming within next 2 days
        due = self.db.get_due_reviews(user_id)
        upcoming = self.db.get_upcoming_reviews(user_id, days=2)

        # Combine and sort by urgency
        all_items = due + upcoming
        all_items.sort(key=lambda x: x.next_review)

        # Limit to max_items
        session_items = all_items[:max_items]

        return [{
            "id": item.id,
            "topic": item.topic,
            "next_review": item.next_review,
            "repetition_number": item.repetition_number,
            "easiness_factor": round(item.easiness_factor, 2),
            "is_overdue": item.next_review < datetime.utcnow()
        } for item in session_items]

    @staticmethod
    def calculate_quality_from_performance(
        confidence: float,
        clarity: float,
        had_gaps: bool
    ) -> int:
        """
        Convert teaching performance metrics to SM-2 quality score

        Args:
            confidence: Confidence score (0-1)
            clarity: Clarity score (0-1)
            had_gaps: Whether knowledge gaps were identified

        Returns:
            Quality score (0-5) for SM-2 algorithm
        """
        # Average the two scores
        avg_score = (confidence + clarity) / 2

        # Penalize if gaps were found
        if had_gaps:
            avg_score *= 0.8

        # Convert to 0-5 scale
        if avg_score >= 0.95:
            return 5  # Perfect
        elif avg_score >= 0.85:
            return 4  # Good
        elif avg_score >= 0.70:
            return 3  # Pass
        elif avg_score >= 0.50:
            return 2  # Incorrect but familiar
        elif avg_score >= 0.30:
            return 1  # Vague memory
        else:
            return 0  # Complete failure

    def auto_create_review_from_session(
        self,
        user_id: str,
        topic: str,
        confidence: float,
        clarity: float,
        knowledge_gaps: List[str]
    ):
        """
        Automatically create or update a review item based on teaching session

        Args:
            user_id: User identifier
            topic: Topic taught
            confidence: Confidence score (0-1)
            clarity: Clarity score (0-1)
            knowledge_gaps: List of identified knowledge gaps
        """
        # Create review item if it doesn't exist
        item = self.db.create_review_item(user_id, topic)

        # Calculate quality from performance
        quality = self.calculate_quality_from_performance(
            confidence,
            clarity,
            len(knowledge_gaps) > 0
        )

        # Update the review schedule
        self.db.update_review_item(item.id, quality)

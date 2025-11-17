"""
Database Manager for TeachBack AI
Handles database connections, sessions, and CRUD operations
"""

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import os

from .models import (
    Base, User, Session, Conversation, Analysis,
    KnowledgeNode, KnowledgeEdge, ReviewItem, ProgressMetric
)


class DatabaseManager:
    """
    Manages all database operations for TeachBack AI
    """

    def __init__(self, db_path: str = "teachback.db"):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file
        """
        # Use absolute path
        if not os.path.isabs(db_path):
            db_path = os.path.join(os.getcwd(), db_path)

        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionFactory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.SessionFactory)

        # Create all tables
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # ==================== USER OPERATIONS ====================

    def create_user(self, user_id: str, username: str) -> User:
        """Create a new user"""
        with self.session_scope() as session:
            user = User(id=user_id, username=username)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def get_or_create_user(self, user_id: str, username: str = "default_user") -> User:
        """Get existing user or create new one"""
        with self.session_scope() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if not user:
                user = User(id=user_id, username=username)
                session.add(user)
                session.commit()
                session.refresh(user)
            else:
                user.last_active = datetime.utcnow()
                session.commit()
            return user

    # ==================== SESSION OPERATIONS ====================

    def create_session(
        self,
        session_id: str,
        user_id: str,
        topic: str,
        mode: str,
        voice_enabled: bool = False,
        max_turns: int = 10
    ) -> Session:
        """Create a new teaching session"""
        with self.session_scope() as session:
            teaching_session = Session(
                id=session_id,
                user_id=user_id,
                topic=topic,
                mode=mode,
                voice_enabled=voice_enabled,
                max_turns=max_turns
            )
            session.add(teaching_session)
            session.commit()
            session.refresh(teaching_session)
            return teaching_session

    def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID"""
        with self.session_scope() as session:
            return session.query(Session).filter_by(id=session_id).first()

    def update_session_metrics(
        self,
        session_id: str,
        turn_count: int,
        average_confidence: float,
        average_clarity: float
    ):
        """Update session metrics"""
        with self.session_scope() as session:
            teaching_session = session.query(Session).filter_by(id=session_id).first()
            if teaching_session:
                teaching_session.turn_count = turn_count
                teaching_session.average_confidence = average_confidence
                teaching_session.average_clarity = average_clarity
                teaching_session.updated_at = datetime.utcnow()
                session.commit()

    def complete_session(self, session_id: str, final_confidence: float, final_clarity: float):
        """Mark a session as completed"""
        with self.session_scope() as session:
            teaching_session = session.query(Session).filter_by(id=session_id).first()
            if teaching_session:
                teaching_session.completed_at = datetime.utcnow()
                teaching_session.final_confidence = final_confidence
                teaching_session.final_clarity = final_clarity
                session.commit()

    def get_user_sessions(self, user_id: str, limit: int = 50) -> List[Session]:
        """Get all sessions for a user"""
        with self.session_scope() as session:
            return session.query(Session).filter_by(user_id=user_id)\
                .order_by(Session.created_at.desc())\
                .limit(limit)\
                .all()

    # ==================== CONVERSATION OPERATIONS ====================

    def add_conversation_turn(
        self,
        session_id: str,
        turn_number: int,
        role: str,
        content: str
    ) -> Conversation:
        """Add a conversation turn"""
        with self.session_scope() as session:
            conversation = Conversation(
                session_id=session_id,
                turn_number=turn_number,
                role=role,
                content=content
            )
            session.add(conversation)
            session.commit()
            session.refresh(conversation)
            return conversation

    def get_session_conversations(self, session_id: str) -> List[Conversation]:
        """Get all conversations for a session"""
        with self.session_scope() as session:
            return session.query(Conversation)\
                .filter_by(session_id=session_id)\
                .order_by(Conversation.turn_number)\
                .all()

    # ==================== ANALYSIS OPERATIONS ====================

    def add_analysis(
        self,
        session_id: str,
        turn_number: int,
        confidence_score: float,
        clarity_score: float,
        knowledge_gaps: List[str],
        unexplained_jargon: List[str],
        strengths: List[str]
    ) -> Analysis:
        """Add an analysis result"""
        with self.session_scope() as session:
            analysis = Analysis(
                session_id=session_id,
                turn_number=turn_number,
                confidence_score=confidence_score,
                clarity_score=clarity_score,
                knowledge_gaps=knowledge_gaps,
                unexplained_jargon=unexplained_jargon,
                strengths=strengths
            )
            session.add(analysis)
            session.commit()
            session.refresh(analysis)
            return analysis

    def get_session_analyses(self, session_id: str) -> List[Analysis]:
        """Get all analyses for a session"""
        with self.session_scope() as session:
            return session.query(Analysis)\
                .filter_by(session_id=session_id)\
                .order_by(Analysis.turn_number)\
                .all()

    # ==================== KNOWLEDGE GRAPH OPERATIONS ====================

    def create_or_update_knowledge_node(
        self,
        user_id: str,
        topic: str,
        confidence: float,
        clarity: float,
        related_concepts: List[str] = None,
        gaps: List[str] = None
    ) -> KnowledgeNode:
        """Create or update a knowledge node"""
        with self.session_scope() as session:
            # Check if node exists
            node = session.query(KnowledgeNode)\
                .filter_by(user_id=user_id, topic=topic)\
                .first()

            if node:
                # Update existing node
                node.times_taught += 1
                # Running average
                total_confidence = node.average_confidence * (node.times_taught - 1) + confidence
                total_clarity = node.average_clarity * (node.times_taught - 1) + clarity
                node.average_confidence = total_confidence / node.times_taught
                node.average_clarity = total_clarity / node.times_taught
                node.last_taught = datetime.utcnow()

                # Update related concepts
                if related_concepts:
                    existing = set(node.related_concepts or [])
                    existing.update(related_concepts)
                    node.related_concepts = list(existing)

                # Update persistent gaps
                if gaps:
                    existing_gaps = set(node.persistent_gaps or [])
                    existing_gaps.update(gaps)
                    node.persistent_gaps = list(existing_gaps)
            else:
                # Create new node
                node = KnowledgeNode(
                    user_id=user_id,
                    topic=topic,
                    times_taught=1,
                    average_confidence=confidence,
                    average_clarity=clarity,
                    related_concepts=related_concepts or [],
                    persistent_gaps=gaps or []
                )
                session.add(node)

            session.commit()
            session.refresh(node)
            return node

    def create_knowledge_edge(
        self,
        from_topic: str,
        to_topic: str,
        user_id: str,
        relationship_type: str = "related_to",
        strength: float = 1.0
    ) -> Optional[KnowledgeEdge]:
        """Create an edge between two knowledge nodes"""
        with self.session_scope() as session:
            # Get nodes
            from_node = session.query(KnowledgeNode)\
                .filter_by(user_id=user_id, topic=from_topic)\
                .first()
            to_node = session.query(KnowledgeNode)\
                .filter_by(user_id=user_id, topic=to_topic)\
                .first()

            if not from_node or not to_node:
                return None

            # Check if edge exists
            existing_edge = session.query(KnowledgeEdge)\
                .filter_by(from_node_id=from_node.id, to_node_id=to_node.id)\
                .first()

            if existing_edge:
                # Update strength
                existing_edge.strength = min(existing_edge.strength + 0.1, 2.0)
                session.commit()
                return existing_edge

            # Create new edge
            edge = KnowledgeEdge(
                from_node_id=from_node.id,
                to_node_id=to_node.id,
                relationship_type=relationship_type,
                strength=strength
            )
            session.add(edge)
            session.commit()
            session.refresh(edge)
            return edge

    def get_user_knowledge_graph(self, user_id: str) -> Dict:
        """Get complete knowledge graph for a user"""
        with self.session_scope() as session:
            nodes = session.query(KnowledgeNode).filter_by(user_id=user_id).all()

            graph_data = {
                "nodes": [],
                "edges": []
            }

            # Add nodes
            for node in nodes:
                graph_data["nodes"].append({
                    "id": node.id,
                    "label": node.topic,
                    "times_taught": node.times_taught,
                    "confidence": round(node.average_confidence, 2),
                    "clarity": round(node.average_clarity, 2),
                    "first_taught": node.first_taught.isoformat(),
                    "last_taught": node.last_taught.isoformat(),
                    "gaps": node.persistent_gaps
                })

            # Add edges
            for node in nodes:
                for edge in node.edges_from:
                    graph_data["edges"].append({
                        "from": edge.from_node_id,
                        "to": edge.to_node_id,
                        "type": edge.relationship_type,
                        "strength": edge.strength
                    })

            return graph_data

    # ==================== SPACED REPETITION OPERATIONS ====================

    def create_review_item(self, user_id: str, topic: str) -> ReviewItem:
        """Create a new review item using SM-2 algorithm"""
        with self.session_scope() as session:
            # Check if already exists
            existing = session.query(ReviewItem)\
                .filter_by(user_id=user_id, topic=topic)\
                .first()

            if existing:
                return existing

            # Create new review item
            next_review = datetime.utcnow() + timedelta(days=1)
            item = ReviewItem(
                user_id=user_id,
                topic=topic,
                next_review=next_review
            )
            session.add(item)
            session.commit()
            session.refresh(item)
            return item

    def update_review_item(self, item_id: int, quality: int) -> ReviewItem:
        """
        Update review item after review using SM-2 algorithm

        Args:
            item_id: Review item ID
            quality: Quality of recall (0-5, where 3+ is pass)
        """
        with self.session_scope() as session:
            item = session.query(ReviewItem).filter_by(id=item_id).first()
            if not item:
                return None

            # SM-2 Algorithm
            if quality >= 3:
                # Correct response
                if item.repetition_number == 0:
                    item.interval_days = 1
                elif item.repetition_number == 1:
                    item.interval_days = 6
                else:
                    item.interval_days = int(item.interval_days * item.easiness_factor)

                item.repetition_number += 1
            else:
                # Incorrect response - reset
                item.repetition_number = 0
                item.interval_days = 1

            # Update easiness factor
            item.easiness_factor = max(1.3, item.easiness_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

            # Update review dates
            item.last_reviewed = datetime.utcnow()
            item.next_review = datetime.utcnow() + timedelta(days=item.interval_days)

            # Update stats
            item.review_count += 1
            total_quality = item.average_quality * (item.review_count - 1) + quality
            item.average_quality = total_quality / item.review_count

            session.commit()
            session.refresh(item)
            return item

    def get_due_reviews(self, user_id: str) -> List[ReviewItem]:
        """Get all review items due for review"""
        with self.session_scope() as session:
            now = datetime.utcnow()
            return session.query(ReviewItem)\
                .filter_by(user_id=user_id)\
                .filter(ReviewItem.next_review <= now)\
                .order_by(ReviewItem.next_review)\
                .all()

    def get_upcoming_reviews(self, user_id: str, days: int = 7) -> List[ReviewItem]:
        """Get reviews coming up in the next N days"""
        with self.session_scope() as session:
            now = datetime.utcnow()
            future = now + timedelta(days=days)
            return session.query(ReviewItem)\
                .filter_by(user_id=user_id)\
                .filter(ReviewItem.next_review > now)\
                .filter(ReviewItem.next_review <= future)\
                .order_by(ReviewItem.next_review)\
                .all()

    # ==================== PROGRESS TRACKING ====================

    def update_progress_metrics(self, user_id: str):
        """Update daily progress metrics for a user"""
        with self.session_scope() as session:
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

            # Get or create today's metric
            metric = session.query(ProgressMetric)\
                .filter_by(user_id=user_id, date=today, period_type="daily")\
                .first()

            if not metric:
                metric = ProgressMetric(user_id=user_id, date=today, period_type="daily")
                session.add(metric)

            # Calculate metrics for today
            today_sessions = session.query(Session)\
                .filter_by(user_id=user_id)\
                .filter(Session.created_at >= today)\
                .all()

            if today_sessions:
                metric.sessions_completed = len([s for s in today_sessions if s.completed_at])
                metric.total_turns = sum(s.turn_count for s in today_sessions)

                confidences = [s.average_confidence for s in today_sessions if s.average_confidence > 0]
                clarities = [s.average_clarity for s in today_sessions if s.average_clarity > 0]

                metric.average_confidence = sum(confidences) / len(confidences) if confidences else 0.0
                metric.average_clarity = sum(clarities) / len(clarities) if clarities else 0.0

                metric.unique_topics = len(set(s.topic for s in today_sessions))

            # Calculate streak
            yesterday = today - timedelta(days=1)
            yesterday_metric = session.query(ProgressMetric)\
                .filter_by(user_id=user_id, date=yesterday, period_type="daily")\
                .first()

            if yesterday_metric and yesterday_metric.sessions_completed > 0:
                metric.consecutive_days = yesterday_metric.consecutive_days + 1
            else:
                metric.consecutive_days = 1 if metric.sessions_completed > 0 else 0

            session.commit()

    def get_progress_history(self, user_id: str, days: int = 30) -> List[ProgressMetric]:
        """Get progress metrics for the last N days"""
        with self.session_scope() as session:
            start_date = datetime.utcnow() - timedelta(days=days)
            return session.query(ProgressMetric)\
                .filter_by(user_id=user_id, period_type="daily")\
                .filter(ProgressMetric.date >= start_date)\
                .order_by(ProgressMetric.date)\
                .all()

    def get_user_stats(self, user_id: str) -> Dict:
        """Get comprehensive user statistics"""
        with self.session_scope() as session:
            total_sessions = session.query(func.count(Session.id))\
                .filter_by(user_id=user_id)\
                .scalar()

            completed_sessions = session.query(func.count(Session.id))\
                .filter_by(user_id=user_id)\
                .filter(Session.completed_at.isnot(None))\
                .scalar()

            total_turns = session.query(func.sum(Session.turn_count))\
                .filter_by(user_id=user_id)\
                .scalar() or 0

            avg_confidence = session.query(func.avg(Session.average_confidence))\
                .filter_by(user_id=user_id)\
                .filter(Session.average_confidence > 0)\
                .scalar() or 0.0

            avg_clarity = session.query(func.avg(Session.average_clarity))\
                .filter_by(user_id=user_id)\
                .filter(Session.average_clarity > 0)\
                .scalar() or 0.0

            unique_topics = session.query(func.count(func.distinct(Session.topic)))\
                .filter_by(user_id=user_id)\
                .scalar()

            # Get current streak
            latest_metric = session.query(ProgressMetric)\
                .filter_by(user_id=user_id, period_type="daily")\
                .order_by(ProgressMetric.date.desc())\
                .first()

            current_streak = latest_metric.consecutive_days if latest_metric else 0

            return {
                "total_sessions": total_sessions,
                "completed_sessions": completed_sessions,
                "total_turns": total_turns,
                "average_confidence": round(avg_confidence, 2),
                "average_clarity": round(avg_clarity, 2),
                "unique_topics": unique_topics,
                "current_streak": current_streak
            }

    def cleanup(self):
        """Close database connections"""
        self.Session.remove()
        self.engine.dispose()

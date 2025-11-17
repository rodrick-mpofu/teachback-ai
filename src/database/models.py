"""
Database Models for TeachBack AI
Handles session persistence, progress tracking, and knowledge graphs
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import json

Base = declarative_base()


class User(Base):
    """User model for tracking learners"""
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    knowledge_nodes = relationship("KnowledgeNode", back_populates="user", cascade="all, delete-orphan")
    review_items = relationship("ReviewItem", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id='{self.id}', username='{self.username}')>"


class Session(Base):
    """Teaching session model"""
    __tablename__ = 'sessions'

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    topic = Column(String, nullable=False)
    mode = Column(String, nullable=False)  # socratic, contrarian, five-year-old, anxious
    voice_enabled = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    turn_count = Column(Integer, default=0)
    max_turns = Column(Integer, default=10)

    # Aggregated metrics
    average_confidence = Column(Float, default=0.0)
    average_clarity = Column(Float, default=0.0)
    final_confidence = Column(Float, nullable=True)
    final_clarity = Column(Float, nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    conversations = relationship("Conversation", back_populates="session", cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Session(id='{self.id}', topic='{self.topic}', mode='{self.mode}')>"


class Conversation(Base):
    """Individual conversation turn within a session"""
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.id'), nullable=False)
    turn_number = Column(Integer, nullable=False)
    role = Column(String, nullable=False)  # 'teacher' or 'student'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="conversations")

    def __repr__(self):
        return f"<Conversation(session_id='{self.session_id}', turn={self.turn_number}, role='{self.role}')>"


class Analysis(Base):
    """Analysis results for each teacher explanation"""
    __tablename__ = 'analyses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey('sessions.id'), nullable=False)
    turn_number = Column(Integer, nullable=False)

    confidence_score = Column(Float, nullable=False)
    clarity_score = Column(Float, nullable=False)

    knowledge_gaps = Column(JSON, default=list)  # List of gap strings
    unexplained_jargon = Column(JSON, default=list)  # List of jargon terms
    strengths = Column(JSON, default=list)  # List of strength descriptions

    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    session = relationship("Session", back_populates="analyses")

    def __repr__(self):
        return f"<Analysis(session_id='{self.session_id}', turn={self.turn_number}, confidence={self.confidence_score})>"


class KnowledgeNode(Base):
    """Nodes in the knowledge graph representing concepts"""
    __tablename__ = 'knowledge_nodes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    topic = Column(String, nullable=False, index=True)

    # Knowledge tracking
    times_taught = Column(Integer, default=1)
    average_confidence = Column(Float, default=0.0)
    average_clarity = Column(Float, default=0.0)

    # Metadata
    first_taught = Column(DateTime, default=datetime.utcnow)
    last_taught = Column(DateTime, default=datetime.utcnow)

    # Related concepts (stored as JSON list of strings)
    related_concepts = Column(JSON, default=list)

    # Persistent knowledge gaps
    persistent_gaps = Column(JSON, default=list)

    # Relationships
    user = relationship("User", back_populates="knowledge_nodes")
    edges_from = relationship("KnowledgeEdge", foreign_keys="KnowledgeEdge.from_node_id",
                              back_populates="from_node", cascade="all, delete-orphan")
    edges_to = relationship("KnowledgeEdge", foreign_keys="KnowledgeEdge.to_node_id",
                           back_populates="to_node", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<KnowledgeNode(id={self.id}, topic='{self.topic}', times_taught={self.times_taught})>"


class KnowledgeEdge(Base):
    """Edges in the knowledge graph representing relationships between concepts"""
    __tablename__ = 'knowledge_edges'

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_node_id = Column(Integer, ForeignKey('knowledge_nodes.id'), nullable=False)
    to_node_id = Column(Integer, ForeignKey('knowledge_nodes.id'), nullable=False)

    relationship_type = Column(String, default="related_to")  # e.g., "prerequisite", "related_to", "part_of"
    strength = Column(Float, default=1.0)  # How strong the connection is

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    from_node = relationship("KnowledgeNode", foreign_keys=[from_node_id], back_populates="edges_from")
    to_node = relationship("KnowledgeNode", foreign_keys=[to_node_id], back_populates="edges_to")

    def __repr__(self):
        return f"<KnowledgeEdge(from={self.from_node_id}, to={self.to_node_id}, type='{self.relationship_type}')>"


class ReviewItem(Base):
    """Spaced repetition review items"""
    __tablename__ = 'review_items'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    topic = Column(String, nullable=False)

    # SM-2 Algorithm parameters
    easiness_factor = Column(Float, default=2.5)  # EF, starts at 2.5
    repetition_number = Column(Integer, default=0)  # n
    interval_days = Column(Integer, default=1)  # I(n)

    # Review scheduling
    last_reviewed = Column(DateTime, nullable=True)
    next_review = Column(DateTime, nullable=False)

    # Performance tracking
    review_count = Column(Integer, default=0)
    average_quality = Column(Float, default=0.0)  # Average quality score (0-5)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="review_items")

    def __repr__(self):
        return f"<ReviewItem(topic='{self.topic}', next_review='{self.next_review}', EF={self.easiness_factor})>"


class ProgressMetric(Base):
    """Daily/weekly aggregated progress metrics"""
    __tablename__ = 'progress_metrics'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)

    date = Column(DateTime, nullable=False, index=True)
    period_type = Column(String, default="daily")  # daily, weekly, monthly

    # Metrics
    sessions_completed = Column(Integer, default=0)
    total_turns = Column(Integer, default=0)
    average_confidence = Column(Float, default=0.0)
    average_clarity = Column(Float, default=0.0)
    unique_topics = Column(Integer, default=0)

    # Streak tracking
    consecutive_days = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<ProgressMetric(date='{self.date}', sessions={self.sessions_completed})>"

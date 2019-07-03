"""ORM model for relations service."""

from sqlalchemy import Column, DateTime, Enum, Integer, String, Text, Boolean
from flask_sqlalchemy import SQLAlchemy, Model
from relations.domain import RelationType

db: SQLAlchemy = SQLAlchemy()


class RelationDB(db.Model):
    """Model for relations."""

    __tablename__ = 'relations'
    id = Column(Integer, primary_key=True)
    rel_type = Column(Enum(RelationType))
    arxiv_id = Column(String(255))
    arxiv_ver = Column(Integer)
    resource_type = Column(String(255))
    resource_id = Column(String(255))
    description = Column(Text(1024))
    added_at = Column(DateTime)
    creator = Column(String(255), nullable=True)
    supercedes_or_suppresses = Column(Integer, nullable=True)


class ActivationDB(db.Model):
    """Model for relations."""

    __tablename__ = 'active_records'
    id = Column(Integer, primary_key=True)
    active = Column(Boolean)

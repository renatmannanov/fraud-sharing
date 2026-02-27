import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, Boolean, Integer, DateTime, ForeignKey, Text,
    UniqueConstraint, Index,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class Candidate(Base):
    """
    Unique candidate identified by hashes.
    No PII stored — only hashes and random UUID.
    """
    __tablename__ = "candidates"

    uid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Hashes — multiple keys for matching
    hh_id_hash = Column(String, unique=True, nullable=True, index=True)
    phone_hash = Column(String, nullable=True, index=True)
    email_hash = Column(String, nullable=True, index=True)
    name_dob_hash = Column(String, nullable=True, index=True)       # firstname + dob
    fullname_dob_hash = Column(String, nullable=True, index=True)   # firstname + lastname + dob

    needs_review = Column(Boolean, default=False)

    # Consent tracking
    consent_obtained = Column(Boolean, default=False)
    consent_source = Column(String, nullable=True)  # "candidate_direct", "agency_agreement", etc.

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sources = relationship("CandidateSource", back_populates="candidate")


class CandidateSource(Base):
    """
    One fact from one source about one company.
    Each row = "source X says candidate worked/didn't work at company Y".
    """
    __tablename__ = "candidate_sources"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(UUID(as_uuid=True), ForeignKey("candidates.uid"), nullable=False)

    source_id = Column(String, nullable=False)    # "estaff_test", "agency_excel", "company_indrive"
    source_type = Column(String, nullable=False)   # "candidate", "agency", "company"
    claim_type = Column(String, nullable=False, default="worked_here")  # "worked_here", "never_worked"
    client_uid = Column(String, nullable=True)     # candidate ID in client's system

    # Work history claim
    company = Column(String, nullable=True)        # normalized company name
    position = Column(String, nullable=True)
    worked_from = Column(String, nullable=True)    # "2019-03" or "2019-03-01"
    worked_to = Column(String, nullable=True)      # same format, NULL = currently employed

    added_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    candidate = relationship("Candidate", back_populates="sources")

    __table_args__ = (
        UniqueConstraint("source_id", "client_uid", "company", name="uq_source_client_company"),
        Index("idx_sources_uid", "uid"),
        Index("idx_sources_source_id", "source_id"),
        Index("idx_sources_company", "company"),
    )


class ApiKey(Base):
    """API keys for client authentication."""
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String, unique=True, nullable=False)
    key_hash = Column(String, nullable=False)
    rate_limit = Column(Integer, default=100)  # requests per hour
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """
    Who did what and when. No PII in this table!
    Only source_id, action type, and candidate UIDs.
    """
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String, nullable=False)
    action = Column(String, nullable=False)  # "ingest", "verify", "match"
    candidate_uid = Column(UUID(as_uuid=True), nullable=True)
    details = Column(Text, nullable=True)  # JSON with non-PII metadata
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

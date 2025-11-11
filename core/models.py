from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum
from datetime import datetime
import pytz
from core.db import Base

# ---- IST TIME (naive for MySQL) ----
IST = pytz.timezone("Asia/Kolkata")
def now_ist_naive():
    # MySQL doesn't support tz-aware datetimes well; store IST clock time without tzinfo
    return datetime.now(IST).replace(tzinfo=None)

class RoleEnum(str, enum.Enum):
    BESS = "BESS"
    EPC = "EPC"
    ADMIN = "ADMIN"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    role = Column(Enum(RoleEnum), nullable=False)
    password_hash = Column(String(255), nullable=False)

    proposals = relationship("Proposal", back_populates="creator")

class Proposal(Base):
    __tablename__ = "proposals"
    id = Column(Integer, primary_key=True)
    reference_no = Column(String(100), index=True, unique=True, nullable=False)
    template_type = Column(String(50), nullable=False)  # "EPC" or "BESS"
    created_at = Column(DateTime, default=now_ist_naive, nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"))
    meta = Column(JSON, nullable=True)

    creator = relationship("User", back_populates="proposals")
    logs = relationship("ProposalLog", back_populates="proposal")

class ProposalLog(Base):
    __tablename__ = "proposal_logs"
    id = Column(Integer, primary_key=True)
    proposal_id = Column(Integer, ForeignKey("proposals.id"), index=True)
    reference_no = Column(String(100), index=True)
    level = Column(String(20), default="INFO")
    message = Column(Text)
    at = Column(DateTime, default=now_ist_naive, index=True, nullable=False)
    extra = Column(JSON, nullable=True)

    proposal = relationship("Proposal", back_populates="logs")

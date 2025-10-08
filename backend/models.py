from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Index, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from backend.db import Base


class History(Base):
    """
    stores analysis history for bias emotion and debate sessions
    """
    __tablename__ = "history"

    # primary key
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # text content being analyzed
    text = Column(Text, nullable=False)
    
    # analyze or debate mode
    mode = Column(
        String(20),
        nullable=False,
        index=True
    )
    
    # analysis results as jsonb for fast queries
    results = Column(JSONB, nullable=False, default=dict)
    
    # when record was created
    created_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    
    # last update time
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    __table_args__ = (
        # composite index for mode and date queries
        Index('ix_history_mode_created', 'mode', 'created_at'),
        
        # only allow valid modes
        CheckConstraint(
            "mode IN ('analyze', 'debate')",
            name='check_valid_mode'
        ),
        
        # text cant be empty
        CheckConstraint(
            "length(text) > 0",
            name='check_text_not_empty'
        ),
    )
    
    def __repr__(self):
        """debug representation"""
        return (
            f"<History(id={self.id}, mode='{self.mode}', "
            f"created_at={self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None})>"
        )
    
    def __str__(self):
        """readable string"""
        text_preview = self.text[:50] + "..." if len(self.text) > 50 else self.text
        return f"History #{self.id} - {self.mode}: {text_preview}"
    
    def to_dict(self):
        """convert to dict for json response"""
        return {
            "id": self.id,
            "text": self.text,
            "mode": self.mode,
            "results": self.results,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

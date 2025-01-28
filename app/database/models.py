from sqlalchemy import Column, String, DateTime, Float, Boolean, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    plan_type = Column(String)
    stripe_customer_id = Column(String)

class APIKey(Base):
    __tablename__ = 'api_keys'
    key_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    api_key = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)

class Sample(Base):
    __tablename__ = 'samples'
    sample_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.user_id'))
    timestamp = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    altitude = Column(Float)
    location_type = Column(String)
    temperature = Column(Float)
    humidity = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class MicrobiomeAnalysis(Base):
    __tablename__ = 'microbiome_analysis'
    analysis_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sample_id = Column(UUID(as_uuid=True), ForeignKey('samples.sample_id'))
    biodiversity_index = Column(Float)
    dominant_species = Column(JSON)
    health_indicators = Column(JSON)
    recommendations = Column(ARRAY(String))
    external_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
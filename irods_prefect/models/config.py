"""
Configuration models for the irods_prefect package.
"""
from typing import Dict, List, Optional, Union
from pydantic import BaseModel, Field, validator


class iRODSConfig(BaseModel):
    """Configuration for iRODS connection."""
    host: str = Field(..., description="iRODS host")
    port: int = Field(1247, description="iRODS port")
    user: str = Field(..., description="iRODS user")
    password: str = Field(..., description="iRODS password")
    zone: str = Field(..., description="iRODS zone")
    default_resource: Optional[str] = Field(None, description="Default resource")
    
    class Config:
        env_prefix = "IRODS_"


class PrefectConfig(BaseModel):
    """Configuration for Prefect."""
    api_url: Optional[str] = Field(None, description="Prefect API URL")
    api_key: Optional[str] = Field(None, description="Prefect API key")
    
    class Config:
        env_prefix = "PREFECT_"


class NotificationConfig(BaseModel):
    """Configuration for notifications."""
    email_enabled: bool = Field(False, description="Enable email notifications")
    email_smtp_server: Optional[str] = Field(None, description="SMTP server")
    email_smtp_port: Optional[int] = Field(None, description="SMTP port")
    email_username: Optional[str] = Field(None, description="SMTP username")
    email_password: Optional[str] = Field(None, description="SMTP password")
    email_from: Optional[str] = Field(None, description="From email address")
    email_to: Optional[List[str]] = Field(None, description="To email addresses")
    
    slack_enabled: bool = Field(False, description="Enable Slack notifications")
    slack_webhook_url: Optional[str] = Field(None, description="Slack webhook URL")
    
    class Config:
        env_prefix = "NOTIFICATION_"


class SequencerConfig(BaseModel):
    """Configuration for sequencer data."""
    base_dir: str = Field(..., description="Base directory for sequencer data")
    completion_indicator: str = Field("RTAComplete.txt", description="File indicating run completion")
    
    class Config:
        env_prefix = "SEQUENCER_"


class APIConfig(BaseModel):
    """Configuration for the API."""
    host: str = Field("0.0.0.0", description="API host")
    port: int = Field(8000, description="API port")
    debug: bool = Field(False, description="Enable debug mode")
    
    class Config:
        env_prefix = "API_"


class AppConfig(BaseModel):
    """Main application configuration."""
    irods: iRODSConfig
    prefect: PrefectConfig = PrefectConfig()
    notification: NotificationConfig = NotificationConfig()
    sequencer: SequencerConfig
    api: APIConfig = APIConfig()

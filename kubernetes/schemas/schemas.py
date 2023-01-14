from typing import List, Optional
from json import dumps, loads
from pydantic import BaseModel, Field
from kubernetes.utils import (
    get_date,
    get_id,
    get_name,
    get_password,
    get_port,
    get_host,
)


class DataStoreSchema(BaseModel):
    image: str = Field(...)
    protocol: str = Field(default="tcp")
    name: str = Field(default_factory=get_name)
    host: str = Field(default_factory=get_host)
    host_port: int = Field(default_factory=get_port)
    username: str = Field(default_factory=get_name)
    password: str = Field(default_factory=get_password)
    database: Optional[str] = Field(default_factory=get_name)
    container_id: Optional[str] = Field(default=None)
    database_uri: Optional[str] = Field(default=None)
    container_port: Optional[int] = Field(default=None)
    owner: Optional[str] = Field(default=None)


class UserSchema(BaseModel):
    sub: str = Field(...)
    name: str = Field(...)
    email: Optional[str] = Field(default=None)
    picture: Optional[str] = Field(default=None)
    nickname: Optional[str] = Field(default=None)
    updated_at: Optional[str] = Field(default_factory=get_date)
    email_verified: Optional[bool] = Field(default=False)
    given_name: Optional[str] = Field(default=None)
    family_name: Optional[str] = Field(default=None)
    locale: Optional[str] = Field(default=None)


class IssueSchema(BaseModel):
    title: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    status: Optional[str] = Field(default="open")
    labels: Optional[List[str]] = Field(default=[])
    completed: Optional[bool] = Field(default=False)
    project: Optional[str] = Field(default=None)
    last_modified: Optional[str] = Field(default_factory=get_date)
    owner: Optional[str] = Field(default=None)


class CodeFileSchema(BaseModel):
    name: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)
    project: Optional[str] = Field(default=None)
    last_modified: Optional[str] = Field(default_factory=get_date)
    url: Optional[str] = Field(default=None)
    icon: Optional[str] = Field(default=None)
    content_type: Optional[str] = Field(default=None)
    size: Optional[float] = Field(default=None)
    extension: Optional[str] = Field(default=None)
    owner: Optional[str] = Field(default=None)


class ProjectSchema(BaseModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    last_modified: Optional[str] = Field(default_factory=get_date)
    code_files: Optional[List[CodeFileSchema]] = Field(default_factory=list)
    issues: Optional[List[IssueSchema]] = Field(default_factory=list)
    owner: Optional[str] = Field(default=None)


class MicroServiceSchema(BaseModel):
    name: Optional[str] = Field(default=None)
    runtime: Optional[str] = Field(default=None)
    code: Optional[List[CodeFileSchema]] = Field(default_factory=list)
    zip: Optional[bytes] = Field(default=None)
    zip_url: Optional[str] = Field(default=None)
    function_name: Optional[str] = Field(default=None)
    function_url: Optional[str] = Field(default=None)
    function_id: Optional[str] = Field(default_factory=get_id)
    function_arn: Optional[str] = Field(default=None)
    owner: Optional[str] = Field(default=None)

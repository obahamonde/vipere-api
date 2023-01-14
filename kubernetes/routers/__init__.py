from kubernetes.routers.codefiles import CodeFileResource
from kubernetes.routers.issues import IssueResource
from kubernetes.routers.projects import ProjectResource
from kubernetes.routers.users import UserResource, SearchResource, MetricsResource
from kubernetes.routers.microservices import MicroServiceResource
from kubernetes.routers.datastores import DataStoreResource
from fastapi import APIRouter

routers = [
    CodeFileResource(),
    IssueResource(),
    ProjectResource(),
    UserResource(),
    MicroServiceResource(),
    DataStoreResource(),
    SearchResource(),
    MetricsResource(),
]


class Router(APIRouter):
    def __init__(self):
        super().__init__()
        for router in routers:
            self.include_router(router, prefix="/api", tags=[router.prefix])

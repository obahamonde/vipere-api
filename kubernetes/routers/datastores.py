from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from kubernetes.services.docker import DockerService
from kubernetes.schemas.models import DataStore, engine


class DataStoreResource(APIRouter):
    """Database as a Service"""
    def __init__(self):
        super().__init__()
        self.prefix = "/datastores"

        @self.get("/")
        async def index():
            return await engine.find(DataStore)

        @self.get("/")
        async def list_(sub: str):
            return await engine.find(DataStore, DataStore.owner == sub)

        @self.post("/{image}")
        async def create(image: str, sub: str):
            data = await DockerService(image=image).run()
            data_store = DataStore(**data.dict())
            data_store.owner = sub
            return await engine.save(data_store)

        @self.get("/{name}")
        async def read(name: str):
            return await DockerService.get(name=name)

        @self.delete("/{name}")
        async def delete(name: str):
            datastore = await engine.find_one(DataStore, DataStore.name == name)
            await DockerService.delete(name=name)
            return await engine.delete(datastore)

        @self.get("/logs/{name}")
        async def logs(name: str):
            data = await DockerService.logs(name=name)
            return PlainTextResponse(data)

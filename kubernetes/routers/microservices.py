from json import loads
from fastapi import APIRouter, Body, HTTPException
from odmantic import ObjectId
from kubernetes.schemas.models import MicroService, engine
from kubernetes.schemas.schemas import MicroServiceSchema
from kubernetes.services.aws import create_microservice


class MicroServiceResource(APIRouter):
    def __init__(self):
        super().__init__()
        self.prefix = "/microservices"

        @self.post("/")
        async def deploy_microservice(microservice=Body(...)):
            payload = loads(microservice)
            microservice = MicroServiceSchema(**payload)
            if await engine.find_one(
                MicroService, MicroService.name == microservice.name
            ):
                raise HTTPException(
                    status_code=400, detail="Microservice name already exists"
                )
            function_data = await create_microservice(
                microservice.name, microservice.code
            )
            microservice.function_arn = function_data["function_arn"]
            microservice.function_name = function_data["function_name"]
            microservice.function_url = function_data["function_url"]
            microservice_in_db = MicroService(**microservice.dict())
            return await engine.save(microservice_in_db)

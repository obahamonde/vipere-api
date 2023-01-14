from fastapi import APIRouter, Body
from fastapi.responses import PlainTextResponse
from json import loads
from datetime import datetime, timedelta
from kubernetes.schemas.models import User, engine
from kubernetes.schemas.schemas import UserSchema
from kubernetes.services.api import github_search, google_search, complete, pypi_search
from kubernetes.services.aws import get_cloudtrail_data, TimeFrame, get_cloudwatch_data


class UserResource(APIRouter):
    def __init__(self):
        super().__init__()
        self.prefix = "/users"

        @self.post("/")
        async def create(user=Body(...)):
            user_schema = UserSchema(**loads(user))
            user_in_db = await engine.find_one(User, User.sub == user_schema.sub)
            if user_in_db:
                return user_in_db.json()
            return await engine.save(User(**user_schema.dict()))


class SearchResource(APIRouter):
    def __init__(self):
        super().__init__()
        self.prefix = "/search"

        @self.get("/google/{query}")
        async def google(query: str):
            return await google_search(query)

        @self.get("/github/{query}")
        async def github(query: str):
            return await github_search(query)

        @self.get("/complete/")
        async def completion_():
            return PlainTextResponse(
                """
            """
            )
        
        @self.get("/complete/{query}")
        async def completion(query: str):
            print(query)
            return PlainTextResponse(
                await complete(
                    """
            You are an enhanced version of github copilot, your job is to suggest the best piece of code
            possible to autocomplete the code being written by the user, now to prove your worth, you must do your best
            to give the best autocompletion for the following code, without comments or explanations, just the code:
            
            """
                    + query
                    + "\n"
                )
            )

        @self.get("/pypi/{query}")
        async def pypi(query: str):
            return await pypi_search(query)


class MetricsResource(APIRouter):
    def __init__(self):
        super().__init__()
        self.prefix = "/metrics"

        @self.get("/cloudtrail/{timeframe}")
        async def metrics(name: str, timeframe: TimeFrame):
            return await get_cloudtrail_data(name, timeframe)

        @self.get("/cloudwatch/{timeframe}")
        async def cw_metrics(name: str, timeframe: TimeFrame):
            response = await get_cloudwatch_data(name, timeframe)
            return response
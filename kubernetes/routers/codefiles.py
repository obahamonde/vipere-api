"""CodeFile Resource"""
from json import loads
from fastapi import APIRouter, Body, HTTPException
from odmantic import ObjectId
from kubernetes.schemas.models import CodeFile, engine
from kubernetes.schemas.schemas import CodeFileSchema


class CodeFileResource(APIRouter):
    """IDE as a Service"""
    def __init__(self):
        super().__init__()
        self.prefix = "/codefiles"

        @self.get("/")
        async def index(sub: str):
            return await engine.find(CodeFile, CodeFile.owner == sub)

        @self.post("/")
        async def create(sub: str, codefile=Body(...)):
            codefile_schema = CodeFileSchema(**loads(codefile))
            codefile_schema.owner = sub
            codefile_in_db = await engine.find(CodeFile, CodeFile.owner == sub)
            for codefile in codefile_in_db:
                if codefile.name == codefile_schema.name:
                    response = codefile
                    for key, value in codefile_schema.dict().items():
                        setattr(response, key, value)
                    await engine.save(response)
                    break
            else:
                response = await engine.save(CodeFile(**codefile_schema.dict()))
            return response

        @self.delete("/{id}")
        async def delete(sub: str, id: str):
            try:
                codefile = await engine.find_one(CodeFile, CodeFile.id == ObjectId(id))
                if codefile.owner != sub:
                    raise HTTPException(status_code=403, detail="Forbidden")
                await engine.delete(codefile)
            except Exception as exc:
                raise HTTPException(status_code=500, detail=str(exc)) from exc

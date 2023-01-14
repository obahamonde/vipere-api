from fastapi import APIRouter, HTTPException, Body
from odmantic import ObjectId
from kubernetes.schemas.models import Issue, engine
from kubernetes.schemas.schemas import IssueSchema, loads


class IssueResource(APIRouter):
    """Issues Resource
    """

    def __init__(self):
        super().__init__()
        self.prefix = "/issues"

        @self.get("/")
        async def list_all_issues():
            return await engine.find(Issue)

        @self.get("/{sub}")
        async def list_issues_by_subscriptor(sub: str):
            return await engine.find(Issue, Issue.owner == sub)

        @self.post("/")
        async def create_issue_instance(issue=Body(...)):
            issue_schema = IssueSchema(**loads(issue))
            return await engine.save(Issue(**issue_schema.dict()))

        @self.put("/")
        async def update_issue_by_id(id: str, body=Body(...)):
            try:
                issue = IssueSchema(**loads(body))
                issue_db = await engine.find_one(Issue, Issue.id == ObjectId(id))
                for key, value in issue.dict().items():
                    setattr(issue_db, key, value)
                return await engine.save(issue_db)
            except Exception as exc:
                raise HTTPException(status_code=500, detail=str(exc)) from exc

        @self.delete("/")
        async def delete_issue_by_id(id: str):
            try:
                issue = await engine.find_one(Issue, Issue.id == ObjectId(id))
                await engine.delete(issue)
            except Exception as exc:
                raise HTTPException(status_code=500, detail=str(exc)) from exc
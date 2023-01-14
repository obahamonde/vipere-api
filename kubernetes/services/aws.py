"""AWS services"""
import os
import subprocess
from typing import List, Dict, Any
from datetime import datetime, timedelta
from json import loads
from enum import Enum
from aioboto3 import Session
from kubernetes.config import process
from kubernetes.schemas.models import CodeFile
from yaml import safe_load

class TimeFrame(str, Enum):
    """Time frame"""

    DAY = "day"
    WEEK = "week"
    HOUR = "hour"


session = Session(
    aws_access_key_id=process.env.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=process.env.AWS_SECRET_ACCESS_KEY,
    region_name=process.env.AWS_DEFAULT_REGION,
)


async def create_microservice(name: str, codefiles: List[CodeFile]) -> Dict[str, Any]:
    """Create a microservice"""
    subprocess.run(["rm", "-rf", "code/*"], check=True)
    for f in codefiles:
        with open(f"code/{f.name}", "w", encoding="utf-8") as file:
            file.write(f.content)
    for root, _, files in os.walk("code"):
        for file in files:
            if file.endswith("requirements.txt"):
                subprocess.run(
                    ["pip", "install", "-r", "requirements.txt", "-t", "."],
                    cwd=root,
                    check=True,
                )
    subprocess.run(["zip", "-r", "app.zip", "."], cwd=root, check=True)
    async with session.client("lambda") as lambda_:
        response = await lambda_.create_function(
            FunctionName=name,
            Runtime="python3.8",
            Role=process.env.AWS_LAMBDA_ROLE,
            Handler="app.handler",
            Code={"ZipFile": open("code/app.zip", "rb").read()},
            Timeout=16,
            MemorySize=256,
            Publish=True,
        )
        url = await lambda_.create_function_url_config(
            FunctionName=response["FunctionName"],
            AuthType="NONE",
            Cors={
                "AllowOrigins": ["*"],
                "AllowMethods": ["*"],
                "AllowHeaders": ["*"],
                "AllowCredentials": True,
                "ExposeHeaders": ["*"],
                "MaxAge": 86400,
            },
        )
        await lambda_.add_permission(
            FunctionName=response["FunctionName"],
            StatementId=name,
            Action="lambda:InvokeFunctionUrl",
            Principal="*",
            FunctionUrlAuthType="NONE",
        )
        return {
            "function_name": response["FunctionName"],
            "function_arn": response["FunctionArn"],
            "function_url": url["FunctionUrl"],
        }


async def get_cloudtrail_data(name: str, time_frame: TimeFrame) -> Dict[str, Any]:
    """Get log data"""
    async with session.client("cloudtrail") as cloudtrail:
        if time_frame == TimeFrame.HOUR:
            start_time = datetime.utcnow() - timedelta(hours=1)
        elif time_frame == TimeFrame.DAY:
            start_time = datetime.utcnow() - timedelta(days=1)
        elif time_frame == TimeFrame.WEEK:
            start_time = datetime.utcnow() - timedelta(days=7)
        else:
            start_time = datetime.utcnow() - timedelta(days=1)
        response = await cloudtrail.lookup_events(
            StartTime=start_time,
            EndTime=datetime.utcnow(),
            LookupAttributes=[{"AttributeKey": "ResourceName", "AttributeValue": name}],
        )
        responses = []
        for event in response["Events"]:
            responses.append(loads(event["CloudTrailEvent"]))
        return {"count": len(responses), "events": responses}

async def get_cloudwatch_data(name: str, time_frame: TimeFrame) -> Dict[str, Any]:
    """Get log data"""
    async with session.client("logs") as logs:
        if time_frame == TimeFrame.HOUR:
            start_time = datetime.utcnow() - timedelta(hours=1)
        elif time_frame == TimeFrame.DAY:
            start_time = datetime.utcnow() - timedelta(days=1)
        elif time_frame == TimeFrame.WEEK:
            start_time = datetime.utcnow() - timedelta(days=7)
        else:
            start_time = datetime.utcnow() - timedelta(days=1)
        response = await logs.filter_log_events(
            logGroupName=f"/aws/lambda/{name}",
            startTime=int(start_time.timestamp() * 1000),
            endTime=int(datetime.utcnow().timestamp() * 1000)
        )
        responses = [e["message"].strip().split("\t") for e in response["events"]]
        for index, _list in enumerate(responses):
            responses.append(responses.pop(index)[1])
from __future__ import annotations
from aiohttp import ClientSession
from typing import List
from json import loads
from bs4 import BeautifulSoup
from kubernetes.config import process


class env:
    OPENAI_API_TOKEN = process.env.OPENAI_API_KEY
    GITHUB_TOKEN = process.env.GITHUB_TOKEN
    BROWSER_HEADERS = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    }
    OPENAI_HEADERS = {"Authorization": f"Bearer {OPENAI_API_TOKEN}"}
    GITHUB_HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"}
    OPENAI_BASE_URL = "https://api.openai.com/v1/completions"
    GITHUB_BASE_URL = "https://api.github.com"
    GOOGLE_BASE_URL = "https://www.google.com/search?q="


async def complete(
    prompt: str,
    model: str = "text-davinci-003",
    max_tokens: int = 64,
    temperature: float = 1,
    top_p: float = 0.9,
    n: int = 1,
) -> str:
    async with ClientSession(headers=env.OPENAI_HEADERS) as session:
        async with session.post(
            env.OPENAI_BASE_URL,
            json={
                "prompt": prompt,
                "model": model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "n": n,
            },
        ) as response:
            json_response = await response.json()
            return json_response["choices"][0]["text"].strip()


async def github_search(
    query: str,
    sort: str = "stars",
    order: str = "desc",
    per_page: int = 100,
    page: int = 1,
) -> List[dict]:
    async with ClientSession(headers=env.GITHUB_HEADERS) as session:
        async with session.get(
            f"{env.GITHUB_BASE_URL}/search/repositories?q={query}&sort={sort}&order={order}&per_page={per_page}&page={page}"
        ) as response:
            return loads(await response.text())["items"]


async def google_search(query: str) -> List[dict]:
    async with ClientSession(headers=env.BROWSER_HEADERS) as session:
        async with session.get(f"{env.GOOGLE_BASE_URL}{query}") as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
            domels = soup.find_all("div", {"class": "yuRUbf"})
            return [
                {"title": d.find("h3").text, "url": d.find("a")["href"]} for d in domels
            ]


async def pypi_search(query: str) -> List[dict]:
    async with ClientSession(headers=env.BROWSER_HEADERS) as session:
        async with session.get(f"https://pypi.org/search/?q={query}") as response:
            soup = BeautifulSoup(await response.text(), "html.parser")
            domels = soup.find_all("a", {"class": "package-snippet"})
            return [
                {
                    "name": d.find("span", {"class": "package-snippet__name"}).text,
                    "url": f"https://pypi.org{d['href']}",
                    "version": d.find(
                        "span", {"class": "package-snippet__version"}
                    ).text,
                    "description": d.find("p").text,
                }
                for d in domels
            ]

import asyncio
from typing import Any
from httpx import AsyncClient
import httpx
import redis
import json

from .models import GroupInfo, Speciality


class SiteParser:
    client: httpx.AsyncClient

    def __init__(self):
        self.client = httpx.AsyncClient(follow_redirects=True)

    @staticmethod
    def headers() -> dict:
        return {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 YaBrowser/20.12.1.179 Yowser/2.5 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://almetpt.ru",
            "Referrer": "https://almetpt.ru",
        }

    @staticmethod
    def urlencoded_headers() -> dict:
        data = SiteParser.headers()
        data.update(
            [("Content-Type", "application/x-www-form-urlencoded; charset=UTF-8")]
        )
        return data

    async def get_group_info(self, group_id: int) -> GroupInfo | None:
        resp = await self.client.post(
            "https://almetpt.ru/2020/abit/abitGroup",
            data={"group": group_id},
            headers=self.urlencoded_headers(),
        )
        return GroupInfo.read(resp.json())

    async def get_groups_info_cached(
        self, redis_conn: redis.Redis, groups: list[int]
    ) -> list[GroupInfo | None]:
        return await asyncio.gather(
            *[self.get_cached_group_info(redis_conn, i) for i in groups]
        )

    async def get_cached_group_info(
        self, redis_conn: redis.Redis, group_id: int
    ) -> GroupInfo | None:
        key = f"group-{group_id}"
        value: str | None = redis_conn.get(key)  # type: ignore
        if value is None:
            res = await self.get_group_info(group_id)
            if res is not None:
                redis_conn.set(key, json.dumps(res.model_dump(mode="json")), ex=15)
            return res
        data = json.loads(value)
        return GroupInfo(**data)

    async def get_cached_groups(self, redis_conn: redis.Redis) -> list[Speciality]:
        value: str | None = redis_conn.get("groups")  # type: ignore
        if value is None:
            res = await self.get_groups()
            if len(res) > 0:
                data = [i.model_dump(mode="json") for i in res]
                redis_conn.set("groups", json.dumps(data), ex=60)
            return res
        data: list[dict] = json.loads(value)
        return [Speciality(**i) for i in data]

    async def get_groups(self) -> list[Speciality]:
        resp = await self.client.post(
            "https://almetpt.ru/2020/json/abitgroups",
            json={"search": ""},
            headers=self.headers(),
        )
        resp.raise_for_status()
        groups: dict[str, Any] = resp.json()["groups"]
        needed_group_ids: list[int] = (
            groups["dep_0_study_Бюджет"] + groups["dep_0_study_Внебюджет"]
        )
        filtered_groups: list[dict] = list(
            filter(lambda x: isinstance(x, dict), map(lambda x: x[1], groups.items()))
        )
        return list(
            filter(
                lambda x: x is not None and x.id in needed_group_ids,
                map(lambda x: Speciality.read(x), filtered_groups),
            )
        )  # type: ignore

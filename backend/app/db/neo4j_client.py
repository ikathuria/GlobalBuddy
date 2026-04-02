"""Async Neo4j AuraDB client — records are normalized to plain dicts only."""

from collections.abc import Mapping
from typing import Any

from neo4j import AsyncDriver, AsyncGraphDatabase, RoutingControl


def _record_to_dict(record: Any) -> dict[str, Any]:
    return dict(record.data())


class Neo4jClient:
    """Thin async wrapper around the Neo4j Python driver."""

    def __init__(
        self,
        uri: str,
        user: str,
        password: str,
        database: str | None = None,
    ) -> None:
        self._uri = uri
        self._user = user
        self._password = password
        self._database = database
        self._driver: AsyncDriver | None = None

    @property
    def is_connected(self) -> bool:
        return self._driver is not None

    async def connect(self) -> None:
        if self._driver is not None:
            return
        self._driver = AsyncGraphDatabase.driver(
            self._uri,
            auth=(self._user, self._password),
        )
        await self._driver.verify_connectivity()

    async def query(
        self,
        cypher: str,
        params: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        driver = self._require_driver()
        records, _, _ = await driver.execute_query(
            cypher,
            parameters_=dict(params or {}),
            database_=self._database,
            routing_=RoutingControl.READ,
        )
        return [_record_to_dict(record) for record in records]

    async def query_write(
        self,
        cypher: str,
        params: Mapping[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        driver = self._require_driver()
        records, _, _ = await driver.execute_query(
            cypher,
            parameters_=dict(params or {}),
            database_=self._database,
            routing_=RoutingControl.WRITE,
        )
        return [_record_to_dict(record) for record in records]

    async def close(self) -> None:
        if self._driver is None:
            return
        await self._driver.close()
        self._driver = None

    def _require_driver(self) -> AsyncDriver:
        if self._driver is None:
            raise RuntimeError("Neo4j driver is not connected. Call connect() first.")
        return self._driver

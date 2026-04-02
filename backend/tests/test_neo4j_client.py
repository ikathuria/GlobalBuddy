from app.db.neo4j_client import Neo4jClient


def test_neo4j_client_not_connected_until_connect() -> None:
    c = Neo4jClient(uri="bolt://localhost:7687", user="neo4j", password="x")
    assert c.is_connected is False

from neo4j import AsyncGraphDatabase

async def get_subgraph(company_id=None, property_key=None, property_value=None):
    # Example Neo4j query logic
    async with AsyncGraphDatabase.driver() as driver:
        with driver.session() as session:
            query = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100"
            # Apply filters here
            result = session.run(query)
            return [record for record in result]
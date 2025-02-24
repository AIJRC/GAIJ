import neo4j from "neo4j-driver";

export const neo4jConfig = {
  // url: 'bolt://localhost:7687', // or your Docker container's address
  url: 'bolt://158.37.66.6:7687',
  username: 'neo4j',
  password: 'testtest'
};

// Create a **single persistent Neo4j driver instance**
export const neo4jDriver = neo4j.driver(
  neo4jConfig.url,
  neo4j.auth.basic(neo4jConfig.username, neo4jConfig.password)
);

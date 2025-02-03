import connectivitySearchDefinitions from './definitions.json';
import { neo4jConfig } from './config';
import neo4j from 'neo4j-driver';

const driver = neo4j.driver(
  neo4jConfig.url,
  neo4j.auth.basic(neo4jConfig.username, neo4jConfig.password)
);

export async function searchNodes(searchString, otherNodeId, nodeType) {
  const session = driver.session();
  try {
    const query = `
      MATCH (n:${nodeType || 'Company'})  // Default to Company if no type specified
      WHERE (n.name CONTAINS $searchString OR n.full_address CONTAINS $searchString)
      RETURN n LIMIT 10
    `;
    
    const result = await session.run(query, { 
      searchString: searchString || '' 
    });
    return result.records.map(record => {
      const node = record.get('n');
      return {
        id: node.identity.toNumber(),
        name: node.properties.name || node.properties.full_address,
        metanode: node.labels[0],
        properties: node.properties
      };
    });
  } catch (error) {
    console.error('Error searching nodes:', error);
    return [];
  } finally {
    await session.close();
  }
}

export async function fetchGraphData(sourceId, targetId) {
  const session = driver.session();
  try {
    const query = `
      MATCH (source:Company)
      WHERE id(source) = $sourceId
      MATCH (target:Company)
      WHERE id(target) = $targetId
      OPTIONAL MATCH path = (source)-[:PARENT_OF*1..1]->(target)
      WITH source, target, path
      OPTIONAL MATCH path2 = (source)<-[:PARENT_OF*1..1]-(target)
      WITH source, target, path, path2
      MATCH (source)-[rel:PARENT_OF]->(sub:Company)
      RETURN source as n, rel, sub as m
      UNION
      MATCH (target)-[rel:PARENT_OF]->(sub:Company)
      WHERE id(target) = $targetId
      RETURN target as n, rel, sub as m
    `;
    
    const result = await session.run(query, {
      sourceId: parseInt(sourceId),
      targetId: parseInt(targetId)
    });
    
    const graph = {
      nodes: [],
      edges: []
    };
    
    const nodesMap = new Map();

    result.records.forEach(record => {
      const source = record.get('n');
      const target = record.get('m');
      const relationship = record.get('rel');

      // Add source node if not already added
      if (!nodesMap.has(source.identity.toNumber())) {
        nodesMap.set(source.identity.toNumber(), {
          neo4j_id: source.identity.toNumber(),
          name: source.properties.name || source.properties.full_address,
          metanode: source.labels[0],
          properties: { ...source.properties }
        });
      }

      // Add target node if not already added
      if (!nodesMap.has(target.identity.toNumber())) {
        nodesMap.set(target.identity.toNumber(), {
          neo4j_id: target.identity.toNumber(),
          name: target.properties.name || target.properties.full_address,
          metanode: target.labels[0],
          properties: { ...target.properties }
        });
      }

      // Add edge
      graph.edges.push({
        source_neo4j_id: source.identity.toNumber(),
        target_neo4j_id: target.identity.toNumber(),
        kind: relationship.type,
        directed: true,
        properties: { ...relationship.properties }
      });
    });

    graph.nodes = Array.from(nodesMap.values());
    return graph;
  } catch (error) {
    console.error('Error fetching graph data:', error);
    throw error;
  } finally {
    await session.close();
  }
}

export async function lookupNode(id) {
  const session = driver.session();
  try {
    const query = `
      MATCH (n)
      WHERE id(n) = $id
      RETURN n
    `;
    const result = await session.run(query, { id: parseInt(id) });
    if (result.records.length === 0) return {};
    
    const node = result.records[0].get('n');
    return {
      id: node.identity.toNumber(),
      name: node.properties.name || node.properties.full_address,
      metanode: node.labels[0],
      properties: node.properties
    };
  } catch (error) {
    console.error('Error looking up node:', error);
    return {};
  } finally {
    await session.close();
  }
}

export function getConnectivitySearchDefinitions() {
  return connectivitySearchDefinitions || {};
}

export async function testConnection() {
  const session = driver.session();
  try {
    const result = await session.run('MATCH (n) RETURN count(n) as count');
    console.log('Connected to Neo4j! Node count:', result.records[0].get('count').toNumber());
    return true;
  } catch (error) {
    console.error('Failed to connect to Neo4j:', error);
    return false;
  } finally {
    await session.close();
  }
}

export async function getTopCompanies() {
  const session = driver.session();
  try {
    const query = `
      MATCH (c:Company)-[:PARENT_OF]->(sub:Company)
      WITH c, count(sub) as subsidiary_count
      ORDER BY subsidiary_count DESC
      LIMIT 10
      WITH collect(c) as companies
      UNWIND companies as c
      MATCH path = (c)-[:PARENT_OF]->(sub:Company)
      UNWIND relationships(path) as rel
      MATCH (n)-[rel]->(m)
      RETURN DISTINCT n, rel, m
    `;
    
    const result = await session.run(query);
    console.log('Neo4j result:', result.records);
    
    const graph = {
      nodes: [],
      edges: []
    };
    
    const nodesMap = new Map();

    result.records.forEach(record => {
      const source = record.get('n');
      const target = record.get('m');
      const relationship = record.get('rel');

      // Add source node if not already added
      if (!nodesMap.has(source.identity.toNumber())) {
        nodesMap.set(source.identity.toNumber(), {
          neo4j_id: source.identity.toNumber(),
          name: source.properties.name || source.properties.full_address,
          metanode: source.labels[0],
          properties: { ...source.properties }
        });
      }

      // Add target node if not already added
      if (!nodesMap.has(target.identity.toNumber())) {
        nodesMap.set(target.identity.toNumber(), {
          neo4j_id: target.identity.toNumber(),
          name: target.properties.name || target.properties.full_address,
          metanode: target.labels[0],
          properties: { ...target.properties }
        });
      }

      // Add edge
      graph.edges.push({
        source_neo4j_id: source.identity.toNumber(),
        target_neo4j_id: target.identity.toNumber(),
        kind: relationship.type,
        directed: true,
        properties: { ...relationship.properties }
      });
    });

    graph.nodes = Array.from(nodesMap.values());
    console.log('Transformed data:', graph);
    return graph;
  } catch (error) {
    console.error('Error getting top companies:', error);
    return null;
  } finally {
    await session.close();
  }
}

export async function fetchNodeConnections(nodeId, nodeType) {
  const session = driver.session();
  try {
    const query = `
      MATCH (n)-[r]->(m)
      WHERE id(n) = $nodeId
      RETURN n, r, m, true as outgoing
      UNION
      MATCH (n)<-[r]-(m)
      WHERE id(n) = $nodeId
      RETURN n, r, m, false as outgoing
    `;
    
    const result = await session.run(query, { nodeId: nodeId });
    return {
      nodes: result.records.map(record => ({
        neo4j_id: record.get('m').identity.toNumber(),
        name: record.get('m').properties.name || record.get('m').properties.full_address,
        metanode: record.get('m').labels[0],
        properties: record.get('m').properties || {},
        elementType: 'node'
      })),
      edges: result.records.map(record => {
        const isOutgoing = record.get('outgoing');
        return {
          source_neo4j_id: isOutgoing ? record.get('n').identity.toNumber() : record.get('m').identity.toNumber(),
          target_neo4j_id: isOutgoing ? record.get('m').identity.toNumber() : record.get('n').identity.toNumber(),
          kind: record.get('r').type,
          properties: record.get('r').properties || {},
          elementType: 'edge',
          directed: true
        };
      })
    };
  } finally {
    await session.close();
  }
}

// Get top 10 companies with most board members
export async function getTopCompaniesByBoardMembers() {
  const session = driver.session();
  try {
    const query = `
      MATCH (p:Person)-[:LEADS]->(c:Company)
      WITH p, count(c) as company_count, collect(c) as companies
      ORDER BY company_count DESC
      LIMIT 10
      MATCH path = (p)-[:LEADS]->(c:Company)
      WHERE c IN companies
      RETURN path
    `;
    
    const result = await session.run(query);
    console.log('Neo4j result:', result.records);
    
    const graph = {
      nodes: [],
      edges: []
    };
    
    const nodesMap = new Map();

    result.records.forEach(record => {
      const path = record.get('path');
      const segments = path.segments;

      segments.forEach(segment => {
        const source = segment.start;
        const target = segment.end;
        const relationship = segment.relationship;

        // Add source node (Person) if not already added
        if (!nodesMap.has(source.identity.toNumber())) {
          nodesMap.set(source.identity.toNumber(), {
            neo4j_id: source.identity.toNumber(),
            name: source.properties.name,
            metanode: source.labels[0],
            properties: { ...source.properties }
          });
        }

        // Add target node (Company) if not already added
        if (!nodesMap.has(target.identity.toNumber())) {
          nodesMap.set(target.identity.toNumber(), {
            neo4j_id: target.identity.toNumber(),
            name: target.properties.name,
            metanode: target.labels[0],
            properties: { ...target.properties }
          });
        }

        // Add edge
        graph.edges.push({
          source_neo4j_id: source.identity.toNumber(),
          target_neo4j_id: target.identity.toNumber(),
          kind: relationship.type,
          directed: true,
          properties: { ...relationship.properties }
        });
      });
    });

    graph.nodes = Array.from(nodesMap.values());
    console.log('Transformed data:', graph);
    return graph;
  } catch (error) {
    console.error('Error getting top board members:', error);
    return null;
  } finally {
    await session.close();
  }
}

export async function getTopSharedAddresses() {
  const session = driver.session();
  try {
    const query = `
      MATCH (c:Company)-[:LOCATED_AT]->(a:Address)
    WITH a, count(c) as company_count, collect(c) as companies
    WHERE company_count > 1
    ORDER BY company_count DESC
    LIMIT 10
    MATCH path = (c:Company)-[:LOCATED_AT]->(a)
    WHERE c IN companies
    RETURN path
  `;
    
    const result = await session.run(query);
    console.log('Neo4j result:', result.records);
    
    const graph = {
      nodes: [],
      edges: []
    };
    
    const nodesMap = new Map();

    result.records.forEach(record => {
      const path = record.get('path');
      const segments = path.segments;

      segments.forEach(segment => {
        const source = segment.start;
        const target = segment.end;
        const relationship = segment.relationship;

        // Add source node (Person) if not already added
        if (!nodesMap.has(source.identity.toNumber())) {
          nodesMap.set(source.identity.toNumber(), {
            neo4j_id: source.identity.toNumber(),
            name: source.properties.name,
            metanode: source.labels[0],
            properties: { ...source.properties }
          });
        }

        // Add target node (Company) if not already added
        if (!nodesMap.has(target.identity.toNumber())) {
          nodesMap.set(target.identity.toNumber(), {
            neo4j_id: target.identity.toNumber(),
            name: target.properties.name,
            metanode: target.labels[0],
            properties: { ...target.properties }
          });
        }

        // Add edge
        graph.edges.push({
          source_neo4j_id: source.identity.toNumber(),
          target_neo4j_id: target.identity.toNumber(),
          kind: relationship.type,
          directed: true,
          properties: { ...relationship.properties }
        });
      });
    });

    graph.nodes = Array.from(nodesMap.values());
    console.log('Transformed data:', graph);
    return graph;
  } catch (error) {
    console.error('Error getting top board members:', error);
    return null;
  } finally {
    await session.close();
  }
}
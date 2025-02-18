import connectivitySearchDefinitions from './definitions.json';
import { neo4jConfig } from './config';
import neo4j from 'neo4j-driver';

const driver = neo4j.driver(
  neo4jConfig.url,
  neo4j.auth.basic(neo4jConfig.username, neo4jConfig.password)
);

// Utility function to create a node object from Neo4j node
function createNodeObject(node) {
  return {
    neo4j_id: node.identity.toNumber(),
    name: node.properties.name || node.properties.full_address,
    metanode: node.labels[0],
    properties: { ...node.properties }
  };
}

// Utility function to create an edge object from Neo4j relationship
function createEdgeObject(source, target, relationship) {
  return {
    source_neo4j_id: source.identity.toNumber(),
    target_neo4j_id: target.identity.toNumber(),
    kind: relationship.type,
    directed: true,
    properties: { ...relationship.properties }
  };
}

// Utility function to process Neo4j results into graph data
function processGraphResults(records, getNodesAndRelationships) {
  const graph = {
    nodes: [],
    edges: []
  };
  
  const nodesMap = new Map();

  records.forEach(record => {
    const { nodes, relationships } = getNodesAndRelationships(record);
    
    // Add nodes to map if not already present
    nodes.forEach(node => {
      if (!nodesMap.has(node.identity.toNumber())) {
        nodesMap.set(node.identity.toNumber(), createNodeObject(node));
      }
    });

    // Add edges
    relationships.forEach(rel => {
      graph.edges.push(createEdgeObject(rel.source, rel.target, rel.relationship));
    });
  });

  graph.nodes = Array.from(nodesMap.values());
  return graph;
}

// Example of how to refactor one of the existing functions:
export async function getSharedLeadership() {
  const session = driver.session();
  try {
    const query = `
      MATCH (p:Person)-[:LEADS]->(c1:Company)
      MATCH (p)-[:LEADS]->(c2:Company)
      WHERE c1 <> c2
      WITH p, c1, c2
      RETURN DISTINCT p, c1, c2
      LIMIT 100
    `;
    
    const result = await session.run(query);
    return processGraphResults(result.records, record => ({
      nodes: [record.get('p'), record.get('c1'), record.get('c2')],
      relationships: [
        { source: record.get('p'), target: record.get('c1'), relationship: { type: 'LEADS' } },
        { source: record.get('p'), target: record.get('c2'), relationship: { type: 'LEADS' } }
      ]
    }));
  } catch (error) {
    console.error('Error getting shared leadership:', error);
    throw error;
  } finally {
    await session.close();
  }
}

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

// Add this new function
export async function searchNodesWithConditions(conditions) {
  const session = driver.session();
  try {
    // Build dynamic query based on conditions
    const matches = conditions.map((c, i) => `
      MATCH (n${i}:${c.nodeType})
      WHERE n${i}.name CONTAINS $searchString${i}
    `).join('\n');

    const returns = conditions.map((_, i) => `n${i}`).join(', ');
    const query = `
      ${matches}
      RETURN ${returns}
      LIMIT 10
    `;
    
    const params = conditions.reduce((acc, c, i) => {
      acc[`searchString${i}`] = c.searchString;
      return acc;
    }, {});

    const result = await session.run(query, params);
    
    return processGraphResults(result.records, record => {
      const nodes = conditions.map((_, i) => record.get(`n${i}`));
      const relationships = [];
      
      // Create virtual relationships between consecutive nodes
      for (let i = 0; i < nodes.length - 1; i++) {
        relationships.push({
          source: nodes[i],
          target: nodes[i + 1],
          relationship: { type: 'RELATED_TO' }
        });
      }

      return { nodes, relationships };
    });
  } catch (error) {
    console.error('Error searching nodes with conditions:', error);
    return { nodes: [], edges: [] };
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
    
    return processGraphResults(result.records, record => ({
      nodes: [record.get('n'), record.get('m')],
      relationships: [{
        source: record.get('n'),
        target: record.get('m'),
        relationship: record.get('rel')
      }]
    }));
  } catch (error) {
    console.error('Error fetching graph data:', error);
    throw error;
  } finally {
    await session.close();
  }
}

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
    return processGraphResults(result.records, record => {
      const path = record.get('path');
      const segments = path.segments;
      const nodes = [];
      const relationships = [];

      segments.forEach(segment => {
        nodes.push(segment.start, segment.end);
        relationships.push({
          source: segment.start,
          target: segment.end,
          relationship: segment.relationship
        });
      });

      return { nodes, relationships };
    });
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
    return processGraphResults(result.records, record => {
      const path = record.get('path');
      const segments = path.segments;
      const nodes = [];
      const relationships = [];

      segments.forEach(segment => {
        nodes.push(segment.start, segment.end);
        relationships.push({
          source: segment.start,
          target: segment.end,
          relationship: segment.relationship
        });
      });

      return { nodes, relationships };
    });
  } catch (error) {
    console.error('Error getting top shared addresses:', error);
    return null;
  } finally {
    await session.close();
  }
}

export async function getParentSubsidiaryLeadership() {
  const session = driver.session();
  try {
    const query = `
      MATCH (person:Person)-[:LEADS]->(companyA:Company)-[:PARENT_OF]->(companyB:Company),
            (person)-[:LEADS]->(companyB)
      WITH person, companyA, companyB
      RETURN DISTINCT person, companyA, companyB
      LIMIT 100
    `;
    
    const result = await session.run(query);
    return processGraphResults(result.records, record => ({
      nodes: [record.get('person'), record.get('companyA'), record.get('companyB')],
      relationships: [
        { source: record.get('person'), target: record.get('companyA'), relationship: { type: 'LEADS' } },
        { source: record.get('person'), target: record.get('companyB'), relationship: { type: 'LEADS' } },
        { source: record.get('companyA'), target: record.get('companyB'), relationship: { type: 'PARENT_OF' } }
      ]
    }));
  } catch (error) {
    console.error('Error getting parent-subsidiary leadership:', error);
    throw error;
  } finally {
    await session.close();
  }
}

export async function getCompaniesWithTwoSubsidiaries() {
  const session = driver.session();
  try {    
    const query = `
      MATCH (parent:Company)-[:PARENT_OF]->(sub1:Company)
      MATCH (parent)-[:PARENT_OF]->(sub2:Company)
      WHERE sub1 <> sub2 OR sub1 = parent OR sub2 = parent
      WITH DISTINCT parent, sub1, sub2
      RETURN parent, sub1, sub2
      LIMIT 100
    `;
    
    const result = await session.run(query);
    return processGraphResults(result.records, record => ({
      nodes: [record.get('parent'), record.get('sub1'), record.get('sub2')],
      relationships: [
        { source: record.get('parent'), target: record.get('sub1'), relationship: { type: 'PARENT_OF' } },
        { source: record.get('parent'), target: record.get('sub2'), relationship: { type: 'PARENT_OF' } }
      ]
    }));
  } catch (error) {
    console.error('Error getting companies with two subsidiaries:', error);
    throw error;
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
    return processGraphResults(result.records, record => {
      const isOutgoing = record.get('outgoing');
      return {
        nodes: [record.get('m')],
        relationships: [{
          source: isOutgoing ? record.get('n') : record.get('m'),
          target: isOutgoing ? record.get('m') : record.get('n'),
          relationship: record.get('r')
        }]
      };
    });
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
    return createNodeObject(node);
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
    return processGraphResults(result.records, record => ({
      nodes: [record.get('n'), record.get('m')],
      relationships: [{
        source: record.get('n'),
        target: record.get('m'),
        relationship: record.get('rel')
      }]
    }));
  } catch (error) {
    console.error('Error getting top companies:', error);
    return null;
  } finally {
    await session.close();
  }
}
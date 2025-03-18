# GAIJ Neo4j Query Commands

## Basic Company Queries


```cypher
MATCH (c:Company)
RETURN count(c) as total_companies
```

### Top 10 companies with the highest number of subsidiaries
```cypher
MATCH (c:Company)-[:PARENT_OF]->(sub:Company)
WITH c, count(sub) as subsidiary_count
ORDER BY subsidiary_count DESC
LIMIT 10
MATCH path = (c)-[:PARENT_OF]->(sub:Company)
RETURN path
```

### Top 10 companies with the highest number of board members

```cypher
MATCH (p:Person)-[:LEADS]->(c:Company)
WITH p, count(c) as company_count, collect(c) as companies
ORDER BY company_count DESC
LIMIT 10
MATCH path = (p)-[:LEADS]->(c:Company)
WHERE c IN companies
RETURN path
```



## Top 10 addresses that are shared by the highest number of companies
MATCH (c:Company)-[:LOCATED_AT]->(a:Address)
WITH a, count(c) as company_count, collect(c) as companies
WHERE company_count > 1
ORDER BY company_count DESC
LIMIT 10
MATCH path = (c:Company)-[:LOCATED_AT]->(a)
WHERE c IN companies
RETURN path


```cypher
MATCH (c:Company)
WITH count(c) as total,
count(c.profit_status) as companies_with_profit_status,
count(c.number_of_employees) as companies_with_employee_data
RETURN total, companies_with_profit_status, companies_with_employee_data
```


### Find Company by Name
```cypher
MATCH (c:Company {name: "CompanyName"}) 
RETURN c
```

### Get Company with Subsidiaries
```cypher
MATCH (c:Company {name: "CompanyName"})-[:PARENT_OF]->(sub:Company)
RETURN c, sub
```

# Find Company Leadership
```cypher
MATCH (p:Person)-[:LEADS]->(c:Company {name: "CompanyName"})
RETURN p.name, p.role, c.name
```

# Get Board Members
```cypher
MATCH (p:Person {role: "Board Member"})-[:MEMBER_OF]->(c:Company {name: "CompanyName"})
RETURN p.name, c.name
```

# Find Company Properties
```cypher
MATCH (c:Company {name: "CompanyName"})-[r:OWNS|RENTS]->(p:Property)
RETURN c.name, type(r), p.name
```
# Get Company Address
```cypher
MATCH (c:Company {name: "CompanyName"})-[:LOCATED_AT]->(a:Address)
RETURN c.name, a.full_address
```

# Complete Company Network
```cypher
MATCH path = (parent:Company)-[:PARENT_OF*]->(c:Company {name: "CompanyName"})
RETURN path
UNION
MATCH path = (c:Company {name: "CompanyName"})-[:PARENT_OF*]->(sub:Company)
RETURN path
```

# Full Company Profile
```cypher
MATCH (c:Company {name: "CompanyName"})
OPTIONAL MATCH (c)-[:LOCATED_AT]->(a:Address)
OPTIONAL MATCH (p:Person)-[:LEADS|MEMBER_OF]->(c)
OPTIONAL MATCH (c)-[:OWNS|RENTS]->(prop:Property)
RETURN c, a, p, prop
```

# Delete All Nodes and Relationships
MATCH (n)
DETACH DELETE n

### Get all nodes
```cypher 
MATCH (n)
RETURN count(n) AS total_nodes

### Get all relationships 
```cypher 
MATCH ()-[r]->()
RETURN count(r) AS total_relationships
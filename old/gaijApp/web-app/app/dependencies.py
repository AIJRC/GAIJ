from fastapi import Depends
from neo4j import GraphDatabase
from app.config import settings

def get_db():
    driver = GraphDatabase.driver(settings.neo4j_uri, auth=(settings.neo4j_user, settings.neo4j_password))
    try:
        yield driver
    finally:
        driver.close()
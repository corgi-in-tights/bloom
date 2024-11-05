import math
import random
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# global db tables

# Guilds & their enabled extensions

def create_tables(engine, *args):  # noqa: ARG001
    Base.metadata.create_all(bind=engine)
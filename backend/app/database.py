from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")

client = AsyncIOMotorClient(MONGO_URL)
db = client[DATABASE_NAME]

import json
import os
from datetime import datetime
from pymongo import MongoClient

# Use the URI from environment or default to the one provided
MONGO_URI = os.environ.get("MONGODB_URI", "mongodb+srv://ThugPenguin1:Hunni246886425@googlecloudrapidagentha.ffu84im.mongodb.net/StemTutorDB?appName=GoogleCloudRapidAgentHackathon")

print(f"Connecting to MongoDB...")
client = MongoClient(MONGO_URI)

try:
    # Test connection
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
    
    db = client.get_default_database()
    
    with open('sample_data.json', 'r') as f:
        data = json.load(f)

    def normalize_doc(collection_name, doc):
        if collection_name == 'study_sessions' and isinstance(doc.get('timestamp'), str):
            try:
                doc['timestamp'] = datetime.fromisoformat(doc['timestamp'].replace('Z', '+00:00'))
            except ValueError:
                pass
        return doc
        
    for collection_name, docs in data.items():
        if docs:
            # Clear existing data for a clean slate
            db[collection_name].delete_many({})
            db[collection_name].insert_many([normalize_doc(collection_name, doc) for doc in docs])
            print(f"Inserted {len(docs)} documents into '{collection_name}' collection.")
            
    print("Database seeded successfully!")
    
except Exception as e:
    print(f"An error occurred: {e}")

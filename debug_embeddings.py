#!/usr/bin/env python3
"""Debug script to check embeddings and similarity scores"""

import os
import sys
sys.path.insert(0, '/app')

from app.vectordb import PlantVectorDB

# Initialize
db = PlantVectorDB()
db.load_plants_from_json("./data/plants.json")

# Check what's stored
print("=== Stored Plants ===")
all_plants = db.collection.get()
for i, doc in enumerate(all_plants['documents']):
    print(f"\n{i+1}. {all_plants['metadatas'][i]['name']}")
    print(f"   Document: {doc[:100]}...")

# Test query
print("\n\n=== Query Test ===")
query = "What grows well with 8 hours of sun?"
print(f"Query: {query}\n")

results = db.collection.query(
    query_texts=[query],
    n_results=4,
    include=["documents", "metadatas", "distances"]
)

print("Raw results:")
for i, (doc, meta, dist) in enumerate(zip(results['documents'][0], results['metadatas'][0], results['distances'][0])):
    print(f"\n{i+1}. {meta['name']}")
    print(f"   Distance: {dist}")
    print(f"   Similarity (1-distance): {1 - dist}")
    print(f"   Doc: {doc[:80]}...")

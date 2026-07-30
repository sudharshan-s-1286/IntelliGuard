import asyncio
from qdrant_client import AsyncQdrantClient

async def main():
    client = AsyncQdrantClient("localhost", port=6333)
    collections = await client.get_collections()
    if collections.collections:
        c_name = collections.collections[0].name
        results = await client.query_points(
            collection_name=c_name,
            query=[0.0]*384,
            limit=2
        )
        print("Type:", type(results))
        if hasattr(results, 'points'):
            print("Is list?", isinstance(results.points, list))
            print("First item type:", type(results.points[0]))
        
asyncio.run(main())

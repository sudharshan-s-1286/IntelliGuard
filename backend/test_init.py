import asyncio
from agents.security_agent.agent import SecurityAgent

async def main():
    agent = SecurityAgent()
    await agent.initialize()
    health = agent.health()
    print("Health:", health)

asyncio.run(main())

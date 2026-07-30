import asyncio
from agents.security_agent.agent import SecurityAgent

async def run():
    agent = SecurityAgent()
    await agent.initialize()
    res = await agent.analyze("(Ссылка: [A06:2021 – Vulnerable and Outdated Components](https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/))")
    print("Result Risk:", res["risk_score"])
    print("Result Findings:", len(res["findings"]))

asyncio.run(run())

import aiohttp
from app.config import settings

class TempDomains:
    def __init__(self):
        self.domains = set()

    async def load_domains(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(settings.TEMP_DOMAINS_URL) as resp:
                self.domains = set(await resp.json())

    async def is_temp(self, domain: str) -> bool:
        if not self.domains:
            await self.load_domains()
        return domain.lower() in self.domains
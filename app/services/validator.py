import dns.resolver
import socket
import asyncio
import aiosmtplib
from email_validator import validate_email, EmailNotValidError
from typing import Dict

class EmailValidator:
    def __init__(self, cache):
        self.cache = cache
        self.temp_domains = {"mailinator.com", "tempmail.com", "10minutemail.com"}

    async def validate(self, email: str, smtp_check: bool = False) -> Dict:
        # Validación básica de formato
        is_valid_format = self._validate_format(email)
        domain = email.split('@')[-1] if '@' in email else ''

        result = {
            "email": email,
            "valid_format": is_valid_format,
            "has_mx_records": await self._check_mx(domain) if is_valid_format else False,
            "is_temp": domain.lower() in self.temp_domains if domain else False,
            "domain_exists": await self._check_domain(domain) if domain else False,
            "score": 0.0
        }

        if smtp_check and is_valid_format:
            result.update(await self._verify_smtp(email))

        result["score"] = self._calculate_score(result)
        return result

    def _validate_format(self, email: str) -> bool:
        try:
            validate_email(email)
            return True
        except EmailNotValidError:
            return False

    async def _check_mx(self, domain: str) -> bool:
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: dns.resolver.resolve(domain, 'MX')
            )
            return True
        except:
            return False

    async def _check_domain(self, domain: str) -> bool:
        try:
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: socket.gethostbyname(domain)
            )
            return True
        except:
            return False

    async def _verify_smtp(self, email: str) -> Dict:
        domain = email.split('@')[-1]
        try:
            mx_records = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: dns.resolver.resolve(domain, 'MX')
            )
            mx_record = str(mx_records[0].exchange)
            
            async with aiosmtplib.SMTP(
                hostname=mx_record,
                port=25,
                timeout=5
            ) as smtp:
                await smtp.connect()
                await smtp.helo()
                await smtp.mail('verify@emailvalidator.com')
                code, _ = await smtp.rcpt(email)
                return {
                    "smtp_valid": code == 250,
                    "smtp_details": f"MX: {mx_record} - Code: {code}"
                }
        except Exception as e:
            return {
                "smtp_valid": False,
                "smtp_details": str(e)
            }

    def _calculate_score(self, result: Dict) -> float:
        score = 0.0
        if result["valid_format"]: score += 0.3
        if result["has_mx_records"]: score += 0.3
        if not result["is_temp"]: score += 0.2
        if result["domain_exists"]: score += 0.2
        return min(1.0, score)
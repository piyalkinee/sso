from abc import ABC, abstractmethod

import httpx
from loguru import logger

from ..configuration import conf


class PhoneProvider(ABC):
    @abstractmethod
    async def send_code(self, phone: str, code: str) -> bool:
        pass


class SMSProvider(PhoneProvider):
    async def send_code(self, phone: str, code: str) -> bool:
        if conf['sms']['provider'] == 'mock':
            logger.warning("=" * 60)
            logger.warning("📱 SMS CODE (DEBUG/MOCK MODE)")
            logger.warning(f"Phone: {phone}  Code: {code}")
            logger.warning("=" * 60)
            return True
        if conf['sms']['provider'] == 'twilio':
            return await self._send_twilio_code(phone, code)
        logger.error(f"SMS provider '{conf['sms']['provider']}' not configured")
        return False

    async def _send_twilio_code(self, phone: str, code: str) -> bool:
        twilio = conf['twilio']
        account_sid = twilio['account_sid']
        auth_token = twilio['auth_token']
        from_phone = twilio['from_phone']
        messaging_service_sid = twilio['messaging_service_sid']

        if not account_sid or not auth_token:
            logger.error("Twilio credentials are not configured")
            return False
        if not from_phone and not messaging_service_sid:
            logger.error("Twilio sender is not configured")
            return False

        payload = {
            "To": phone,
            "Body": f"Aydago verification code: {code}",
        }
        if messaging_service_sid:
            payload["MessagingServiceSid"] = messaging_service_sid
        else:
            payload["From"] = from_phone

        url = f"https://api.twilio.com/2010-04-01/Accounts/{account_sid}/Messages.json"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    url,
                    data=payload,
                    auth=(account_sid, auth_token),
                )
            if response.status_code in {200, 201}:
                return True
            logger.error(f"Twilio SMS failed: status={response.status_code} body={response.text[:300]}")
            return False
        except Exception as e:
            logger.error(f"Twilio SMS error: {e}")
            return False


class WhatsAppProvider(PhoneProvider):
    async def send_code(self, phone: str, code: str) -> bool:
        if conf['debug']:
            logger.warning("=" * 60)
            logger.warning("📱 WHATSAPP CODE (DEBUG MODE)")
            logger.warning(f"Phone: {phone}  Code: {code}")
            logger.warning("=" * 60)
            return True
        try:
            wa = conf['whatsapp']
            url = f"{wa['api_url']}/{wa['phone_number_id']}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": phone,
                "type": "template",
                "template": {
                    "name": "authentication_code",
                    "language": {"code": "ru"},
                    "components": [{"type": "body", "parameters": [{"type": "text", "text": code}]}],
                },
            }
            async with httpx.AsyncClient() as client:
                r = await client.post(url, json=payload, headers={"Authorization": f"Bearer {wa['api_token']}"}, timeout=10.0)
            return r.status_code == 200
        except Exception as e:
            logger.error(f"WhatsApp error: {e}")
            return False


class TelegramProvider(PhoneProvider):
    async def send_code(self, phone: str, code: str) -> bool:
        if conf['debug']:
            logger.warning("=" * 60)
            logger.warning("📱 TELEGRAM CODE (DEBUG MODE)")
            logger.warning(f"Phone: {phone}  Code: {code}")
            logger.warning("=" * 60)
            return True
        logger.error("Telegram production not implemented (needs chat_id mapping)")
        return False


class PhoneProviderFactory:
    @staticmethod
    def get_provider(provider_type: str) -> PhoneProvider:
        providers = {"sms": SMSProvider, "whatsapp": WhatsAppProvider, "telegram": TelegramProvider}
        cls = providers.get(provider_type)
        if not cls:
            raise ValueError(f"Unknown provider: {provider_type}")
        return cls()

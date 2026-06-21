from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from loguru import logger
from databases.core import Connection

from ..configuration import conf
from ..core import access_tokens
from ..core.phone_providers import PhoneProviderFactory
from ..core.verification_code import format_phone_number
from ..exceptions.auth import InvalidCredentialsError
from ..model.queries import phone as qphone
from ..model.queries import tokens as qtokens
from ..model.queries import users as qusers
from ..schemas import output as soutput
from ..schemas import phone as sphone
from ..schemas import tokens as stokens


async def check_phone(database: Connection, data: sphone.PhoneCheckInput) -> sphone.PhoneCheckOutput:
    phone = format_phone_number(data.phone)
    user_id = await qphone.get_user_id_by_phone(database=database, phone=phone)
    return sphone.PhoneCheckOutput(exists=user_id is not None, phone=phone)


async def send_phone_code(database: Connection, data: sphone.PhoneSendCodeInput) -> sphone.PhoneSendCodeOutput:
    phone = format_phone_number(data.phone)
    logger.info(f"Sending code to {phone} via {data.provider}")

    code = await qphone.create_verification_code(
        database=database,
        phone=phone,
        provider=data.provider,
    )

    provider = PhoneProviderFactory.get_provider(data.provider)
    success = await provider.send_code(phone, code)
    expose_debug_code = conf["debug"] or conf["sms"]["provider"] == "mock"

    if not success:
        if not expose_debug_code:
            raise HTTPException(status_code=500, detail="Не удалось отправить код. Попробуйте позже.")
        logger.warning("SMS provider failed, using dev debug-code fallback")

    if expose_debug_code:
        logger.warning("=" * 60)
        logger.warning("📱 PHONE OTP CODE (DEV)")
        logger.warning(f"Phone: {phone}  Provider: {data.provider}  Code: {code}")
        logger.warning("=" * 60)

    return sphone.PhoneSendCodeOutput(
        success=True,
        message=f"Код отправлен на {phone}",
        phone=phone,
        expires_in=conf['verification']['code_ttl'],
        provider=data.provider,
        debug_code=code if expose_debug_code else None,
    )


async def verify_phone_code(database: Connection, data: sphone.PhoneVerifyCodeInput) -> soutput.AccessOutput:
    phone = format_phone_number(data.phone)
    logger.debug(f"Verifying code for {phone}")
    fixed_code = conf["verification"].get("dev_fixed_code") or ""
    fixed_code_ok = bool(conf["debug"] and fixed_code and data.code == fixed_code)

    code_record = None
    for provider in ["sms", "telegram", "whatsapp"]:
        record = await qphone.get_latest_verification_code(database=database, phone=phone, provider=provider)
        if record and record["expires_at"] >= datetime.now(timezone.utc).replace(tzinfo=None) and not record["used_at"]:
            code_record = record
            break

    if code_record is None and not fixed_code_ok:
        raise InvalidCredentialsError(detail="Код не найден. Запросите новый код.")

    if code_record and code_record["attempts"] >= conf['verification']['max_attempts']:
        raise InvalidCredentialsError(detail="Превышено количество попыток. Запросите новый код.")

    if code_record:
        await qphone.increment_attempts(database=database, code_id=code_record["id"])

    if not fixed_code_ok and code_record["code"] != data.code:
        raise InvalidCredentialsError(detail="Неверный код.")

    # Get or create user
    user_id = await qphone.get_user_id_by_phone(database=database, phone=phone)
    is_new = False
    if user_id is None:
        user_id = await qphone.create_user_by_phone(database=database, phone=phone, name=data.name or "")
        is_new = True

    if code_record:
        await qphone.mark_code_as_used(database=database, code_id=code_record["id"])

    user_data = await qusers.get_data_for_token(database=database, id=user_id)
    token_data = user_data.model_dump()
    roles = [
        group.get("name")
        for group in token_data.get("groups", [])
        if group.get("name")
    ]
    if conf["debug"] and data.role in {"passenger", "driver"} and data.role not in roles:
        roles.append(data.role)
    token_data["sub"] = str(user_id)
    token_data["roles"] = roles

    ttl = conf['access_security']['access_token_ttl']
    access_token = access_tokens.generate_token(
        data=token_data,
        type="access",
        ttl=ttl,
    )
    refresh_token = access_tokens.generate_token(
        data={"id": user_id},
        type="refresh",
        ttl=conf['access_security']['refresh_token_ttl'],
    )

    await qtokens.create(
        database=database,
        token=stokens.TokenCreate(
            access_token=access_token,
            refresh_token=refresh_token,
            valid_to=datetime.today() + timedelta(minutes=ttl),
            user_id=user_id,
        ),
    )

    return soutput.AccessOutput(
        tokens=soutput.TokensOutput(access=access_token, refresh=refresh_token),
        is_new=is_new,
    )

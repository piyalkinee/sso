from fastapi import APIRouter

from ...commands import phone as cphone
from ...schemas import output as soutput, middleware as smiddleware, phone as sphone
from ...middleware import session as mvsession, route

router: APIRouter = APIRouter()
middleware_router = lambda method, path, **kwargs: route(router, method, path, **kwargs)


@middleware_router(
    method="post",
    path="/check",
    summary="Check if phone number is registered",
    response_model=sphone.PhoneCheckOutput,
    requires_auth=False,
    permissions=[],
)
async def check_phone(
    data: sphone.PhoneCheckInput,
    session: smiddleware.Session = mvsession,
):
    return await cphone.check_phone(database=session.db, data=data)


@middleware_router(
    method="post",
    path="/send-code",
    summary="Send OTP code via SMS / WhatsApp / Telegram",
    response_model=sphone.PhoneSendCodeOutput,
    requires_auth=False,
    permissions=[],
)
async def send_code(
    data: sphone.PhoneSendCodeInput,
    session: smiddleware.Session = mvsession,
):
    return await cphone.send_phone_code(database=session.db, data=data)


@middleware_router(
    method="post",
    path="/verify",
    summary="Verify OTP code and get JWT tokens",
    response_model=soutput.AccessOutput,
    requires_auth=False,
    permissions=[],
)
async def verify_code(
    data: sphone.PhoneVerifyCodeInput,
    session: smiddleware.Session = mvsession,
):
    return await cphone.verify_phone_code(database=session.db, data=data)

from pydantic import BaseModel, Field


class PhoneCheckInput(BaseModel):
    phone: str = Field(..., description="Phone number in international format")


class PhoneCheckOutput(BaseModel):
    exists: bool
    phone: str


class PhoneSendCodeInput(BaseModel):
    phone: str = Field(..., description="Phone number in international format")
    provider: str = Field("sms", description="sms | telegram | whatsapp")
    name: str | None = Field(None, description="Name for new user registration")


class PhoneSendCodeOutput(BaseModel):
    success: bool
    message: str
    phone: str
    expires_in: int
    provider: str
    debug_code: str | None = Field(None, description="Dev/mock only. Omitted for real SMS providers.")


class PhoneVerifyCodeInput(BaseModel):
    phone: str = Field(..., description="Phone number in international format")
    code: str = Field(..., description="6-digit verification code")
    name: str | None = Field(None, description="Name for new user (optional)")
    role: str | None = Field(None, description="Dev/mock only: passenger | driver")

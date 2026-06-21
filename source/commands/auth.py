from datetime import datetime, timedelta
import httpx
from loguru import logger
from databases.core import Connection
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from jose import jwt, jwk
from jose.utils import base64url_decode
import json

from ..model.queries import users as qusers, tokens as qtokens, projects as qprojects
from ..schemas import oauth2 as oauth2_input, output as soutput, tokens as stokens
from ..core import access_tokens
from ..configuration import conf
from ..exceptions import auth, access
from ..exceptions.database import ItemNotFoundError

# For Apple, we verify the audience matches our bundle.
# For Google, we verify the audience matches our Client ID.

async def verify_google_token(token: str) -> str:
    try:
        # Use google-auth library which handles caching and verification securely
        request = google_requests.Request()
        id_info = id_token.verify_oauth2_token(
            token, 
            request, 
            conf['oauth2']['google_client_id']
        )
        
        email = id_info.get('email')
        if not email:
            raise ValueError("Email not found in token")
        return email
    except Exception as e:
        logger.error(f"Google Token Verification Failed: {e}")
        raise auth.InvalidCredentialsError

async def verify_apple_token(token: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://appleid.apple.com/auth/keys")
            response.raise_for_status()
            jwks = response.json()

        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        alg = header.get("alg")

        rsa_key = next((key for key in jwks["keys"] if key["kid"] == kid), None)
        if not rsa_key:
            raise ValueError("Invalid Key ID")

        bundle_id = conf['oauth2']['apple_bundle_id']
        payload = jwt.decode(
            token,
            rsa_key,
            algorithms=[alg],
            audience=bundle_id,
            issuer="https://appleid.apple.com",
        )

        email = payload.get("email")
        if not email:
            raise ValueError("Email not found in Apple Token")

        return email

    except Exception as e:
        logger.error(f"Apple Token Verification Failed: {e}")
        raise auth.InvalidCredentialsError


async def login_oauth2(
        database: Connection,
        data: oauth2_input.OAuth2Input
) -> soutput.AccessOutput:
    
    email = None
    if data.provider == 'google':
        email = await verify_google_token(data.token)
    elif data.provider == 'apple':
        email = await verify_apple_token(data.token)
    else:
        raise access.InvalidInput("Unsupported provider")
        
    logger.info(f"OAuth2 Login verified for email: {email}")

    # 1. Check if we have a direct provider link (stable ID)
    user_id = await qusers.get_id_by_provider(
        database=database,
        provider=data.provider,
        provider_user_id=email
    )
    
    if not user_id:
        # 2. If no link, check by email (legacy or first-time migration)
        try:
            user_email_data = await qusers.get_by_email(database=database, email=email)
            user_id = user_email_data.id
        except ItemNotFoundError:
            # 3. If still not found, create new user
            logger.info(f"User not found, creating new user for {email}")
            try:
                user_id = await qusers.create_oauth2_user(database, email)
            except Exception as e:
                logger.error(f"Failed to create user: {e}")
                raise access.DatabaseError # Generic error
        except Exception as e:
            logger.error(f"Error checking user: {e}")
            raise
        
    # Link Provider (Ensures it's recorded if not already)
    await qusers.record_provider_link(
        database=database,
        user_id=user_id,
        provider=data.provider,
        provider_user_id=email # Using email as provider_user_id since we don't have stable sub table yet
    )

    # Get Full Data
    full_user_data = await qusers.get_data_for_token(database=database, id=user_id)

    project_id_str = None
    if data.project_id:
        if await qprojects.exists(database=database, project_id=data.project_id):
            await qprojects.link_user(database=database, user_id=user_id, project_id=data.project_id)
            project_id_str = str(data.project_id)
        else:
            logger.warning(f"project_id={data.project_id} not found, skipping link")

    user_projects = await qprojects.get_user_project_names(database=database, user_id=user_id)

    access_token = access_tokens.generate_token(
        type="access",
        data={**full_user_data.model_dump(), "project_id": project_id_str, "projects": user_projects},
        ttl=conf['access_security']['access_token_ttl']
    )
    refresh_token = access_tokens.generate_token(
        type="refresh",
        data={
            "id": user_id,
            "project_id": project_id_str,
        },
        ttl=conf['access_security']['refresh_token_ttl']
    )

    await qtokens.create(
        database=database,
        token=stokens.TokenCreate(
            access_token=access_token,
            refresh_token=refresh_token,
            valid_to=datetime.today() + timedelta(minutes=conf['access_security']['access_token_ttl']),
            user_id=user_id,
        ))

    return soutput.AccessOutput(
        tokens=soutput.TokensOutput(
            access=access_token,
            refresh=refresh_token
        )
    )


async def link_oauth2(
        database: Connection,
        user_id: int,
        data: oauth2_input.OAuth2Input
) -> soutput.AccessOutput:
    
    email = None
    if data.provider == 'google':
        email = await verify_google_token(data.token)
    elif data.provider == 'apple':
        email = await verify_apple_token(data.token)
    else:
        raise access.InvalidInput("Unsupported provider")
        
    logger.info(f"Link OAuth2 verified for email: {email}, user_id: {user_id}")

    # Record Provider Link
    await qusers.record_provider_link(
        database=database,
        user_id=user_id,
        provider=data.provider,
        provider_user_id=email
    )
    
    # Return updated OAuth status
    # Fetching full user data to get all linked providers
    full_user_data = await qusers.get_data_for_token(database=database, id=user_id)
    
    # Generate Tokens (Shared Logic)
    # Copied from access.base to ensure consistency
    access_token = access_tokens.generate_token(
        type="access",
        data=full_user_data.model_dump(),
        ttl=conf['access_security']['access_token_ttl']
    )
    refresh_token = access_tokens.generate_token(
        type="refresh",
        data={
            "id": user_id
        },
        ttl=conf['access_security']['refresh_token_ttl']
    )
    
    await qtokens.create(
        database=database,
        token=stokens.TokenCreate(
            access_token=access_token,
            refresh_token=refresh_token,
            valid_to=datetime.today() + timedelta(minutes=conf['access_security']['access_token_ttl']),
            user_id=user_id,
        ))
        
    return soutput.AccessOutput(
        tokens=soutput.TokensOutput(
            access=access_token,
            refresh=refresh_token
        )
    )


async def refresh_access_token(
        database: Connection,
        refresh_token: str
) -> soutput.AccessOutput:
    try:
        # Decode and verify refresh token
        token_data = access_tokens.decode_token(refresh_token)
        
        if token_data.get('type') != 'refresh':
             raise auth.InvalidCredentialsError
             
        user_id = token_data.get('id')
        if not user_id:
            raise auth.InvalidCredentialsError

        project_id_str = token_data.get('project_id')

        # Verify user exists (and is active)
        full_user_data = await qusers.get_data_for_token(database=database, id=user_id)
        user_projects = await qprojects.get_user_project_names(database=database, user_id=user_id)

        # Generate Tokens
        new_access_token = access_tokens.generate_token(
            type="access",
            data={**full_user_data.model_dump(), "project_id": project_id_str, "projects": user_projects},
            ttl=conf['access_security']['access_token_ttl']
        )
        new_refresh_token = access_tokens.generate_token(
            type="refresh",
            data={
                "id": user_id,
                "project_id": project_id_str,
            },
            ttl=conf['access_security']['refresh_token_ttl']
        )
        
        await qtokens.create(
            database=database,
            token=stokens.TokenCreate(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                valid_to=datetime.today() + timedelta(minutes=conf['access_security']['access_token_ttl']),
                user_id=user_id,
            ))
            
        return soutput.AccessOutput(
            tokens=soutput.TokensOutput(
                access=new_access_token,
                refresh=new_refresh_token
            )
        )
        
    except Exception as e:
        logger.error(f"Refresh Token Failed: {e}")
        raise auth.InvalidCredentialsError

from typing import Annotated

from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer

from config import get_jwt_auth_manager
from exceptions import BaseSecurityError
from security.interfaces import JWTAuthManagerInterface


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/accounts/login/")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    jwt_manager: JWTAuthManagerInterface = Depends(get_jwt_auth_manager),
):
    try:
        decoded_token = jwt_manager.decode_access_token(token)
        user_id = decoded_token.get("user_id")
    except BaseSecurityError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )
    return {"id": user_id}

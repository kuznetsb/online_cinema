from datetime import datetime, timezone
from typing import cast

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import UserModel, UserGroupModel, ActivationTokenModel, RefreshTokenModel
from schemas import UserRegistrationRequestSchema, UserActivationRequestSchema


async def get_user_by_email(db: AsyncSession, email: str) -> UserModel:
    stmt = select(UserModel).where(UserModel.email == email)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int) -> UserModel:
    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await db.execute(stmt)
    return result.scalars().first()


async def get_user_group_by_name(db: AsyncSession, name: str) -> UserGroupModel:
    stmt = select(UserGroupModel).where(UserGroupModel.name == name)
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_activation_token(db: AsyncSession, user_id: int) -> ActivationTokenModel:
    try:
        activation_token = ActivationTokenModel(user_id=user_id)
        db.add(activation_token)

        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise e
    return activation_token


async def create_new_user(
    db: AsyncSession,
    user_data: UserRegistrationRequestSchema,
    user_group_id: int
) -> UserModel:
    try:
        new_user = UserModel.create(
            email=str(user_data.email),
            raw_password=user_data.password,
            group_id=user_group_id,
        )
        db.add(new_user)
        await db.flush()
        await db.commit()
        await db.refresh(new_user)

        return new_user
    except SQLAlchemyError as e:
        await db.rollback()
        raise e


async def get_activation_token(
    db: AsyncSession, activation_data: UserActivationRequestSchema
) -> ActivationTokenModel:
    stmt = (
        select(ActivationTokenModel)
        .options(joinedload(ActivationTokenModel.user))
        .join(UserModel)
        .where(
            UserModel.email == activation_data.email,
            ActivationTokenModel.token == activation_data.token
        )
    )
    result = await db.execute(stmt)
    token_record = result.scalars().first()
    now_utc = datetime.now(timezone.utc)
    if not token_record or cast(datetime, token_record.expires_at).replace(tzinfo=timezone.utc) < now_utc:
        if token_record:
            await db.delete(token_record)
            await db.commit()
    return token_record


async def create_refresh_token(
    db: AsyncSession,
    user_id: int,
    days_valid: int,
    jwt_refresh_token: str,
) -> RefreshTokenModel:
    try:
        refresh_token = RefreshTokenModel.create(
            user_id=user_id,
            days_valid=days_valid,
            token=jwt_refresh_token
        )
        db.add(refresh_token)
        await db.flush()
        await db.commit()
    except SQLAlchemyError as e:
        await db.rollback()
        raise e
    return refresh_token


async def get_refresh_token(db: AsyncSession, token: str) -> RefreshTokenModel:
    stmt = select(RefreshTokenModel).filter_by(token=token)
    result = await db.execute(stmt)
    return result.scalars().first()

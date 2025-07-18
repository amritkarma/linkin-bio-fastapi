from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, delete
from . import models, schemas, auth

async def get_user_by_username(db: AsyncSession, username: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalar_one_or_none()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_pw = auth.hash_password(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_pw
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def authenticate_user(db: AsyncSession, username: str, password: str):
    user = await get_user_by_username(db, username)
    if not user or not auth.verify_password(password, user.hashed_password):
        return None
    return user

async def get_user_links(db: AsyncSession, username: str, limit=10, offset=0):
    user = await get_user_by_username(db, username)
    if not user:
        return []
    result = await db.execute(
        select(models.Link)
        .where(models.Link.user_id == user.id)
        .offset(offset)
        .limit(limit)
    )
    return result.scalars().all()

async def create_link(db: AsyncSession, user_id: int, link: schemas.LinkCreate):
    db_link = models.Link(title=link.title, url=link.url, user_id=user_id)
    db.add(db_link)
    await db.commit()
    await db.refresh(db_link)
    return db_link

async def get_link_by_id(db: AsyncSession, link_id: int, user_id: int):
    result = await db.execute(
        select(models.Link).where(models.Link.id == link_id, models.Link.user_id == user_id)
    )
    return result.scalar_one_or_none()

async def update_link(db: AsyncSession, link_id: int, user_id: int, link_data: schemas.LinkUpdate):
    result = await db.execute(
        select(models.Link).where(models.Link.id == link_id, models.Link.user_id == user_id)
    )
    link = result.scalar_one_or_none()
    if not link:
        return None
    if link_data.title is not None:
        link.title = link_data.title
    if link_data.url is not None:
        link.url = link_data.url
    await db.commit()
    await db.refresh(link)
    return link

async def delete_link(db: AsyncSession, link_id: int, user_id: int):
    result = await db.execute(
        select(models.Link).where(models.Link.id == link_id, models.Link.user_id == user_id)
    )
    link = result.scalar_one_or_none()
    if link:
        await db.delete(link)
        await db.commit()
    return link

async def update_user_profile(db: AsyncSession, user_id: int, data: schemas.UserUpdate):
    result = await db.execute(
        select(models.User).where(models.User.id == user_id)
    )
    user = result.scalar_one_or_none()
    if not user:
        return None
    if data.bio is not None:
        user.bio = data.bio
    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url
    await db.commit()
    await db.refresh(user)
    return user

async def get_user_by_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalar_one_or_none()

async def get_links_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Link).where(models.Link.user_id == user_id))
    return result.scalars().all()

async def get_public_profile(db: AsyncSession, username: str):
    result = await db.execute(
        select(models.User)
        .options(selectinload(models.User.links))  # ✅ eager load
        .where(models.User.username == username)
    )
    user = result.scalars().first()
    if not user:
        return None

    return {
        "username": user.username,
        "bio": user.bio,
        "avatar_url": user.avatar_url,
        "links": [
            {"id": link.id, "title": link.title, "url": link.url}
            for link in user.links
        ],
    }
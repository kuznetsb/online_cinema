from datetime import date
from typing import Iterable

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import MovieModel, CountryModel, GenreModel, ActorModel, LanguageModel
from schemas import MovieCreateSchema, MovieUpdateSchema


async def get_movies_count(db: AsyncSession) -> int:
    count_stmt = select(func.count(MovieModel.id))
    result_count = await db.execute(count_stmt)
    return result_count.scalar() or 0


async def get_paginated_movies_list(
    db: AsyncSession, offset: int, page_size: int
) -> Iterable[MovieModel]:
    order_by = MovieModel.default_order_by()
    stmt = select(MovieModel)
    if order_by:
        stmt = stmt.order_by(*order_by)

    stmt = stmt.offset(offset).limit(page_size)

    result_movies = await db.execute(stmt)
    return result_movies.scalars().all()


async def get_movie_by_name_and_date(db: AsyncSession, name: str, release_date: date) -> MovieModel:
    existing_stmt = select(MovieModel).where(
        (MovieModel.name == name),
        (MovieModel.date == release_date)
    )
    existing_result = await db.execute(existing_stmt)
    return existing_result.scalars().first()


async def get_or_create_country(db: AsyncSession, country_code: str) -> CountryModel:
    country_stmt = select(CountryModel).where(CountryModel.code == country_code)
    country_result = await db.execute(country_stmt)
    country = country_result.scalars().first()
    if not country:
        country = CountryModel(code=country_code)
        db.add(country)
        await db.flush()
    return country


async def get_or_create_genre(db: AsyncSession, genre_name: str) -> GenreModel:
    genre_stmt = select(GenreModel).where(GenreModel.name == genre_name)
    genre_result = await db.execute(genre_stmt)
    genre = genre_result.scalars().first()

    if not genre:
        genre = GenreModel(name=genre_name)
        db.add(genre)
        await db.flush()
    return genre


async def get_or_create_actor(db: AsyncSession, actor_name: str) -> ActorModel:
    actor_stmt = select(ActorModel).where(ActorModel.name == actor_name)
    actor_result = await db.execute(actor_stmt)
    actor = actor_result.scalars().first()

    if not actor:
        actor = ActorModel(name=actor_name)
        db.add(actor)
        await db.flush()
    return actor


async def get_or_create_language(db: AsyncSession, language_name: str) -> LanguageModel:
    lang_stmt = select(LanguageModel).where(LanguageModel.name == language_name)
    lang_result = await db.execute(lang_stmt)
    language = lang_result.scalars().first()

    if not language:
        language = LanguageModel(name=language_name)
        db.add(language)
        await db.flush()
    return language


async def create_movie_in_db(db: AsyncSession, movie_data: MovieCreateSchema) -> MovieModel:
    try:
        country = await get_or_create_country(db, movie_data.country)
        genres = []
        for genre_name in movie_data.genres:
            genre = await get_or_create_genre(db, genre_name)
            genres.append(genre)

        actors = []
        for actor_name in movie_data.actors:
            actor = await get_or_create_actor(db, actor_name)
            actors.append(actor)

        languages = []
        for language_name in movie_data.languages:
            language = await get_or_create_language(db, language_name)
            languages.append(language)

        movie = MovieModel(
            name=movie_data.name,
            date=movie_data.date,
            score=movie_data.score,
            overview=movie_data.overview,
            status=movie_data.status,
            budget=movie_data.budget,
            revenue=movie_data.revenue,
            country=country,
            genres=genres,
            actors=actors,
            languages=languages,
        )
        db.add(movie)
        await db.commit()
        await db.refresh(movie, ["genres", "actors", "languages"])

        return movie
    except IntegrityError as e:
        await db.rollback()
        raise e


async def get_movie_by_id_from_db(db: AsyncSession, movie_id: int, joined: bool = False) -> MovieModel:
    stmt = select(MovieModel).where(MovieModel.id == movie_id)
    if joined:
        stmt.options(
            joinedload(MovieModel.country),
            joinedload(MovieModel.genres),
            joinedload(MovieModel.actors),
            joinedload(MovieModel.languages),
        )

    result = await db.execute(stmt)
    return result.scalars().first()


async def update_movie_in_db(db: AsyncSession, movie: MovieModel, movie_data: MovieUpdateSchema):
    for field, value in movie_data.model_dump(exclude_unset=True).items():
        setattr(movie, field, value)

    try:
        await db.commit()
        await db.refresh(movie)
    except IntegrityError as e:
        await db.rollback()
        raise e

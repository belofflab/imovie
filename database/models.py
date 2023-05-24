import datetime
from decimal import Decimal

from gino import Gino
from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        Integer, Numeric, Sequence, String)

db = Gino()


class User(db.Model):
    __tablename__ = "users"
    idx: int = Column(BigInteger, primary_key=True)
    username: str = Column(String(255))

    setup_date: datetime.datetime = Column(DateTime, default=datetime.datetime.now)

    def __str__(self) -> str:
        return f"ID: {self.idx}\nUsername: {self.username}\n\nДата регистрации: {self.setup_date}"

class Genre(db.Model):
    __tablename__ = "genres"
    idx: int = Column(BigInteger, Sequence('genres_idx_seq'), primary_key=True)
    name: str = Column(String(length=255))

class Movie(db.Model):
    __tablename__ = "movies"
    idx: int = Column(BigInteger, Sequence('movies_idx_seq'), primary_key=True)
    href:  str = Column(String(length=1024))
    genres: str = Column(String(length=1024))
    title: str = Column(String(length=255))
    description: str = Column(String(length=1024))
    country: str = Column(String(length=255))
    voiced_by: str = Column(String(length=1024))
    year: str = Column(String(length=1024))
    rate: Decimal = Column(Numeric(12,2))
    preview: str = Column(String(length=1024))
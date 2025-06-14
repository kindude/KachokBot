import datetime

from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class UserTable(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    nickname = Column(String)


class DayTable(Base):
    __tablename__ = "days"
    id = Column(Integer, primary_key=True)
    date = Column(Date)


class PushUpsTable(Base):
    __tablename__ = "pushups"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    day_id = Column(Integer, ForeignKey("days.id"))
    pushups_done = Column(Integer)


class AnecdotesTable(Base):
    __tablename__ = "anecdotes"
    id = Column(Integer, primary_key=True)
    anecdote = Column(String)
    last_sent = Column(Date, nullable=False, default=datetime.date(9999, 12, 31))


class ArticlesSent(Base):
    __tablename__ = "articles_sent"
    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)


class MotivationalPhrases(Base):
    __tablename__ = "motivational_phrases"
    id = Column(Integer, primary_key=True)
    phrase = Column(String)


from sqlalchemy import Column, Integer, BigInteger, String, create_engine, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import *
from data.operations import *
import re

engine = create_engine(db_url, pool_pre_ping=True)
Base = declarative_base()
session = sessionmaker(bind=engine)()
session.begin()


class User(Base):
    __tablename__ = 'users'
    user_id = Column(BigInteger, primary_key=True)
    cred = Column(String, default='user')
    full_name = Column(String)
    username = Column(String)
    scene = Column(String, default='menu')
    notifications = Column(Boolean, default=True)
    reg_time = Column(DateTime)

    @staticmethod
    def subscribed():
        return session.query(User).filter_by(notifications=True).all()

    @staticmethod
    def all():
        return session.query(User).all()

    @staticmethod
    def get_by_full_name(full_name):
        return session.query(User).filter_by(full_name=full_name).first()

    @staticmethod
    def get_by_username(username):
        return session.query(User).filter_by(username=username).first()

    @staticmethod
    def get(user_id):
        return session.query(User).filter_by(user_id=user_id).first()

    @staticmethod
    def find(text):
        user = None
        if re.fullmatch(r'\d+', text):
            value = re.findall(r'(\d+)', text)[0][-1]
            user = User.get(value)
        if user is None:
            user = User.get_by_username(text[1:])
        if user is None:
            user = User.get_by_full_name(text)
        return user

    @staticmethod
    def add(user_id, username, full_name):
        user = User.get(user_id)
        status = 'ok'
        if user is None:
            user = User(user_id=user_id, username=username, full_name=full_name, reg_time=now(), scene='start')
            session.add(user)
            session.commit()
            status = 'start'
        return status, user

    @staticmethod
    def edit(user, commit=True, **kwargs):
        user = user if isinstance(user, User) else User.get(user)
        for key, value in kwargs.items():
            user.__setattr__(key, value)
        if commit:
            session.commit()


class Site(Base):
    __tablename__ = 'sites'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    url = Column(String)
    css_path = Column(String)
    title_hash = Column(String)
    interval = Column(Integer)
    update_time = Column(DateTime)
    js_required = Column(Boolean, default=False)
    translate = Column(Boolean, default=True)
    enabled = Column(Boolean, default=True)
    added_time = Column(DateTime)

    @staticmethod
    def get_updating():
        all_sites = session.query(Site).filter_by(enabled=True).order_by(Site.id).all()
        updating_sites = []
        time_now = now()
        for site in all_sites:
            if site.update_time is None or site.update_time + timedelta(milliseconds=site.interval) <= time_now:
                updating_sites.append(site)
        return updating_sites

    @staticmethod
    def get(site_id):
        return session.query(Site).filter_by(id=site_id).first()

    @staticmethod
    def add(url, css_path, js_required=False, name=None):
        if name is None:
            name = get_url_name(url)
        time_now = now()
        interval = 60000 if js_required else 15000
        site = Site(name=name, url=url, interval=interval, js_required=js_required, css_path=css_path, update_time=time_now, added_time=time_now)
        session.add(site)
        session.commit()
        return site

    @staticmethod
    def edit(site, commit=True, **kwargs):
        site = site if isinstance(site, Site) else Site.get(site)
        for key, value in kwargs.items():
            site.__setattr__(key, value)
        if commit:
            session.commit()


Base.metadata.create_all(engine)

#!/usr/bin/python
# -*- coding: utf-8 -*-
from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine import create_engine
from config.settings import settings
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine(f"sqlite:///{settings.SQLITE_PATH}", pool_size=10, max_overflow=20)

Session = sessionmaker(bind=engine)

db_session = Session()


class APIInfo(Base):
    __tablename__ = 'api_info'

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    api_number = Column(String(255), comment="API编号")
    name = Column(String(255), comment="API名称")
    url = Column(String(255), comment="API URL")
    method = Column(String(255), comment="API请求方法")
    params = Column(String(255), comment="API请求参数")
    content_type = Column(String(255), comment="API请求头")
    request_body = Column(String(255), comment="API请求体")
    need_input_params = Column(String(255), comment="输入参数", default="")

    def to_dict(self):
        return {
            "id": self.id, "api_number": self.api_number, "name": self.name, "url": self.url, "method": self.method,
            "params": self.params, "content_type": self.content_type, "request_body": self.request_body,
            "need_input_params": self.need_input_params
        }
# Base.metadata.create_all(engine)

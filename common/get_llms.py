#!/usr/bin/python
# -*- coding: utf-8 -*-
import threading

from langchain_deepseek import ChatDeepSeek
import os
from dotenv import load_dotenv

load_dotenv()


class LLM:
    _llm = None
    _instance_lock = threading.Lock()

    def __new__(cls):
        if not hasattr(cls, '_instance'):
            with cls._instance_lock:
                cls._instance = super().__new__(cls)
                cls._llm = ChatDeepSeek(model="deepseek-chat", temperature=0.6, streaming=True)
        return cls._instance

    def get_llm(self):
        return self._llm

# print(embeddings.embed_documents(["你好", "世界"]))
# print(embeddings)
# print(LLM().get_llm())

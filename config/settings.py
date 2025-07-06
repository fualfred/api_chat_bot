#!/usr/bin/python
# -*- coding: utf-8 -*-
import os


class Settings:
    BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOGS_PATH = os.path.join(BASE_PATH, "logs")
    API_TF_IDF_PATH = os.path.join(BASE_PATH, 'tfidf_vectorizer')
    SQLITE_PATH = os.path.join(BASE_PATH, 'api.db')
    CHECK_POINTER_DIR_PATH = os.path.join(BASE_PATH, 'checkpointer')
    CHECK_POINTER_PATH = os.path.join(CHECK_POINTER_DIR_PATH, 'checkpoint.db')


settings = Settings()
# print(settings.API_DOC_PATH)
# print(settings.CHECK_POINTER_PATH)

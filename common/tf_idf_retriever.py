#!/usr/bin/python
# -*- coding: utf-8 -*-
from langchain_community.retrievers import TFIDFRetriever
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from common.utils import parse_openapi_json
from config.settings import settings


def get_if_idf_retriever_by_file(file_path):
    try:
        loader = TextLoader(file_path)
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_overlap=200, chunk_size=200)
        splits = text_splitter.split_documents(docs)
        retriever = TFIDFRetriever.from_documents(splits)
        return retriever
    except Exception as e:
        raise Exception(e)


def save_local(retriever, file_path):
    retriever.save_local(file_path)


def load_local(file_path, allow_dangerous_deserialization=True):
    return TFIDFRetriever.load_local(file_path, allow_dangerous_deserialization=allow_dangerous_deserialization)


def get_retriever_from_text(text: List[str]):
    retriever = TFIDFRetriever.from_texts(text)
    return retriever


if __name__ == "__main__":
    # api_project = parse_openapi_json('http://127.0.0.1:8080/openapi.json')
    # apis = api_project.apis
    # text = []
    # for i in range(len(apis)):
    #     api_text = "N{:03d}".format(i) + "_" + "_".join(apis[i].tags)
    #     text.append(api_text)
    # tf_idf_retriever = get_retriever_from_text(text)
    # save_local(tf_idf_retriever, settings.API_TF_IDF_PATH)
    # tf_idf_retriever = load_local(settings.API_TF_IDF_PATH)
    # docs = tf_idf_retriever.invoke('Service')
    # for doc in docs:
    #     print(doc.page_content)
    pass
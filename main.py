#!/usr/bin/python
# -*- coding: utf-8 -*-
import sqlite3

import uvicorn
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from common.work_flow import AgentState, command_node, http_node, collection_params_node, retriever_node, where_to_go, \
    collection_after, reset_node, command_after
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.sqlite import SqliteSaver
from config.settings import settings

from fastapi_offline import FastAPIOffline
from pydantic import BaseModel

app = FastAPIOffline()


class RequestModel(BaseModel):
    thread_id: str
    user_input: str


class ThreadModel(BaseModel):
    thread_id: str


def start_graph():
    work_flow = StateGraph(AgentState)
    # memory = InMemorySaver()
    conn = sqlite3.connect(settings.CHECK_POINTER_PATH, check_same_thread=False)

    memory = SqliteSaver(conn)

    work_flow.add_node('command_node', command_node)
    work_flow.add_node('http_node', http_node)
    work_flow.add_node('collection_params_node', collection_params_node)
    work_flow.add_node('retriever_node', retriever_node)
    work_flow.add_node('reset_node', reset_node)

    work_flow.add_conditional_edges(START, where_to_go,
                                    {'retriever_node': 'retriever_node', 'command_node': 'command_node',
                                     'collection_params_node': 'collection_params_node',
                                     '__end__': END, 'reset_node': 'reset_node'})
    work_flow.add_edge('reset_node', END)
    work_flow.add_conditional_edges('command_node', command_after, {'__end__': END, 'http_node': 'http_node'})
    work_flow.add_conditional_edges('collection_params_node', collection_after,
                                    {'http_node': 'http_node', '__end__': END})
    work_flow.add_edge('http_node', END)
    work_flow.add_edge('retriever_node', END)

    graph = work_flow.compile(checkpointer=memory)
    return graph


# graph_png = graph.get_graph().draw_mermaid_png()
#
# with open('graph.png', 'wb') as f:
#     f.write(graph_png)
# _graph = start_graph()
# config = {"configurable": {"thread_id": "2"}}
# while True:
#     user_input = input("请输入：")
#     context = _graph.get_state(config=config).values.get("context", {})
#     response = _graph.invoke({'messages': [HumanMessage(content=user_input)], 'context': context}, config=config)
#     print(f"response: {response}")
# print(context)

_graph = start_graph()


@app.post("/api/graph")
def request_graph(request: RequestModel):
    config = {"configurable": {"thread_id": request.thread_id}}
    context = _graph.get_state(config=config).values.get("context", {})
    response = _graph.invoke({'messages': [HumanMessage(content=request.user_input)], 'context': context},
                             config=config)
    return response


@app.post("/api/state")
def get_state(request: ThreadModel):
    config = {"configurable": {"thread_id": request.thread_id}}
    state = _graph.get_state(config=config)
    return state


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
# gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

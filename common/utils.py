#!/usr/bin/python
# -*- coding: utf-8 -*-
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from common.models import ApiItem, ApiProject
from pathlib import Path
from urllib.parse import urlparse
import json
import requests
from common.database_model import db_session, APIInfo

session = requests.Session()


# 解析fastapi的openapi.json文件
def parse_openapi_json(fast_openapi_json_url: str) -> ApiProject:
    loader = WebBaseLoader(fast_openapi_json_url, encoding="utf-8")
    docs = loader.load()
    content_dict = json.loads(docs[0].page_content)
    # 项目名
    project_name = content_dict['info']['title']
    schemas_dict = content_dict['components']['schemas']

    api_item_list = list()
    for path, methods in content_dict['paths'].items():
        for method, api in methods.items():
            url = path
            tags = api.get('tags')
            summary = api.get('summary', "")
            description = api.get('description', "")
            request_body = api.get('requestBody', "")
            params = api.get('parameters', "")
            if request_body:
                content_type_body = request_body.get('content')
                if content_type_body:
                    content_type = list(content_type_body.keys())[0]
                else:
                    content_type = 'application/json'
            else:
                content_type = ""
            api_item = ApiItem(summary=summary, description=description, url=url, method=method, params=params,
                               content_type=content_type,
                               request_body=request_body, tags=tags)
            api_item_list.append(api_item)
    for api_item in api_item_list:
        if api_item.method.lower() == 'post':
            new_request_body = {}
            ref_path = api_item.request_body.get('content').get('application/json').get('schema').get('$ref')
            mode_name = Path(ref_path).name
            if mode_name in schemas_dict:
                for key, value in schemas_dict[mode_name].items():
                    if key == 'properties':
                        for k, v in value.items():
                            new_request_body[k] = v.get('default') if 'default' in v else ""
            api_item.request_body = new_request_body
    # 解析base_url
    parsed = urlparse(fast_openapi_json_url)
    base_url = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme else f"{parsed.netloc}"
    return ApiProject(base_url=base_url, apis=api_item_list, project_name=project_name)


def create_txt_document(api_str, project_name):
    with open(f"{project_name}.txt", 'w', encoding='utf-8') as f:
        f.write(api_str)


def create_text_from_api(api_project: ApiProject):
    apis = api_project.apis
    api_str = ""
    for api in apis:
        api_str += f"【接口名称】\n {'-'.join(api.tags)}\n"
        api_str += f"\n【接口功能】\n {'-'.join(api.tags)}\n"
        api_str += f"\n【请求方式】\n {api.method.upper()}\n"
        api_str += f"\n 【content-type】\n {api.content_type}\n"
        api_str += f"\n【请求地址】\n {apis.base_url}/{api.url}\n"
        api_str += f"\n【接口摘要】\n{api.summary}\n"
        api_str += f"\n【接口描述】\n{api.description}\n"
        api_str += f"\n【请求示例】\n{json.dumps(api.request_body, indent=4, ensure_ascii=False) if api.request_body else json.dumps({})}\n"
        api_str += "\n"
    return api_str


def request_api(url, method, params=None, request_body=None, content_type="application/json"):
    try:
        response = None
        if method.lower() == 'get':
            response = session.get(url, params=params, headers={'Content-Type': content_type}).json()
        elif method.lower() == 'post':
            response = session.post(url, data=json.dumps(request_body),
                                    headers={'Content-Type': content_type}).json()
        else:
            pass
    except Exception as e:
        response = json.dumps({'status_code': 500, 'error': str(e), 'message': '请求失败，稍后重试'})

    return response


def is_json_with_single_quotes(s):
    try:
        # 替换单引号为双引号
        s = s.replace("'", '"')
        return isinstance(json.loads(s), (dict, list))
    except (json.JSONDecodeError, TypeError):
        return False


def splitter_text(url):
    api_project = parse_openapi_json(url)
    api_str = create_text_from_api(api_project)
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = splitter.split_text(api_str)
    return splits


def save_api_info_db(url):
    try:
        api_project = parse_openapi_json(url)
        apis = api_project.apis
        base_url = api_project.base_url
        for i in range(len(apis)):
            api = apis[i]
            params = api.params if api.params else ""
            api_info = APIInfo(url=base_url + api.url, method=api.method, params=str(params),
                               request_body=str(api.request_body),
                               content_type=api.content_type, name='-'.join(api.tags), api_number="N{:03d}".format(i))
            db_session.add(api_info)
        db_session.commit()
    except Exception as e:
        db_session.rollback()
        raise


def query_api_info_by_api_number(api_number):
    return db_session.query(APIInfo).filter(APIInfo.api_number == api_number).first()

# save_api_info_db('http://127.0.0.1:8080/openapi.json')

# api_info = query_api_info_by_api_number('N001')
# print(api_info.to_dict())

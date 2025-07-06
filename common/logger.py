#!/usr/bin/python
# -*- coding: utf-8 -*-
from loguru import logger
from config.settings import settings
import os
import threading

# 创建日志目录
if not settings.LOGS_PATH:
    os.mkdir(settings.LOGS_PATH)


class LoguruLogger:
    _instance_lock = threading.Lock()  # 线程锁
    _logger = None

    def __new__(cls):
        if not hasattr(cls, "_instance"):
            with cls._instance_lock:
                if not hasattr(cls, "_instance"):
                    cls._instance = super().__new__(cls)
                    cls._instance._init_logger()

        return cls._instance

    def _init_logger(self):
        """初始化日志配置"""
        log_path = os.path.join(settings.LOGS_PATH, "API_{time:YYYY-MM-DD}.log")

        self._logger = logger
        self._logger.add(
            sink=log_path,
            rotation="20 MB",  # 单个日志文件最大10MB[5](@ref)
            retention="30 days",  # 保留最近30天日志[1](@ref)
            enqueue=True,  # 异步写入防阻塞[5](@ref)
            encoding="utf-8",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {file}:{line} - {message}",
            compression='zip'
        )

    def get_logger(self):
        return self._logger


# 全局访问点
logger = LoguruLogger().get_logger()
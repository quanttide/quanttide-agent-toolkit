"""
定义不同阶段的法律文书模型
"""

# 原本是为了给法律文书的处理写的代码
# 所以定义了每个阶段间传递的数据，方便追踪

from abc import ABC
from datetime import datetime

import numpy as np


class Model(ABC):
    def __init__(self) -> None:
        super().__init__()


class ChunkedText(Model):
    """
    被读取，然后被分割后的模型
    """

    def __init__(self, file_id: str, file_path: str, file_name: str, file_contents: list[str]):
        """
        file_id: 分配的id
        file_path: 原始文件的路径
        file_name: 原始文件的名字
        file_contents: 分割后的文件段
        """
        self.file_id = file_id
        self.file_path = file_path
        self.file_name = file_name
        self.status = "chunked_and_waiting_for_process"
        self.file_contents = file_contents

    def __repr__(self):
        return f"Model_ChunkedText({self.file_id}, {self.file_name}, {self.status})"


class ProcessedText(Model):
    """
    被向量化处理后的模型
    file_id: 分配的id
    file_path: 原始文件的路径
    file_name: 原始文件的名字
    file_contents_with_vector: 一个字典, key为文本, value为文本对应的向量
    """

    def __init__(self, file_id, file_path, file_name, file_contents_with_vector: dict[str, np.ndarray]):
        self.file_id = file_id
        self.file_path = file_path
        self.file_name = file_name
        self.file_contents_with_vector = file_contents_with_vector
        self.status = "processed_and_waiting_for_extrated"

    def __repr__(self):
        return f"ExtractedSegment(file_id={self.file_id}, file_name={self.file_name}, status={self.status})"


class BestMatch(Model):
    def __init__(self, file_id, file_path, file_name, relevant_text: list[str]):
        self.file_id = file_id
        self.file_path = file_path
        self.file_name = file_name
        self.relevant_text = relevant_text  # 字段：前n对应的文本
        self.status = "extracted_segments_and_waiting_for_ask"

    def __repr__(self):
        return f"ExtractedSegment(file_id={self.file_id}, file_name={self.file_name}, status={self.status})"


class TargetFileds(Model):
    def __init__(self, file_id, file_path, file_name, relevant_text, query_id, answer):
        self.file_id = file_id
        self.file_path = file_path
        self.file_name = file_name
        self.relevant_text = relevant_text
        self.query_id = query_id
        self.answer = answer
        self.status = "answered_fields_and_waiting_for_save"
        self.timestamp = datetime.now()

    def __repr__(self):
        return f"SavedResult(file_id={self.file_id}, file_name={self.file_name}, status={self.status}, timestamp={self.timestamp})"


class ErrorRecord(Model):
    def __init__(self, file_id, stage, error_message, retry_count, error_model: Model):
        self.file_id = file_id
        self.stage = stage
        self.error_message = error_message
        self.retry_count = retry_count
        self.status = "an_unexpected_error_occured"
        self.error_model = error_model

    def __repr__(self):
        return f"ErrorRecord(file_id={self.file_id}, stage={self.stage}, error_message={self.error_message}, retry_count={self.retry_count}, status={self.status})"

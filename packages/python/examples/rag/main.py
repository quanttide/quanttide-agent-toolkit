# -*- coding: utf-8 -*-
"""
程序启动入口
"""
import logging

from config import init_logging
from read_file import FileReader
from text_process import TextProcessor
from compare import Comparator
from llms import QWenModel

init_logging()
LOGGER = logging.getLogger(__name__)


def main():
    # 1 阅读文本，分块
    file_path = "test.txt"
    file_reader = FileReader(chunk_pattern='chunk_by_token')
    chunked_model = file_reader.read_and_chunk(file_path)

    # 2 对每一块向量化
    text_processor = TextProcessor()
    vector_model = text_processor.process_model(chunked_model)
    
    # 3 对问题向量化
    question = "Who is the author of the book?"
    vector_text = text_processor.process_text(question)
    
    # 4 比较，获得贴近的向量块
    comparator = Comparator()
    result = comparator.compare(vector_model, vector_text, 5)
    result_text = result.relevant_text
    
    # 5 将对应文本嵌入prompt，并调用LLM回答用户问题
    llm = QWenModel()
    answer = llm.ask_llm(question, result_text[0])
    
    print(answer)



if __name__ == '__main__':
    main()

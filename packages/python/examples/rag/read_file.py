import docx
from chunker import Chunker
from models import ChunkedText

class FileReader:

    # 传入要使用的分割器
    def __init__(self,chunk_pattern):
        self.chunker = Chunker(chunk_pattern)
        self.count = 0

    def read_and_chunk(self,file_path: str ,) ->ChunkedText:
        content = self.read_file_content(file_path)
        contents = self.chunker.chunk(content)
        self.count += 1
        
        return ChunkedText(file_id=self.count,
                           file_path=file_path,
                           file_name=file_path,
                           file_contents=contents
                           )

    # 读取文件内容，传入一个文件路径，返回该文件内容字符串
    @classmethod
    def read_file_content(cls, file_path: str) -> str:
        """
        读取本地文件的内容，提取成字符串
        """
        if file_path.endswith('.md'):
            return cls.read_md_content(file_path)
        elif file_path.endswith('.txt'):
            return cls.read_txt_content(file_path)
        elif file_path.endswith('.docx') or file_path.endswith('.doc'):
            return cls.read_word_content(file_path)

    @classmethod
    def read_md_content(cls, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @classmethod
    def read_txt_content(cls, file_path: str):
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()

    @classmethod
    def read_word_content(cls, file_path: str):
        """
        读取Word文件的内容，提取成字符串
        """
        doc = docx.Document(file_path)
        content = []
        for paragraph in doc.paragraphs:
            content.append(paragraph.text)
        return '\n'.join(content)
    


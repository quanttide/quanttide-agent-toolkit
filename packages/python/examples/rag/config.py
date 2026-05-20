# -*- coding: utf-8 -*-
"""
配置
"""
import logging
from pathlib import Path
import yaml
import dynaconf

settings = dynaconf.Dynaconf(
    # note: absolute path so that tests can run correctly.
    # https://docs.python.org/3/library/pathlib.html#pathlib.PurePath.with_name
    settings_files=[Path(__file__).resolve().with_name('settings.yml')],
    # note: split settings_files and secrets.
    # https://www.dynaconf.com/configuration/#secrets
    secrets=Path(__file__).resolve().with_name('.secrets.yml'),
    environments=True,
    env_switcher='DYNACONF_STAGE',
    load_dotenv=True,
)

# 项目根目录设置为仓库根目录
settings.PROJECT_ROOT = Path(__file__).resolve().parent.parent

# 具体配置
# 大模型使用选择
llm_settins = 'qwen'

#词嵌入模型选择
embedding_settings = 'qwen'

#文本分割选择
chunker_settings = 'default'

#保存方法和路径选择
save_settings = 'default'

def init_logging() -> None:
    """
    初始化logging配置
    :return: None
    """
    logging.basicConfig(level=settings.LOGGING_LEVEL, format=settings.LOGGING_FORMAT)
    # 屏蔽不重要的第三方库DEBUG日志
    # logging.getLogger('urllib3.connectionpool').setLevel(max(logging.INFO, settings.LOGGING_LEVEL))

def load_api_key(model_name) ->str:
    """ 
    读取.secret.yml中的内容
    其内容应该按照
    ```yml
    api_key:
        qwen: sk-XXXXXXXXXXXXXXXXXXXX
    ```
    的形式展开
    """
    file_path = 'information_extractor\\.secrets.yml'
    with open(file_path, 'r', encoding='utf-8') as file:
        secrets = yaml.safe_load(file)
        return secrets['api_key'][model_name]
    
def load_settings() ->dict[str:int]:
    file_path = 'information_extractor\\settings.yml'
    with open(file_path,"r",encoding='utf-8') as file:
        pass


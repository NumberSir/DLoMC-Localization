# 简介
半自动化汉化 Daily Lives of My Countryside 游戏，供汉化组内部使用

# 项目结构
```text
📁root
┣━ 📁data
┃  ┣━ 📁log
┃  ┗━ 📁tmp
┣━ 📁resource
┃  ┣━ 📁00-original
┃  ┃  ┗━ 📁Daily Lives of My Countryside ...
┃  ┣━ 📁01-translation
┃  ┣━ 📁02-paratranz
┃  ┃  ┣━ 📁convert
┃  ┃  ┗━ 📁download
┃  ┣━ 📁03-result
┃  ┣━ 📁04-special-file
┃  ┃  ┗━ 📁www
┃  ┃     ┗━ 📁img
┃  ┃        ┗━ 📁pictures
┃  ┗━ 📁project-img
┃     ┗━ 🖼️icon.png
┣━ 📁src
┣━ ⚙️.env
┣━ ⚙️.env.template
┣━ 📄LICENSE
┣━ 🐍main.py
┣━ ⚙️pyproject.toml
┗━ 📄README.md
```

# 用法
1. 安装 [Python](https://www.python.org/downloads/) 3.8+, 安装必需的库：
    - 安装 [pipx](https://pipx.pypa.io/stable/installation/)
    ```shell
    pip install pipx
    ```
    - 安装 [poetry](https://python-poetry.org/docs/#installation)
    ```shell
    pipx install poetry
    ```
    - 使用 poetry 安装项目依赖
    ```shell
    poetry install
    ```
2. ~~（尚未实现）自动下载最新版游戏，解压至 `./resource/<游戏名>`~~
3. 创建 `./resource` 文件夹，手动下载游戏，解压至 `./resource` 目录下
4. 创建 `.env` 文件，在其中填写 `.env.template` 中示例的环境变量
   ```dotenv
   # 不要直接修改 `.env.template`，而是重新在项目根目录下创建一个新的 `.env` 文件再做修改
   # 必填字段均已标注出来，未标注的均是有默认值的可选字段，若不进行改动可以删除字段
   # 模板文件中已填写字段的值均为默认值
   # 值有空格时需用引号 " 或 ' 包裹
   
   ### PROJECT ###
   # name, version, username 和 email 为构建 `User-Agent` 时用
   # 格式: `User-Agent: <PROJECT_USERNAME>/<PROJECT_NAME>/<PROJECT_VERSION> (<PROJECT_EMAIL>)`
   PROJECT_NAME=DLoMC-Localization
   PROJECT_VERSION=0.0.1
   PROJECT_USERNAME=Anonymous
   PROJECT_EMAIL=anonymous@email.com
   # 可改为 `DEBUG`, `WARN` 等
   PROJECT_LOG_LEVEL=INFO
   # "extra[project_name]" 与 `PROJECT_NAME` 的值一致
   PROJECT_LOG_FORMAT="<g>{time:HH:mm:ss}</g> | [<lvl>{level:^7}</lvl>] | {extra[project_name]}{message:<35}{extra[filepath]}"
   
   ### FILEPATH ###
   # 所有路径均相对于本项目的根目录
   PATH_DATA=data
   # 临时文件存放处，如下载文件、临时生成数据文件等
   # tmp 会在每次运行脚本时自动清理/重建
   PATH_TMP=data/tmp
   # 存储自动生成的日志文件
   PATH_LOG=data/log
   # 项目所需大文件/脚本自动生成的游戏文件存放处
   PATH_RESOURCE=resource
   # 游戏原文件存放处
   PATH_ORIGINAL=resource/00-original
   # 已有汉化文件，手动放置
   PATH_TRANSLATION=resource/01-translation
   # 提取游戏原文件并结合已有汉化后生成的文件，需上传至 Paratranz 平台
   PATH_CONVERT=resource/02-paratranz/convert
   # 从 Paratranz 平台下载的汉化文件
   PATH_DOWNLOAD=resource/02-paratranz/download
   # 用 Paratranz 平台下载的汉化文件覆盖替换游戏原文件的结果，需手动替换游戏原文件
   PATH_RESULT=resource/03-result
   # 一些无法经常规文本替换汉化的游戏原文件，如图片等
   PATH_SPECIAL=resource/04-special-file
   
   ### GAME ###
   # 游戏名称，不带版本号
   GAME_NAME="Daily Lives of My Countryside"
   # !!!必填字段!!!
   # 游戏版本号，游戏文件夹默认名称末尾，如 0.3.2.1
   GAME_VERSION=
   
   ### GITHUB ###
   # !!!必填字段!!!
   GITHUB_ACCESS_TOKEN=
   
   ### PARATRANZ ###
   # !!!必填字段!!!
   PARATRANZ_PROJECT_ID=
   # !!!必填字段!!!
   PARATRANZ_TOKEN=
   ```
5. 运行根目录下的 `main.py`
   ```shell
   python -m main
   ```
6. `./resource/02-paratranz/convert` 中会生成处理后的原文件，需要手动上传到 Paratranz 项目根目录下
7. `./resource/02-paratranz/download` 中会生成自动下载好的原文-汉化字典，若没有说明你的 Paratranz 项目中没有汉化文件，或 Paratranz 项目结构不对
8. `./resource/03-result` 中会生成替换完毕的汉化文件，需要将其手动覆盖替换游戏原文件
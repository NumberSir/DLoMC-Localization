# 简介
半自动化汉化 Daily Lives of My Countryside 游戏，供汉化组内部使用

# 项目结构
```text
📁root
┣━ 📁data
┃  ┣━ 📁log
┃  ┗━ 📁tmp
┣━ 📁resource
┃  ┣━ 📁Daily Lives of My Countryside ...
┃  ┗━ 📁translation
┣━ 📁src
┣━ ⚙️.env
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
   # tmp 会在每次运行脚本时自动清理/重建
   PATH_TMP=data/tmp
   PATH_LOG=data/log
   PATH_RESOURCE=resource
   
   ### GAME ###
   # 游戏名称，不带版本号
   GAME_NAME="Daily Lives of My Countryside"
   # !!!必填字段!!!
   # 游戏版本号，游戏文件夹默认名称末尾，如 0.3.2.1
   GAME_VERSION=
   
   ### GITHUB ###
   # !!!必填字段!!!
   GITHUB_ACCESS_TOKEN=
   ```
5. 运行根目录下的 `main.py`
   ```shell
   python -m main
   ```
6. `./resource/paratranz/convert` 中会生成处理后的原文件，需要手动上传到 Paratranz 项目根目录下
7. `./resource/paratranz/download` 中会生成自动下载好的原文-汉化字典，若没有说明你的 Paratranz 项目中没有汉化文件，或 Paratranz 项目结构不对
8. `./resource/result` 中会生成替换完毕的汉化文件，需要将其手动覆盖替换游戏原文件
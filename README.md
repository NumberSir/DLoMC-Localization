# 简介
半自动化汉化 Daily Lives of My Countryside 游戏，供汉化组内部使用

# 项目结构
```text
📁root
┣━ 📁data
┃  ┣━ 📁log
┃  ┗━ 📁tmp
┣━ 📁dist
┣━ 📁resource
┃  ┣━ 📁01-original
┃  ┃  ┗━ 📁Daily Lives of My Countryside v<VERSION>
┃  ┣━ 📁02-paratranz
┃  ┃  ┣━ 📁convert
┃  ┃  ┗━ 📁download
┃  ┣━ 📁03-result
┃  ┣━ 📁04-special-file
┃  ┃  ┗━ 📁www
┃  ┃     ┣━ 📁img
┃  ┃     ┗━ 📁js
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

# 使用前
1. 你的电脑上需要有 [Python][Python] 3.10 环境
~~2. 你需要能够访问 [SubscribeStar][SubscribeStar] 和 [Mega][Mega] 网站的网络环境~~
~~3. 你需要注册一个 [SubscribeStar][SubscribeStar] 账号，并关闭账号的多因素认证（如果有开启的话）：~~
   ~~1. 打开`账号设置 (Account Settings)`~~
   ~~2. 找到最下方的`安全 (Security)` 部分~~
      ~~- 如果有框选，则取消框选 `Two-Factor E-mail Authentication` 选项~~
      ~~- 如果有框选，则取消框选 `Quick E-mail Code Login` 选项~~
   ~~3. 找到更下方的`验证器 (Authenticator Apps)` 部分~~
      ~~- 如果之前设置过验证器，则点击 `Manage OTP Settings`~~
      ~~- 点击 `Disable OTP`~~
   ~~4. 找到更更下方的`通行秘钥验证 (Passkey Authentication)` 部分~~
      ~~- 如果之前设置过通行秘钥，则点击对应秘钥右上角的垃圾桶图标删除该秘钥~~

# 使用说明
1. 安装本项目必需的库：
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
2. ~~（尚未实现）自动下载最新版游戏，解压至 `./resource/01-original/<游戏名>`~~
3. 创建 `./resource/01-original` 文件夹，手动下载游戏，解压至 `./resource/01-original` 目录下
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
   # 项目结果导出为压缩包的存放目录
   PATH_DIST=dist
   # 项目所需大文件/脚本自动生成的游戏文件存放处
   PATH_RESOURCE=resource
   # 游戏原文件存放处
   PATH_ORIGINAL=resource/01-original
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
   # 游戏中文名称，不带版本号
   GAME_NAME_TRANSLATION=我的乡村日常生活
   # !!!必填字段!!!
   # 游戏版本号，游戏文件夹默认名称末尾，如 0.3.2.1
   GAME_VERSION=
   
   ### GITHUB ###
   # !!!必填字段!!!
   # GitHub 个人 personal access token
   GITHUB_ACCESS_TOKEN=
   
   ### PARATRANZ ###
   # !!!必填字段!!!
   # Paratranz 项目 ID，纯数字
   PARATRANZ_PROJECT_ID=
   # !!!必填字段!!!
   # Paratranz 个人 access token
   PARATRANZ_TOKEN=
   ```
5. 运行根目录下的 `main.py`
   ```shell
   python -m main
   ```
6. `./resource/02-paratranz/convert` 中会生成处理后的原文件，需要手动上传到 Paratranz 项目根目录下
7. `./resource/02-paratranz/download` 中会生成自动下载好的原文-汉化字典，若没有说明你的 Paratranz 项目中没有汉化文件，或 Paratranz 项目结构不对
8. `./resource/03-result` 中会生成替换完毕的汉化文件，需要将其手动覆盖替换游戏原文件。
   - 不要替换 `./resource/01-original` 中的游戏原文件！
   - 最好将游戏原文件复制一份到其他地方，单独覆盖游玩，保留 `./resource/01-original` 中的游戏原文件供文本提取用
9. `./dist` 中会生成结果的压缩包。压缩包末尾的两个数字分别为万分之翻译进度和万分之审核进度


[SubscribeStar]: https://subscribestar.adult/
[Python]: https://www.python.org/downloads/
[Mega]: https://mega.nz/
最终软件包说明（二次开发）

目录结构
- app\  运行版 EXE
- src\  源代码与资源、构建脚本

快速构建
1) Windows 打开 src\ 目录，双击运行 build.bat
   - 自动创建虚拟环境 .venv
   - 安装依赖（requirements.txt）与 PyInstaller
   - 打包生成 EXE 到上级 app\
2) 也可在 src\ 手动执行：
   - python -m venv .venv
   - .venv\Scripts\activate
   - pip install -r requirements.txt
   - pip install pyinstaller
   - pyinstaller -F -w -n "大飞哥软件自习室—本地账号密码管理器" --icon "安卓手机清新系统7.ico" --add-data "支付宝(支付完联系电话：18603298215).jpg;." --add-data "安卓手机清新系统7.ico;." main.py --distpath ..\app

运行与数据
- 首次运行会在 EXE 同目录生成：
  - saved_accounts.json（加密数据文件）
  - secret.key（密钥文件，软件会自动生成；丢失则无法解密数据）
- 若设置了软件密码，启动会提示输入；可在“软件加密”里取消或更改。

开发注意事项
- 图标：窗口图标与 EXE 图标使用 src\安卓手机清新系统7.ico
- 赞助图片：src\支付宝(支付完联系电话：18603298215).jpg
- 主题：在 theme.py 的 apply_pink_theme 调整全局样式
- 打包配置：可编辑 src\*.spec，或直接用 build.bat 的命令行

版权与分发
- 生成的 app\EXE 可直接分发给用户，无需 Python 环境。
- 请勿将个人环境下生成的 secret.key 一并分发；用户运行时会自动生成自己的密钥。
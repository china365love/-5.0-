@echo off
setlocal
pushd %~dp0

REM 检查 Python
where python >nul 2>&1
if errorlevel 1 (
  echo 未检测到 Python，请先安装 Python 3.9+ 并添加到 PATH。
  exit /b 1
)

REM 创建并激活虚拟环境
python -m venv .venv
call .venv\Scripts\activate

REM 安装依赖及打包工具
python -m pip install -U pip
pip install -r requirements.txt
pip install pyinstaller

REM 构建 EXE（带图标与内置资源）
pyinstaller -F -w -n "大飞哥软件自习室—本地账号密码管理器" --icon "安卓手机清新系统7.ico" --add-data "支付宝(支付完联系电话：18603298215).jpg;." --add-data "安卓手机清新系统7.ico;." main.py --distpath .\out

if %errorlevel% neq 0 (
  echo 构建失败，请检查控制台错误信息。
  exit /b %errorlevel%
)

echo 构建完成：out\大飞哥软件自习室—本地账号密码管理器.exe
popd
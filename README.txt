使用说明\n\n1. 安装依赖并打包为exe
   - 打开PowerShell到本目录
   - 执行: pip install -r requirements.txt
   - 执行: pyinstaller -F -w -n "大飞哥软件自习室—本地账号密码管理器" --add-data "支付宝(支付完联系电话：18603298215).jpg;." main.py
   - 生成的exe位于 dist/大飞哥软件自习室—本地账号密码管理器.exe\n\n2. 首次运行\n   - 会在软件根目录生成 saved_accounts.json 与 secret.key\n   - 可在“软件加密”中设置启动密码，设置后每次启动需输入该密码\n\n3. 数据\n   - 所有记录统一加密存储在 saved_accounts.json\n   - secret.key 为解密密钥文件，请务必妥善保管；丢失即永久无法解密数据\n\n4. CSV导入/导出\n   - 导入至少包含 account、password 字段，网站/手机/邮箱/备注可选\n   - 导出会包含所有字段供备份\n\n5. 其他\n   - 双击表格记录可复制密码；根据“密码清除”选项自动清空剪贴板\n   - 删除记录不可恢复。\n
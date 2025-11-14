import os
import sys
import time
import random
import string
from typing import List, Dict

from PyQt5 import QtCore, QtGui, QtWidgets

from storage import SecureStorage, KeyManager, app_root


class PasswordManagerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('大飞哥软件自习室—本地账号密码管理器')
        self.resize(1280, 800)
        # 设置自定义窗口图标（在打包环境与开发环境均可用）
        icon_name = '安卓手机清新系统7.ico'
        candidate_paths = []
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            candidate_paths.append(os.path.join(getattr(sys, '_MEIPASS'), icon_name))
        candidate_paths.append(os.path.join(app_root(), icon_name))
        icon_path = next((p for p in candidate_paths if os.path.exists(p)), None)
        if icon_path:
            self.setWindowIcon(QtGui.QIcon(icon_path))

        # Models
        self.key_mgr = KeyManager()
        # 启动时尝试加载，如果secret.key已加密，则弹窗输入密码
        self._ensure_unlock_key()
        self.store = SecureStorage(self.key_mgr)
        self.store.load()

        # Clipboard清理设置
        self.clear_clip_after = 10  # 秒
        self.clipboard = QtWidgets.QApplication.clipboard()
        self.clear_timer = QtCore.QTimer(self)
        self.clear_timer.setSingleShot(True)
        self.clear_timer.timeout.connect(self._clear_clipboard)

        # 顶部操作按钮
        top = QtWidgets.QWidget()
        top_layout = QtWidgets.QHBoxLayout(top)
        for title, handler in [
            ('支持输出', self.on_export),
            ('存储记录', self.on_show_records),
            ('导入数据', self.on_import),
            ('软件加密', self.on_set_password),
            ('使用必读', self.on_show_usage),
            ('赞助支持', self.on_support)
        ]:
            btn = QtWidgets.QPushButton(title)
            btn.clicked.connect(handler)
            top_layout.addWidget(btn)
        top_layout.addStretch(1)

        # 自动生成区域
        auto_group = QtWidgets.QGroupBox('自动生成')
        ag = QtWidgets.QGridLayout(auto_group)
        self.web_auto = QtWidgets.QLineEdit()
        self.mail_auto = QtWidgets.QLineEdit()
        self.phone_auto = QtWidgets.QLineEdit()
        self.note_auto = QtWidgets.QLineEdit()
        ag.addWidget(QtWidgets.QLabel('网站:'), 0, 0)
        ag.addWidget(self.web_auto, 0, 1)
        ag.addWidget(QtWidgets.QLabel('邮箱:'), 0, 2)
        ag.addWidget(self.mail_auto, 0, 3)
        ag.addWidget(QtWidgets.QLabel('手机:'), 0, 4)
        ag.addWidget(self.phone_auto, 0, 5)
        ag.addWidget(QtWidgets.QLabel('备注:'), 1, 0)
        ag.addWidget(self.note_auto, 1, 1, 1, 5)

        self.len_user = QtWidgets.QSpinBox(); self.len_user.setRange(4, 64); self.len_user.setValue(8)
        self.acc_upper = QtWidgets.QCheckBox('大写'); self.acc_upper.setChecked(True)
        self.acc_lower = QtWidgets.QCheckBox('小写'); self.acc_lower.setChecked(True)
        self.acc_digits = QtWidgets.QCheckBox('数字'); self.acc_digits.setChecked(True)
        ag.addWidget(QtWidgets.QLabel('账号长度:'), 2, 0)
        ag.addWidget(self.len_user, 2, 1)
        ag.addWidget(self.acc_upper, 2, 2)
        ag.addWidget(self.acc_lower, 2, 3)
        ag.addWidget(self.acc_digits, 2, 4)

        self.len_pwd = QtWidgets.QSpinBox(); self.len_pwd.setRange(6, 128); self.len_pwd.setValue(12)
        self.pw_upper = QtWidgets.QCheckBox('大写'); self.pw_upper.setChecked(True)
        self.pw_lower = QtWidgets.QCheckBox('小写'); self.pw_lower.setChecked(True)
        self.pw_digits = QtWidgets.QCheckBox('数字'); self.pw_digits.setChecked(True)
        self.pw_symbols = QtWidgets.QCheckBox('符号'); self.pw_symbols.setChecked(True)
        ag.addWidget(QtWidgets.QLabel('密码长度:'), 3, 0)
        ag.addWidget(self.len_pwd, 3, 1)
        ag.addWidget(self.pw_upper, 3, 2)
        ag.addWidget(self.pw_lower, 3, 3)
        ag.addWidget(self.pw_digits, 3, 4)
        ag.addWidget(self.pw_symbols, 3, 5)

        self.gen_count = QtWidgets.QSpinBox(); self.gen_count.setRange(1, 50); self.gen_count.setValue(1)
        self.btn_generate = QtWidgets.QPushButton('开始生成')
        self.btn_generate.clicked.connect(self.on_generate)
        ag.addWidget(QtWidgets.QLabel('生成数量:'), 4, 0)
        ag.addWidget(self.gen_count, 4, 1)
        ag.addWidget(self.btn_generate, 4, 2)

        # 手动录入区域
        manual_group = QtWidgets.QGroupBox('手动录入（*为必填项）')
        mg = QtWidgets.QGridLayout(manual_group)
        self.web = QtWidgets.QLineEdit()
        self.account = QtWidgets.QLineEdit()
        self.password = QtWidgets.QLineEdit(); self.password.setEchoMode(QtWidgets.QLineEdit.Password)
        self.phone = QtWidgets.QLineEdit()
        self.email = QtWidgets.QLineEdit()
        self.note = QtWidgets.QLineEdit()
        mg.addWidget(QtWidgets.QLabel('网站:'), 0, 0)
        mg.addWidget(self.web, 0, 1, 1, 3)
        mg.addWidget(QtWidgets.QLabel('账号:*'), 0, 4)
        mg.addWidget(self.account, 0, 5)
        mg.addWidget(QtWidgets.QLabel('密码:*'), 0, 6)
        mg.addWidget(self.password, 0, 7)
        mg.addWidget(QtWidgets.QLabel('手机:'), 1, 0)
        mg.addWidget(self.phone, 1, 1)
        mg.addWidget(QtWidgets.QLabel('邮箱:'), 1, 2)
        mg.addWidget(self.email, 1, 3)
        mg.addWidget(QtWidgets.QLabel('备注:'), 1, 4)
        mg.addWidget(self.note, 1, 5, 1, 3)
        self.btn_save = QtWidgets.QPushButton('保存录入')
        self.btn_save.clicked.connect(self.on_save_manual)
        mg.addWidget(self.btn_save, 2, 0, 1, 1)

        # 搜索与选项
        bottom_opts = QtWidgets.QWidget()
        bo = QtWidgets.QHBoxLayout(bottom_opts)
        self.search_edit = QtWidgets.QLineEdit(); self.search_edit.setPlaceholderText('搜索网站/账号/邮箱/手机号/备注')
        btn_search = QtWidgets.QPushButton('搜索'); btn_search.clicked.connect(self.on_search)
        bo.addWidget(QtWidgets.QLabel('搜索:'))
        bo.addWidget(self.search_edit)
        bo.addWidget(btn_search)

        bo.addWidget(QtWidgets.QLabel('密码清除:'))
        self.rb_never = QtWidgets.QRadioButton('永不'); self.rb_never.toggled.connect(self.on_clear_choice)
        self.rb_10 = QtWidgets.QRadioButton('10秒'); self.rb_10.setChecked(True); self.rb_10.toggled.connect(self.on_clear_choice)
        self.rb_30 = QtWidgets.QRadioButton('30秒'); self.rb_30.toggled.connect(self.on_clear_choice)
        bo.addWidget(self.rb_never); bo.addWidget(self.rb_10); bo.addWidget(self.rb_30)
        self.cb_show_pwd = QtWidgets.QCheckBox('显示密码'); self.cb_show_pwd.toggled.connect(self.on_toggle_show_password)
        bo.addWidget(self.cb_show_pwd)

        # 记录表
        self.table = QtWidgets.QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels(['网站', '账号', '密码', '手机', '邮箱', '备注', '创建时间'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        # 交互：双击复制，点击网址打开浏览器
        self.table.doubleClicked.connect(self.on_table_double_click)
        self.table.cellClicked.connect(self.on_table_cell_clicked)

        # 底部操作
        bottom_action = QtWidgets.QWidget()
        ba = QtWidgets.QHBoxLayout(bottom_action)
        btn_delete = QtWidgets.QPushButton('删除选中记录')
        btn_delete.clicked.connect(self.on_delete_selected)
        ba.addWidget(btn_delete)
        ba.addStretch(1)

        # 主布局
        central = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout(central)
        lay.addWidget(top)
        lay.addWidget(auto_group)
        lay.addWidget(manual_group)
        lay.addWidget(bottom_opts)
        lay.addWidget(self.table)
        lay.addWidget(bottom_action)
        # 底部版权链接
        footer = QtWidgets.QLabel()
        footer.setText('<a href="https://space.bilibili.com/286436365" style="color:#c2185b; text-decoration:none; font-weight:bold">大飞哥软件自习室荣誉出品</a>')
        footer.setAlignment(QtCore.Qt.AlignCenter)
        footer.setOpenExternalLinks(True)
        lay.addWidget(footer)
        self.setCentralWidget(central)

        self.refresh_table()

    def _ensure_unlock_key(self):
        # 如果secret.key已加密，弹出密码输入
        try:
            self.key_mgr.load(password=None)
        except Exception:
            dlg = QtWidgets.QInputDialog(self)
            dlg.setWindowTitle('解锁软件密码')
            dlg.setLabelText('请输入启动密码以解锁:')
            dlg.setTextEchoMode(QtWidgets.QLineEdit.Password)
            if dlg.exec_() == QtWidgets.QDialog.Accepted:
                pwd = dlg.textValue()
                self.key_mgr.load(password=pwd)
            else:
                QtWidgets.QMessageBox.critical(self, '错误', '必须输入密码才能继续。')
                sys.exit(1)

    # UI helpers
    def add_row(self, rec: Dict):
        row = self.table.rowCount()
        self.table.insertRow(row)
        cols = ['website', 'account', 'password', 'phone', 'email', 'note', 'created_at']
        for i, k in enumerate(cols):
            val = rec.get(k, '')
            if k == 'created_at':
                val = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(val))
            item = QtWidgets.QTableWidgetItem(str(val))
            if k == 'password' and not self.cb_show_pwd.isChecked():
                item.setText('******')
            self.table.setItem(row, i, item)

    def refresh_table(self, data: List[Dict] = None):
        if data is None:
            data = self.store.accounts
        self.table.setRowCount(0)
        for rec in data:
            self.add_row(rec)

    # Generation
    def _build_charset(self, upper, lower, digits, symbols=False):
        cs = ''
        if upper: cs += string.ascii_uppercase
        if lower: cs += string.ascii_lowercase
        if digits: cs += string.digits
        if symbols: cs += '!@#$%^&*()-_=+[]{};:,./?'
        if not cs:
            cs = string.ascii_letters + string.digits
        return cs

    def random_string(self, length: int, cs: str) -> str:
        return ''.join(random.choice(cs) for _ in range(length))

    def on_generate(self):
        acc_cs = self._build_charset(self.acc_upper.isChecked(), self.acc_lower.isChecked(), self.acc_digits.isChecked())
        pw_cs = self._build_charset(self.pw_upper.isChecked(), self.pw_lower.isChecked(), self.pw_digits.isChecked(), self.pw_symbols.isChecked())
        count = self.gen_count.value()
        for _ in range(count):
            rec = {
                'website': self.web_auto.text().strip(),
                'account': self.random_string(self.len_user.value(), acc_cs),
                'password': self.random_string(self.len_pwd.value(), pw_cs),
                'phone': self.phone_auto.text().strip(),
                'email': self.mail_auto.text().strip(),
                'note': self.note_auto.text().strip(),
                'created_at': int(time.time())
            }
            self.store.add(rec)
        self.refresh_table()
        QtWidgets.QMessageBox.information(self, '完成', f'已生成{count}条记录')

    def on_save_manual(self):
        acc = self.account.text().strip()
        pwd = self.password.text().strip()
        if not acc or not pwd:
            QtWidgets.QMessageBox.warning(self, '提示', '账号与密码为必填')
            return
        rec = {
            'website': self.web.text().strip(),
            'account': acc,
            'password': pwd,
            'phone': self.phone.text().strip(),
            'email': self.email.text().strip(),
            'note': self.note.text().strip(),
            'created_at': int(time.time())
        }
        self.store.add(rec)
        self.refresh_table()
        self.account.clear(); self.password.clear()
        QtWidgets.QMessageBox.information(self, '完成', '记录已保存')

    def on_search(self):
        q = self.search_edit.text()
        self.refresh_table(self.store.search(q))

    def on_delete_selected(self):
        rows = sorted(set([r.row() for r in self.table.selectedIndexes()]), reverse=True)
        if not rows:
            return
        if QtWidgets.QMessageBox.question(self, '确认', '删除选中记录将不可恢复，确认删除？') == QtWidgets.QMessageBox.Yes:
            for r in rows:
                self.store.delete_by_index(r)
            self.refresh_table()

    def on_table_cell_clicked(self, row: int, col: int):
        # 单击网址列直接在浏览器打开
        if col == 0:
            rec = self.store.accounts[row]
            url = (rec.get('website', '') or '').strip()
            if url:
                if not (url.startswith('http://') or url.startswith('https://')):
                    url = 'http://' + url
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))

    def on_table_double_click(self, index: QtCore.QModelIndex):
        row = index.row(); col = index.column()
        rec = self.store.accounts[row]
        if col == 0:
            # 网址列：同样支持双击打开
            url = (rec.get('website', '') or '').strip()
            if url:
                if not (url.startswith('http://') or url.startswith('https://')):
                    url = 'http://' + url
                QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
            return
        # 其他列：双击复制真实值
        fields = ['website', 'account', 'password', 'phone', 'email', 'note', 'created_at']
        key = fields[col]
        val = rec.get(key, '')
        if key == 'created_at' and isinstance(val, int):
            val = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(val))
        self.clipboard.setText(str(val))
        if self.clear_clip_after > 0:
            self.clear_timer.start(self.clear_clip_after * 1000)
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), '内容已复制到剪贴板')

    def _clear_clipboard(self):
        self.clipboard.clear()

    def on_clear_choice(self):
        if self.rb_never.isChecked():
            self.clear_clip_after = 0
        elif self.rb_10.isChecked():
            self.clear_clip_after = 10
        elif self.rb_30.isChecked():
            self.clear_clip_after = 30

    def on_toggle_show_password(self, checked):
        self.refresh_table()

    # Top actions
    def on_export(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, '导出CSV', os.path.join(app_root(), 'export.csv'), 'CSV Files (*.csv)')
        if not path:
            return
        self.store.export_csv(path)
        QtWidgets.QMessageBox.information(self, '完成', '已导出到CSV')

    def on_show_records(self):
        self.refresh_table()
        QtWidgets.QMessageBox.information(self, '提示', '列表已刷新到最新数据')

    def on_import(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(self, '选择CSV导入', app_root(), 'CSV Files (*.csv)')
        if not path:
            return
        try:
            cnt = self.store.import_csv(path)
            self.refresh_table()
            QtWidgets.QMessageBox.information(self, '完成', f'成功导入{cnt}条记录')
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, '错误', str(e))

    def on_set_password(self):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle('软件加密设置')
        lay = QtWidgets.QVBoxLayout(dlg)
        warn = QtWidgets.QLabel('<b style="color:red">加密后每次启动都需要输入密码！</b><br>如需解除密码保护，请清空密码框并确认。')
        lay.addWidget(warn)
        new_pwd = QtWidgets.QLineEdit(); new_pwd.setEchoMode(QtWidgets.QLineEdit.Password)
        confirm_pwd = QtWidgets.QLineEdit(); confirm_pwd.setEchoMode(QtWidgets.QLineEdit.Password)
        lay.addWidget(QtWidgets.QLabel('新密码:'))
        lay.addWidget(new_pwd)
        lay.addWidget(QtWidgets.QLabel('确认密码:'))
        lay.addWidget(confirm_pwd)
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        lay.addWidget(btns)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            pwd = new_pwd.text(); pwd2 = confirm_pwd.text()
            if pwd != pwd2:
                QtWidgets.QMessageBox.warning(self, '提示', '两次输入不一致')
                return
            self.key_mgr.set_password(pwd if pwd else None)
            QtWidgets.QMessageBox.information(self, '完成', '软件密码设置已更新')

    def on_show_usage(self):
        text = (
            '<h2 style="color:#c2185b;">安全声明</h2>'
            '<p>本软件采用 <b>AES‑256</b> 加密算法；所有密码数据均加密存储，即使文件泄露也无法解密。</p>'
            '<p>加密密钥与数据分离存储，提供双重安全保障。</p>'
            '<h2 style="color:#c2185b; margin-top:12px;">重要提醒</h2>'
            '<p>软件根目录会生成两个重要文件：</p>'
            '<p>1. <b>saved_accounts.json</b>（加密数据文件）<br>'
            '2. <b>secret.key</b>（解密密钥文件）</p>'
            '<h2 style="color:#c2185b; margin-top:12px;">数据安全警告</h2>'
            '<p>丢失 <b>secret.key</b> 将导致所有数据永久锁定；请妥善保管该文件，切勿在公共电脑保存。</p>'
            '<h2 style="color:#c2185b; margin-top:12px;">密码管理须知</h2>'
            '<p>建议每 <b>3</b> 个月更换一次主密码；自动生成的密码强度通常高于手动设置。</p>'
            '<p>删除记录会永久删除对应数据，请谨慎操作。</p>'
        )
        QtWidgets.QMessageBox.information(self, '使用必读', text)

    def on_support(self):
        # 展示赞助图片（比如支付宝二维码）
        fname = '支付宝(支付完联系电话：18603298215).jpg'
        candidate_paths = []
        # 优先PyInstaller打包后的临时目录
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            candidate_paths.append(os.path.join(getattr(sys, '_MEIPASS'), fname))
        # 其次应用根目录
        candidate_paths.append(os.path.join(app_root(), fname))
        path = next((p for p in candidate_paths if os.path.exists(p)), None)

        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle('赞助支持')
        lay = QtWidgets.QVBoxLayout(dlg)
        if path:
            img_label = QtWidgets.QLabel()
            pix = QtGui.QPixmap(path)
            if not pix.isNull():
                scaled = pix.scaledToWidth(420, QtCore.Qt.SmoothTransformation)
                img_label.setPixmap(scaled)
                lay.addWidget(img_label)
            else:
                lay.addWidget(QtWidgets.QLabel('图片无法加载'))
        else:
            lay.addWidget(QtWidgets.QLabel('未找到赞助图片'))
        lay.addWidget(QtWidgets.QLabel('支付完联系电话：18603298215'))
        btns = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Close)
        btns.rejected.connect(dlg.reject)
        lay.addWidget(btns)
        dlg.exec_()


def main():
    app = QtWidgets.QApplication(sys.argv)
    try:
        from theme import apply_pink_theme
        apply_pink_theme(app)
    except Exception:
        pass
    win = PasswordManagerApp()
    font = QtGui.QFont('Microsoft YaHei UI', 10)
    win.setFont(font)
    win.showMaximized()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
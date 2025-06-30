import tkinter as tk
from tkinter import ttk, messagebox
from story_manager import StoryManager
from audio_player import AudioPlayer
from config import Config
from story_manager_ui import StoryManagerGUI
from story_read_ui import StoryReaderGUI


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        #sự kiện đóng của sổ, để lưu lại vị trí của file nghe
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.reader_tab = None
        self.manager_tab = None
        self.title("Ứng dụng Đọc Truyện")
        self.geometry("1200x800")
        self.current_user_role = None
        self.current_user_id = 0
        self.story_manager = StoryManager()
        self.audio_player = AudioPlayer()
        self.create_login_widgets()

    def on_close(self):
        """Xử lý sự kiện đóng ứng dụng"""
        if hasattr(self, 'reader_tab') and self.reader_tab:
            self.reader_tab.save_progress()  # Gọi phương thức lưu tiến trình
        self.destroy()

    def create_login_widgets(self):
        """Tạo giao diện đăng nhập"""
        self.login_frame = ttk.Frame(self)
        self.login_frame.pack(pady=100)

        # Tên đăng nhập
        ttk.Label(self.login_frame, text="Tên đăng nhập:").grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(self.login_frame, width=30)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        # Mật khẩu
        ttk.Label(self.login_frame, text="Mật khẩu:").grid(row=1, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(self.login_frame, show="*", width=30)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        # Nút đăng nhập
        btn_frame = ttk.Frame(self.login_frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        login_btn = ttk.Button(btn_frame, text="Đăng nhập", command=self.handle_login)
        login_btn.pack(side="left", padx=5)

        register_btn = ttk.Button(btn_frame, text="Đăng ký", command=self.show_register_dialog)
        register_btn.pack(side="left", padx=5)

    def show_register_dialog(self):
        """Hiển thị cửa sổ đăng ký"""
        RegisterDialog(self)

    def handle_logout(self):
        """Xử lý sự kiện đăng xuất"""
        # Lưu tiến trình đọc
        if self.reader_tab:
            self.reader_tab.save_progress()
        self.audio_player.stop()
        # Xóa giao diện chính
        self.toolbar_frame.destroy()
        self.tab_control.destroy()

        # Reset thông tin người dùng
        self.current_user_id = 0
        self.current_user_role = None

        # Hiển thị lại màn hình đăng nhập
        self.create_login_widgets()

        messagebox.showinfo("Thông báo", "Đã đăng xuất thành công!")

    def handle_register(self, username, password, confirm_password):
        """Xử lý logic đăng ký"""
        if not username or not password:
            messagebox.showerror("Lỗi", "Vui lòng điền đầy đủ thông tin")
            return False

        if password != confirm_password:
            messagebox.showerror("Lỗi", "Mật khẩu không khớp")
            return False

        if self.story_manager.user_exists(username):
            messagebox.showerror("Lỗi", "Tên đăng nhập đã tồn tại")
            return False

        if self.story_manager.add_user(username, password, "user"):
            messagebox.showinfo("Thành công", "Đăng ký thành công!")
            return True
        return False

    def handle_login(self):
        """Xử lý sự kiện đăng nhập"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return

        user = self.story_manager.authenticate_user(username, password)
        if user:
            self.current_user_id = user[0]
            self.current_user_role = self.story_manager.get_user_role(username)
            self.login_frame.destroy()
            self.create_main_interface()
        else:
            messagebox.showerror("Lỗi", "Thông tin đăng nhập không chính xác!")

    def create_main_interface(self):
        self.toolbar_frame = ttk.Frame(self)
        self.toolbar_frame.pack(fill=tk.X, side=tk.TOP, padx=5, pady=5)

        # Nút đăng xuất
        logout_btn = ttk.Button(
            self.toolbar_frame,
            text="Đăng xuất",
            command=self.handle_logout,
            style="Logout.TButton"
        )
        logout_btn.pack(side=tk.RIGHT, padx=10)
        """Tạo giao diện chính sau khi đăng nhập thành công"""
        self.tab_control = ttk.Notebook(self)

        # Tab Quản lý chỉ dành cho admin
        if self.current_user_role == "admin":
            self.manager_tab = StoryManagerGUI(self.tab_control, self.story_manager)
            self.tab_control.add(self.manager_tab, text="Quản lý truyện")

            # Tab Đọc truyện cho tất cả người dùng
        self.reader_tab = StoryReaderGUI(self.tab_control, self.story_manager, self.audio_player, user_id=self.current_user_id)
        self.tab_control.add(self.reader_tab, text="Đọc truyện")
        self.tab_control.pack(expand=1, fill="both")

        def on_tab_changed(event):
            selected_tab = event.widget.select()
            tab_text = event.widget.tab(selected_tab, "text")
            if tab_text == "Đọc truyện":
                self.reader_tab.search_stories()
        self.tab_control.bind("<<NotebookTabChanged>>", on_tab_changed)


class RegisterDialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.title("Đăng ký tài khoản")
        self.geometry("600x450")

        self.create_widgets()

    def create_widgets(self):
        ttk.Label(self, text="Tên đăng nhập:").pack(pady=5)
        self.username_entry = ttk.Entry(self, width=50)
        self.username_entry.pack(pady=5)

        ttk.Label(self, text="Mật khẩu:").pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*", width=50)
        self.password_entry.pack(pady=5)

        ttk.Label(self, text="Xác nhận mật khẩu:").pack(pady=5)
        self.confirm_entry = ttk.Entry(self, show="*", width=50)
        self.confirm_entry.pack(pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Đăng ký", command=self.register).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Hủy", command=self.destroy).pack(side="left", padx=5)

    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_entry.get().strip()

        if self.parent.handle_register(username, password, confirm):
            self.destroy()

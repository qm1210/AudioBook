import tkinter as tk
from tkinter import ttk, messagebox
from story_manager import StoryManager
from audio_player import AudioPlayer
from config import Config

class StoryManagerGUI(ttk.Frame):
    def __init__(self, parent, story_manager):
        super().__init__(parent)
        self.story_manager = story_manager
        self.current_story_id = None
        self.current_chapter_id = None
        self.setup_ui()

    def setup_ui(self):
        # Main container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Search Section
        search_frame = ttk.Frame(self)
        search_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(search_frame, text="Tìm kiếm:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side="left", padx=5)

        ttk.Label(search_frame, text="Thể loại:").pack(side="left", padx=5)
        self.category_combobox = ttk.Combobox(search_frame, values=Config.CATEGORIES, state="readonly")
        self.category_combobox.pack(side="left", padx=5)

        search_btn = ttk.Button(search_frame, text="🔍 Tìm kiếm", width=14, command=self.search_stories)
        search_btn.pack(side="left", padx=5)

        # Main Content
        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=2)
        main_frame.grid_rowconfigure(1, weight=1)

        # Story List
        story_list_frame = ttk.LabelFrame(main_frame, text="Danh sách truyện")
        story_list_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=5, pady=5)

        # Thiết lập chiều cao của Treeview bằng cách giảm số hàng hiển thị
        self.stories_tree = ttk.Treeview(
            story_list_frame,
            columns=("id", "title", "category"),
            show="headings",
            height=5  # Giảm số hàng hiển thị để giảm chiều cao
        )
        self.stories_tree.heading("title", text="Tên truyện")
        self.stories_tree.heading("category", text="Thể loại")
        self.stories_tree.column("id", width=0, stretch=False)
        self.stories_tree.column("title", width=200)
        self.stories_tree.column("category", width=100)
        self.stories_tree.pack(fill="both", expand=True)
        self.stories_tree.bind("<<TreeviewSelect>>", self.on_story_select)

        # Story Controls
        story_controls = ttk.Frame(story_list_frame)
        story_controls.pack(fill="x", pady=5)
        ttk.Button(story_controls, text="Thêm Truyện", command=self.show_add_story_dialog).pack(side="left", padx=2)
        ttk.Button(story_controls, text="Sửa Truyện", command=self.show_edit_story_dialog).pack(side="left", padx=2)
        ttk.Button(story_controls, text="Xóa Truyện", command=self.delete_story).pack(side="left", padx=2)

        # Chapter List
        chapter_frame = ttk.LabelFrame(main_frame, text="Danh sách chương")
        chapter_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)

        self.chapters_tree = ttk.Treeview(
            chapter_frame,
            columns=("id", "number", "title"),  # Đảm bảo đúng thứ tự cột
            show="headings"
        )
        self.chapters_tree.heading("number", text="Số chương")
        self.chapters_tree.heading("title", text="Tiêu đề")
        self.chapters_tree.column("id", width=0, stretch=False)  # Ẩn cột ID
        self.chapters_tree.column("number", width=80)
        self.chapters_tree.column("title", width=250)
        self.chapters_tree.pack(fill="both", expand=True)
        self.chapters_tree.bind("<<TreeviewSelect>>", self.on_chapter_select)

        # Chapter Controls
        chapter_controls = ttk.Frame(chapter_frame)
        chapter_controls.pack(fill="x", pady=5)
        ttk.Button(chapter_controls, text="Thêm Chương", command=self.show_add_chapter_dialog).pack(side="left", padx=2)
        ttk.Button(chapter_controls, text="Sửa Chương", command=self.show_edit_chapter_dialog).pack(side="left", padx=2)
        ttk.Button(chapter_controls, text="Xóa Chương", command=self.delete_chapter).pack(side="left", padx=2)

        # Content Editor
        content_frame = ttk.LabelFrame(main_frame, text="Nội dung")
        content_frame.grid(row=1, column=1, sticky="nsew", padx=5, pady=5)

        self.content_text = tk.Text(content_frame, wrap="word", state="disabled")
        scrollbar = ttk.Scrollbar(content_frame, command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=scrollbar.set)
        self.content_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_stories()

    # Các phương thức xử lý dữ liệu
    def load_stories(self):
        for item in self.stories_tree.get_children():
            self.stories_tree.delete(item)
        stories = self.story_manager.get_all_stories()
        for story in stories:
            self.stories_tree.insert("", "end", values=story)

        # ========== CẢI THIỆN CHỨC NĂNG TÌM KIẾM ==========

    def search_stories(self):
        keyword = self.search_entry.get().strip()
        category = self.category_combobox.get()

        # Thêm option "Tất cả" vào combobox
        categories = ["Tất cả"] + Config.CATEGORIES
        if self.category_combobox["values"] != categories:
            self.category_combobox["values"] = categories
            self.category_combobox.set("Tất cả")

        stories = self.story_manager.search_stories(keyword, category if category != "Tất cả" else "")
        self.update_stories_table(stories)

    def on_story_select(self, event):
        selected = self.stories_tree.selection()
        if selected:
            self.current_story_id = self.stories_tree.item(selected[0])["values"][0]
            self.load_chapters()
            self.content_text.delete("1.0", "end")  # Xóa nội dung cũ khi chọn truyện mới

    def load_chapters(self):
        self.chapters_tree.delete(*self.chapters_tree.get_children())
        chapters = self.story_manager.get_story_chapters(self.current_story_id)
        for chap in chapters:
            # Thay đổi thứ tự các giá trị để khớp với cấu trúc Treeview
            self.chapters_tree.insert("", "end", values=(chap[2], "Chương " + str(chap[0]), chap[1]))

    def on_chapter_select(self, event):
        selected = self.chapters_tree.selection()
        if selected:
            self.current_chapter_id = self.chapters_tree.item(selected[0])["values"][0]
            self.load_chapter_content()

    def load_chapter_content(self):
        if self.current_chapter_id:
            self.content_text.config(state="normal")
            content = self.story_manager.get_chapter_content(self.current_chapter_id)
            self.content_text.delete("1.0", "end")
            self.content_text.insert("1.0", content[1])
            self.content_text.config(state="disabled")

    # Các phương thức xử lý dialog
    def show_add_story_dialog(self):
        dialog = StoryDialog(self, "Thêm truyện mới")
        self.wait_window(dialog)  # Chờ dialog đóng
        if dialog.result:
            title, category = dialog.result  # Giải nén tuple
            self.story_manager.add_story(title, category)
            self.load_stories()

    def show_edit_story_dialog(self):
        if self.current_story_id:
            try:
                # Lấy dữ liệu từ database
                story_data = self.story_manager.get_story(self.current_story_id)
                if not story_data or len(story_data) < 3:
                    messagebox.showerror("Lỗi", "Dữ liệu truyện không hợp lệ")
                    return

                # Tạo dialog và chờ kết quả
                dialog = StoryDialog(self, "Sửa thông tin truyện", story_data)
                self.wait_window(dialog)  # Quan trọng: chờ dialog đóng

                if dialog.result:
                    new_title, new_category = dialog.result
                    self.story_manager.update_story(
                        self.current_story_id,
                        new_title,
                        new_category
                    )
                    self.load_stories()

            except Exception as e:
                messagebox.showerror("Lỗi", f"Lỗi khi cập nhật truyện: {str(e)}")

    def delete_story(self):
        if self.current_story_id and messagebox.askyesno("Xác nhận", "Xóa truyện này?"):
            self.story_manager.delete_story(self.current_story_id)
            self.current_story_id = None
            self.load_stories()

    # Tương tự cho các phương thức xử lý chương
    # ...
    def show_add_chapter_dialog(self):
        if not self.current_story_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn truyện trước khi thêm chương")
            return

        dialog = ChapterDialog(self, "Thêm chương mới")
        self.wait_window(dialog)

        if dialog.result:
            title, content = dialog.result
            # Lấy số chương tiếp theo
            chapters = self.story_manager.get_story_chapters(self.current_story_id)
            next_number = len(chapters) + 1

            if self.story_manager.add_chapter(self.current_story_id, next_number, title, content):
                self.load_chapters()
                messagebox.showinfo("Thành công", "Đã thêm chương mới thành công")

    def show_edit_chapter_dialog(self):
        if not self.current_chapter_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn chương cần sửa")
            return

        # Lấy dữ liệu từ database
        chapter_info = self.story_manager.get_chapter(self.current_chapter_id)
        if not chapter_info or len(chapter_info) < 2:
            messagebox.showerror("Lỗi", "Không tìm thấy dữ liệu chương")
            return

        # Truyền đúng thứ tự dữ liệu
        dialog = ChapterDialog(self, "Sửa chương", chapter_info)
        self.wait_window(dialog)

        if dialog.result:
            new_title, new_content = dialog.result
            if self.story_manager.update_chapter(self.current_chapter_id, new_title, new_content):
                self.load_chapters()
                self.load_chapter_content()

    def delete_chapter(self):
        if not self.current_chapter_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn chương cần xóa")
            return

        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa chương này?"):
            if self.story_manager.delete_chapter(self.current_chapter_id):
                self.current_chapter_id = None
                self.load_chapters()
                self.content_text.config(state="normal")
                self.content_text.delete("1.0", "end")
                self.content_text.config(state="disabled")
            messagebox.showinfo("Thành công", "Đã xóa chương thành công")



    def update_stories_table(self, stories):
        self.stories_tree.delete(*self.stories_tree.get_children())
        for story in stories:
            self.stories_tree.insert("", "end", values=story)

    # ========== VALIDATE DỮ LIỆU ==========



class ChapterDialog(tk.Toplevel):
    def __init__(self, parent, title, chapter=None):
        super().__init__(parent)
        self.story_manager = StoryManager()
        self.title(title)
        self.result = None

        url_frame = ttk.Frame(self)
        url_frame.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="ew")  # Dòng 0

        ttk.Label(url_frame, text="URL:").pack(side="left")
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side="left", padx=5, fill="x", expand=True)

        self.fetch_btn = ttk.Button(url_frame, text="Tải từ URL", command=self.fetch_from_url)
        self.fetch_btn.pack(side="left")

        # ===== TIÊU ĐỀ CHƯƠNG - DÒNG 1 =====
        ttk.Label(self, text="Tiêu đề chương:").grid(row=1, column=0, padx=5, pady=5)  # Dòng 1
        self.title_entry = ttk.Entry(self, width=40)
        self.title_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")  # Dòng 1

        # ===== NỘI DUNG - DÒNG 2 =====
        ttk.Label(self, text="Nội dung:").grid(row=2, column=0, padx=5, pady=5)  # Dòng 2
        self.content_text = tk.Text(self, width=60, height=20, wrap="word")
        scrollbar = ttk.Scrollbar(self, command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=scrollbar.set)
        self.content_text.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")  # Dòng 2
        scrollbar.grid(row=2, column=2, sticky="ns")  # Dòng 2

        # Điền dữ liệu nếu là sửa
        # Điền dữ liệu nếu là sửa
        if chapter:
            title = chapter[0]
            content = chapter[1]
            chapter_number = chapter[2]

            self.title_entry.insert(0, title)
            self.content_text.insert("1.0", content)
            self.title(f"Chương {chapter_number}: Sửa nội dung")  # Hiển thị số chương

        # Nút điều khiển
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=3, column=0, columnspan=3, pady=10)  # Dòng 3
        ttk.Button(btn_frame, text="Lưu", command=self.on_ok).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Hủy", command=self.destroy).pack(side="left", padx=5)

    def on_ok(self):
        title = self.title_entry.get().strip()
        content = self.content_text.get("1.0", "end").strip()

        if not title:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tiêu đề chương")
            return

        if not content:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập nội dung chương")
            return

        self.result = (title, content)
        self.destroy()

    def fetch_from_url(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Lỗi", "Vui lòng nhập URL truyện")
            return

        # Gọi StoryManager để tải truyện từ URL
        title, content = self.story_manager.download_story(url)
        if title is None or content is None:
            messagebox.showerror("Lỗi", "Không thể tải truyện từ URL đã nhập")
            return

        # Auto-fill tiêu đề và nội dung vào phần Thêm truyện thủ công
        self.title_entry.delete(0, tk.END)
        self.title_entry.insert(0, title)
        self.content_text.delete("1.0", tk.END)
        self.content_text.insert("1.0", content)
        self.url_entry.delete(0, tk.END)


class StoryDialog(tk.Toplevel):
    def __init__(self, parent, dialog_title, story_data=None):
        super().__init__(parent)
        self.title(dialog_title)
        self.result = None  # Tuple (title, category)

        # Tạo các widget
        ttk.Label(self, text="Tiêu đề:").grid(row=0, column=0, padx=5, pady=5)
        self.title_entry = ttk.Entry(self, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self, text="Thể loại:").grid(row=1, column=0, padx=5, pady=5)
        self.category_combobox = ttk.Combobox(
            self,
            values=["Tất cả"] + Config.CATEGORIES,
            state="readonly"
        )
        self.category_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.category_combobox.set("Tất cả")

        # Điền dữ liệu nếu là sửa
        if story_data:
            self.title_entry.insert(0, story_data[1])  # story_data[1] = title
            self.category_combobox.set(story_data[2])  # story_data[2] = category

        # Nút điều khiển
        btn_frame = ttk.Frame(self)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Lưu", command=self.on_ok).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Hủy", command=self.destroy).pack(side="left", padx=5)

    def on_ok(self):
        title = self.title_entry.get().strip()
        category = self.category_combobox.get().strip()

        if not title:
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập tiêu đề truyện")
            return

        self.result = (title, category)
        self.destroy()
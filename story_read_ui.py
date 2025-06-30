import tkinter as tk
from tkinter import ttk, messagebox
from story_manager import StoryManager
from audio_player import AudioPlayer
from config import Config


class StoryReaderGUI(ttk.Frame):
    def __init__(self, parent, story_manager, audio_player, user_id):
        super().__init__(parent)
        self.resume_position = 0
        self.old_position = 0
        self.story_manager = story_manager
        self.audio_player = audio_player
        self.user_id = user_id
        self.current_story_id = None
        self.current_chapter_id = None
        self.setup_ui()
        self.load_user_progress()

    def setup_ui(self):
        # Cấu hình grid chính
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)  # Chỉ main frame expand

        # Search Section - Đẩy lên sát viền trên
        search_frame = ttk.Frame(self)
        search_frame.grid(row=0, column=0, padx=10, pady=(5, 2), sticky="ew")  # Giảm pady dưới

        # Các thành phần tìm kiếm
        ttk.Label(search_frame, text="Tìm kiếm:").pack(side="left", padx=3)
        self.search_entry = ttk.Entry(search_frame, width=38)
        self.search_entry.pack(side="left", padx=3)

        ttk.Label(search_frame, text="Thể loại:").pack(side="left", padx=3)
        self.category_combobox = ttk.Combobox(search_frame,
                                              values=["Tất cả"] + Config.CATEGORIES,
                                              state="readonly",
                                              width=14)
        self.category_combobox.pack(side="left", padx=3)
        self.category_combobox.set("Tất cả")

        ttk.Button(search_frame, text="🔍 Tìm kiếm", width=14, command=self.search_stories).pack(side="left", padx=3)

        # Main Content - Giảm khoảng cách với search
        main_frame = ttk.Frame(self)
        main_frame.grid(row=1, column=0, padx=10, pady=(0, 5), sticky="nsew")  # Giảm padding trên
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)
        main_frame.grid_rowconfigure(1, weight=1)

        # Story List - Chiếm 30% chiều ngang
        story_list_frame = ttk.LabelFrame(main_frame, text=" Danh sách truyện ")
        story_list_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=3, pady=3)
        story_list_frame.grid_propagate(False)

        self.stories_tree = ttk.Treeview(
            story_list_frame,
            columns=("id", "title", "category"),
            show="headings",
            height=18  # Tăng số dòng hiển thị
        )
        self.stories_tree.heading("title", text="Tên truyện")
        self.stories_tree.heading("category", text="Thể loại")
        self.stories_tree.column("id", width=0, stretch=False)
        self.stories_tree.column("title", width=220)
        self.stories_tree.column("category", width=90)
        self.stories_tree.pack(fill="both", expand=True)
        self.stories_tree.bind("<<TreeviewSelect>>", self.on_story_select)

        # Chapter List - Chiếm 35% chiều ngang
        chapter_frame = ttk.LabelFrame(main_frame, text=" Danh sách chương ")
        chapter_frame.grid(row=0, column=1, sticky="nsew", padx=3, pady=3)

        self.chapters_tree = ttk.Treeview(
            chapter_frame,
            columns=("id", "number", "title"),
            show="headings",
            height=18
        )
        self.chapters_tree.heading("number", text="Chương")
        self.chapters_tree.heading("title", text="Tiêu đề")
        self.chapters_tree.column("id", width=0, stretch=False)
        self.chapters_tree.column("number", width=50)
        self.chapters_tree.column("title", width=260)
        self.chapters_tree.pack(fill="both", expand=True)
        self.chapters_tree.bind("<<TreeviewSelect>>", self.on_chapter_select)

        # Content & Controls - Chiếm 35% chiều ngang
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=1, sticky="nsew", padx=3, pady=3)

        # Voice controls
        voice_frame = ttk.Frame(control_frame)
        voice_frame.pack(fill="x", pady=2)
        ttk.Label(voice_frame, text="Giọng đọc:").pack(side="left", padx=3)
        self.voice_combobox = ttk.Combobox(voice_frame,
                                           values=list(Config.VOICES.keys()),
                                           state="readonly",
                                           width=18)
        self.voice_combobox.pack(side="left", padx=3)

        # Playback controls
        btn_frame = ttk.Frame(control_frame)
        btn_frame.pack(fill="x", pady=3)
        # Sửa lại đoạn tạo playback controls
        self.play_button = ttk.Button(btn_frame, text="▶ Phát", width=8, command=self.play_chapter)
        self.play_button.pack(side="left", padx=2)

        self.pause_button = ttk.Button(btn_frame, text="⏸ Tạm dừng", width=15, command=self.pause_audio,
                                       state="disabled")
        self.pause_button.pack(side="left", padx=2)

        self.stop_button = ttk.Button(btn_frame, text="⏹ Dừng", width=8, command=self.stop_audio, state="disabled")
        self.stop_button.pack(side="left", padx=2)

        # Content display
        self.content_text = tk.Text(control_frame, wrap="word", height=22, state="disabled")
        scrollbar = ttk.Scrollbar(control_frame, command=self.content_text.yview)
        self.content_text.configure(yscrollcommand=scrollbar.set)
        self.content_text.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Cân chỉnh kích thước
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Load dữ liệu
        self.load_stories()

    def load_user_progress(self):
        progress = self.story_manager.get_user_progress(self.user_id)
        if progress:
            story_id, chapter_id, position, voice = progress
            print("position load: ", position)
            # Kiểm tra chapter có tồn tại không
            if self.story_manager.check_chapter_exists(chapter_id):
                self.current_story_id = story_id
                self.current_chapter_id = chapter_id
                self.resume_position = position
                self.old_position = position
                self.load_chapters()
                self.select_chapter_in_tree(chapter_id)
                self.voice_combobox.set(voice)
                self.load_chapter_content()
            else:
                # Xóa tiến trình nếu chapter không tồn tại
                self.story_manager.delete_user_progress(self.user_id)

    def select_chapter_in_tree(self, chapter_id):
        for child in self.chapters_tree.get_children():
            if self.chapters_tree.item(child)['values'][0] == chapter_id:
                self.chapters_tree.selection_set(child)
                self.chapters_tree.focus(child)
                break

    def save_progress(self):
        if self.user_id and self.current_story_id and self.current_chapter_id:
            position = self.audio_player.get_current_position(self.old_position)
            voice = self.voice_combobox.get()
            self.story_manager.save_user_progress(
                self.user_id,
                self.current_story_id,
                self.current_chapter_id,
                position,
                voice
            )

    def load_stories(self):
        for item in self.stories_tree.get_children():
            self.stories_tree.delete(item)
        stories = self.story_manager.get_all_stories()
        for story in stories:
            self.stories_tree.insert("", "end", values=story)

    def search_stories(self):
        keyword = self.search_entry.get().strip()
        category = self.category_combobox.get()
        stories = self.story_manager.search_stories(
            keyword,
            category if category != "Tất cả" else ""
        )
        self.stories_tree.delete(*self.stories_tree.get_children())
        for story in stories:
            self.stories_tree.insert("", "end", values=story)

    def on_story_select(self, event):
        selected = self.stories_tree.selection()
        if selected:
            self.current_story_id = self.stories_tree.item(selected[0])["values"][0]
            self.load_chapters()

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
            self.content_text.delete("1.0", "end")

            # Thêm kiểm tra dữ liệu trả về
            content = self.story_manager.get_chapter_content(self.current_chapter_id)

            if content and len(content) >= 2:  # Kiểm tra content hợp lệ
                self.content_text.insert("1.0", content[1])
            # else:
            #     messagebox.showwarning("Cảnh báo", "Không tìm thấy nội dung chương")

            self.content_text.config(state="disabled")

    def play_chapter(self, resume=False):
        if self.current_chapter_id:
            content = self.content_text.get("1.0", "end").strip()
            voice = Config.VOICES[self.voice_combobox.get()]

            if not content:
                messagebox.showerror("Lỗi", "Không có nội dung để đọc")
                return

            try:
                # Tạo audio mới nếu cần
                if (not resume or
                        not hasattr(self.audio_player, 'current_audio') or
                        self.audio_player.current_audio != content or
                        not hasattr(self.audio_player, 'voice') or
                        self.audio_player.voice != voice
                ):
                    audio_content = self.audio_player.text_to_speech(content[:3000], voice)
                    self.audio_player.current_audio = content
                    self.audio_player.audio_content = audio_content

                if self.audio_player.paused:
                    self.audio_player.resume()
                else:
                    # Phát từ vị trí đã lưu (nếu có)
                    start_pos = getattr(self, 'resume_position', 0)  # Lấy vị trí resume
                    self.audio_player.play_audio(self.audio_player.audio_content, start_pos=start_pos)
                # Reset resume_position sau khi đã xử lý
                if hasattr(self, 'resume_position'):
                    del self.resume_position

                # Cập nhật UI
                self.update_playback_ui(playing=True)
                self.check_playback_status()

            except Exception as e:
                messagebox.showerror("Lỗi TTS", f"Lỗi khi tạo/phát audio:\n{str(e)}")
                self.update_playback_ui(playing=False)

    def update_stories_table(self, event=None):
        category = self.category_combobox.get().strip()
        search_text = self.search_entry.get().strip()
        print("update_stories_table is call")
        # Xóa dữ liệu cũ
        for row in self.stories_tree.get_children():
            self.stories_tree.delete(row)

        # Lấy dữ liệu mới từ story_manager
        stories = self.story_manager.search_stories(category, search_text)

        # Thêm dữ liệu vào bảng
        for story in stories:
            self.stories_tree.insert("", "end", values=(story[0], story[1], story[2]))

    def update_playback_ui(self, playing):
        if playing:
            self.play_button["state"] = "disabled"
            self.pause_button["state"] = "normal"
            self.stop_button["state"] = "normal"
        else:
            self.play_button["state"] = "normal"
            self.pause_button["state"] = "disabled"
            self.stop_button["state"] = "disabled"

    def pause_audio(self):
        self.audio_player.pause()
        self.play_button["state"] = "normal"
        self.pause_button["state"] = "disabled"
        self.stop_button["state"] = "normal"

    def stop_audio(self):
        self.audio_player.stop()
        self.play_button["state"] = "normal"
        self.pause_button["state"] = "disabled"
        self.stop_button["state"] = "disabled"

    def check_playback_status(self):
        # Nếu audio đang bị tạm dừng, không reset UI.
        if self.audio_player.paused:
            self.after(100, self.check_playback_status)
        # Nếu audio đang phát, tiếp tục kiểm tra.
        elif self.audio_player.is_playing():
            self.after(100, self.check_playback_status)
        else:
            # Nếu không đang phát và không bị tạm dừng, audio đã kết thúc -> gọi stop_story
            self.stop_audio()
            self.old_position = 0
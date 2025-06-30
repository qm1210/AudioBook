from database import Database
import requests
from bs4 import BeautifulSoup


class StoryManager:
    def __init__(self):
        self.db = Database()

    def get_chapter(self, chapter_id):
        return self.db.get_chapter(chapter_id)

    def add_chapter(self, story_id, number, title, content):
        return self.db.add_chapter( story_id, number, title, content)

    def update_chapter(self, chapter_id, new_title, new_content):
        return self.db.update_chapter(chapter_id, new_title, new_content)

    def delete_chapter(self, chapter_id):
        return self.db.delete_chapter(chapter_id)

    def search_stories(self, keyword="", category=""):
        return self.db.search_stories(keyword,category)

    def get_all_stories(self):
        return self.db.get_all_stories()

    def get_story(self, story_id):
        return self.db.get_story(story_id)

    def add_story(self, title, category):
        return self.db.add_story(title, category)

    def update_story(self, story_id, title, category):
        return self.db.update_story(story_id, title, category)

    def delete_story(self, story_id):
        return self.db.delete_story(story_id)

    def add_story_manually(self, title, content, category):
        return self.db.add_story(title, content, category)

    def download_story(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            # Trích xuất tiêu đề:
            # Ưu tiên tìm thẻ <h1 class="chapter-title">, nếu không tìm thấy thì thử <a class="truyen-title">
            title_tag = soup.find('a', class_='chapter-title')
            if not title_tag:
                title_tag = soup.find('a', class_='chapter-title')
            title = title_tag.get_text(strip=True) if title_tag else 'Không tìm thấy tiêu đề'

            # Trích xuất nội dung truyện:
            # Giả sử nội dung nằm trong <div class="chapter-c">
            content_tag = soup.find('div', class_='chapter-c')
            if content_tag:
                # Sử dụng get_text với separator để giữ lại định dạng dòng
                content = content_tag.get_text(separator="\n", strip=True)
            else:
                content = 'Không tìm thấy nội dung'

            return title, content

        except requests.RequestException as e:
            print("Lỗi khi tải truyện:", e)
            return None, None

    def get_stories_by_category(self, category):
        return self.db.get_stories_by_category(category)

    def get_story_content(self, story_id):
        return self.db.get_story_content(story_id)

    def search_stories(self, category, search_text):
        return self.db.search_stories(category, search_text)

    def authenticate_user(self, username, password):
        return self.db.authenticate_user(username, password)

    def get_user_role(self, username):
        return self.db.get_user_role(username)

    # story_manager.py
    def add_story_manually(self, title, category, chapters):
        return self.db.add_story_manually(title, category, chapters)

    def get_story_chapters(self, story_id):
        return self.db.get_story_chapters(story_id)

    def get_chapter_content(self, chapter_id):
        return self.db.get_chapter(chapter_id)

    def save_user_progress(self, user_id, story_id, chapter_id, position, voice):
        return self.db.save_user_progress(user_id, story_id, chapter_id, position, voice)

    def get_user_progress(self, user_id):
        return self.db.get_user_progress(user_id)

    def check_chapter_exists(self, chapter_id):
        return self.db.check_chapter_exists(chapter_id)

    def delete_user_progress(self, user_id):
        return self.db.delete_user_progress(user_id)

    def add_user(self, username, password, role="user"):
        return self.db.add_user(username, password, role)

    def user_exists(self, username):
        return self.db.user_exists(username)
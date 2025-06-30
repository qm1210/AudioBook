import sqlite3
from config import Config


class Database:
    def __init__(self):
        self.conn = sqlite3.connect(Config.DB_NAME)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                category TEXT NOT NULL,
                added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Bảng chapters mới
        cursor.execute('''
                CREATE TABLE IF NOT EXISTS chapters (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    story_id INTEGER NOT NULL,
                    chapter_number INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY(story_id) REFERENCES stories(id) ON DELETE CASCADE
                )
            ''')

        # Tạo bảng users
        cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL
                    )
                ''')

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_progress (
                    user_id TEXT PRIMARY KEY,
                    story_id INTEGER,
                    chapter_id INTEGER,
                    position REAL,
                    voice TEXT
                )
            ''')
        self.conn.commit()

    def add_user(self, username, password, role="user"):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO users (username, password, role)
                VALUES (?, ?, ?)
            ''', (username, password, role))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def user_exists(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return cursor.fetchone() is not None

    def authenticate_user(self, username, password):
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
        return cursor.fetchone()

    def get_user_role(self, username):
        cursor = self.conn.cursor()
        cursor.execute('SELECT role FROM users WHERE username=?', (username,))
        result = cursor.fetchone()
        return result[0] if result else None

    def save_user_progress(self, user_id, story_id, chapter_id, position, voice):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO user_progress 
            (user_id, story_id, chapter_id, position, voice)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, story_id, chapter_id, position, voice))
        self.conn.commit()

    def get_user_progress(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT story_id, chapter_id, position, voice 
            FROM user_progress 
            WHERE user_id = ?
        ''', (user_id,))
        return cursor.fetchone()

    def check_chapter_exists(self, chapter_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 FROM chapters WHERE id = ?", (chapter_id,))
        return cursor.fetchone() is not None

    def delete_user_progress(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM user_progress WHERE user_id = ?", (user_id,))
        self.conn.commit()

    def get_stories_by_category(self, category):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, title FROM stories WHERE category = ?', (category,))
        return cursor.fetchall()

    def get_story_content(self, story_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT content FROM stories WHERE id = ?', (story_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def search_stories_by_name(self, category, search_text):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, title 
            FROM stories 
            WHERE category = ? 
            AND LOWER(title) LIKE LOWER(?)
        ''', (category, f'%{search_text}%'))
        return cursor.fetchall()

    def search_stories(self, category=None, search_text=None):
        cursor = self.conn.cursor()
        query = "SELECT id, title, category FROM stories WHERE 1=1"
        params = []

        if category:
            query += " AND category = ?"
            params.append(category)

        if search_text:
            query += " AND title LIKE ?"
            params.append(f"%{search_text}%")
        query += " ORDER BY added_date DESC"
        cursor.execute(query, params)
        return cursor.fetchall()

    def get_chapter(self, chapter_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT title, content, chapter_number 
            FROM chapters 
            WHERE id = ?
        ''', (chapter_id,))
        return cursor.fetchone()

    def add_chapter(self, story_id, number, title, content):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO chapters (story_id, chapter_number, title, content)
                VALUES (?, ?, ?, ?)
            ''', (story_id, number, title, content))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            return False

    def update_chapter(self, chapter_id, new_title, new_content):
        cursor = self.conn.cursor()
        try:
            cursor.execute('''
                UPDATE chapters 
                SET title = ?, content = ?
                WHERE id = ?
            ''', (new_title, new_content, chapter_id))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            return False

    def delete_chapter(self, chapter_id):
        cursor = self.conn.cursor()
        try:
            cursor.execute('DELETE FROM chapters WHERE id = ?', (chapter_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            return False

    def search_stories(self, keyword="", category=""):
        cursor = self.conn.cursor()
        params = []
        query = '''
            SELECT id, title, category 
            FROM stories 
            WHERE 1=1
        '''

        if keyword:
            query += " AND title LIKE ?"
            params.append(f"%{keyword}%")

        if category and category != "Tất cả":
            query += " AND category = ?"
            params.append(category)

        cursor.execute(query, params)
        return cursor.fetchall()
    
    
    def get_all_stories(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, category FROM stories")
        return cursor.fetchall()

    def get_story(self, story_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, category FROM stories WHERE id=?", (story_id,))
        return cursor.fetchone()

    def add_story(self, title, category):
        cursor = self.conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO stories (title, category) VALUES (?, ?)",
                (title, category)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            self.conn.rollback()
            print("Error add stories ", e)
            return False

    def update_story(self, story_id, title, category):
        cursor = self.conn.cursor()
        try:
            cursor.execute("UPDATE stories SET title=?, category=? WHERE id=?",
                                (title, category, story_id))
            self.conn.commit()
        except sqlite3.Error as e:
            self.conn.rollback()
            print("Error add stories ", e)

    def delete_story(self, story_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM stories WHERE id=?", (story_id,))
        self.conn.commit()

    def get_story_chapters(self, story_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT chapter_number, title, id 
            FROM chapters 
            WHERE story_id = ? 
            ORDER BY chapter_number
        ''', (story_id,))
        return cursor.fetchall()

    def get_chapter_content(self, story_id, chapter_number):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT content 
            FROM chapters 
            WHERE story_id = ? AND chapter_number = ?
        ''', (story_id, chapter_number))
        result = cursor.fetchone()
        return result[0] if result else ""

    def add_story_manually(self, title, category, chapters):
        cursor = self.conn.cursor()
        try:
            # Thêm truyện
            cursor.execute("INSERT INTO stories (title, category) VALUES (?, ?)", (title, category))
            story_id = cursor.lastrowid

            # Thêm các chương
            for chapter in chapters:
                cursor.execute('''
                    INSERT INTO chapters (story_id, chapter_number, title, content)
                    VALUES (?, ?, ?, ?)
                ''', (story_id, chapter[0], chapter[1], chapter[2]))

            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            raise e

    def get_chapter_content(self, chapter_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT content 
            FROM chapters 
            WHERE id = ?
        ''', (chapter_id,))
        result = cursor.fetchone()
        return result[0] if result else ""

    def close(self):
        self.conn.close()

import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_path=None):
        # Если путь не указан, создаем базу данных в папке со скриптом
        if db_path is None:
            # Получаем путь к папке, где находится текущий скрипт
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, "snake_scores.db")
        
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_table()
        
        # Выводим информацию о созданной базе данных
        print(f"База данных создана/открыта: {self.db_path}")
    
    def connect(self):
        """Подключение к базе данных"""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def create_table(self):
        """Создание таблицы рекордов"""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nickname TEXT NOT NULL,
                score INTEGER NOT NULL,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
        
        # Проверяем, есть ли записи в таблице
        self.cursor.execute('SELECT COUNT(*) FROM leaderboard')
        count = self.cursor.fetchone()[0]
        print(f"В таблице leaderboard записей: {count}")
    
    def add_score(self, nickname, score):
        """Добавление нового рекорда"""
        print(f"Добавление рекорда: {nickname} - {score}")
        
        # Получаем текущие рекорды
        self.cursor.execute('SELECT nickname, score FROM leaderboard ORDER BY score DESC')
        scores = self.cursor.fetchall()
        
        # Если меньше 10 записей, просто добавляем
        if len(scores) < 10:
            self.cursor.execute('INSERT INTO leaderboard (nickname, score) VALUES (?, ?)', 
                              (nickname, score))
            print(f"Добавлен новый рекорд (место есть)")
        else:
            # Проверяем, входит ли новый результат в топ-10
            min_score = scores[-1][1]
            if score > min_score:
                # Удаляем последнюю запись
                self.cursor.execute('''
                    DELETE FROM leaderboard 
                    WHERE id = (SELECT id FROM leaderboard ORDER BY score DESC LIMIT 1 OFFSET 9)
                ''')
                # Добавляем новую запись
                self.cursor.execute('INSERT INTO leaderboard (nickname, score) VALUES (?, ?)', 
                                  (nickname, score))
                print(f"Добавлен новый рекорд (вытеснен последний с {min_score} очками)")
            else:
                print(f"Рекорд не добавлен: {score} < {min_score}")
        
        self.conn.commit()
        
        # Показываем текущую таблицу рекордов
        self.show_leaderboard()
    
    def get_leaderboard(self):
        """Получение таблицы рекордов"""
        self.cursor.execute('''
            SELECT nickname, score, date FROM leaderboard 
            ORDER BY score DESC LIMIT 10
        ''')
        return self.cursor.fetchall()
    
    def show_leaderboard(self):
        """Вывод таблицы рекордов в консоль для отладки"""
        print("\n=== ТАБЛИЦА РЕКОРДОВ ===")
        self.cursor.execute('SELECT nickname, score FROM leaderboard ORDER BY score DESC LIMIT 10')
        scores = self.cursor.fetchall()
        if scores:
            for i, (nick, score) in enumerate(scores, 1):
                print(f"{i}. {nick} - {score} очков")
        else:
            print("Пока нет рекордов")
        print("=" * 25 + "\n")
    
    def clear_leaderboard(self):
        """Очистка таблицы рекордов (для тестирования)"""
        self.cursor.execute('DELETE FROM leaderboard')
        self.conn.commit()
        print("Таблица рекордов очищена")
    
    def delete_database(self):
        """Удаление файла базы данных"""
        self.close()
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
            print(f"База данных удалена: {self.db_path}")
    
    def close(self):
        """Закрытие соединения с базой данных"""
        if self.conn:
            self.conn.close()
            print("Соединение с базой данных закрыто")
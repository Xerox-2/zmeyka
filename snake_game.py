from tkinter import *
from random import randint
from database import Database
from game_settings import *

class Game:
    def __init__(self, canvas):
        self.canvas = canvas
        self.vector = KEYS
        self.game_loop_id = None  # ID для after
        self.dialog = None  # Для хранения ссылки на диалог
        
        # Привязка клавиш
        self.canvas.bind("<Key>", self.on_key_press)
        self.canvas.bind("<Button-1>", lambda event: self.canvas.focus_set())
        
        # Инициализация базы данных
        self.db = Database(DATABASE_PATH)
        
        self.reset_game()
        self.start_game_loop()

    def start_game_loop(self):
        """Запуск игрового цикла"""
        if self.game_loop_id:
            self.canvas.after_cancel(self.game_loop_id)
        self.game_loop_id = self.canvas.after(GAME_SPEED, self.GAME)

    def stop_game_loop(self):
        """Остановка игрового цикла"""
        if self.game_loop_id:
            self.canvas.after_cancel(self.game_loop_id)
            self.game_loop_id = None

    def reset_game(self):
        """Сброс параметров игры"""
        # Создаем стены
        self.create_walls()
        
        self.snake_coords = [coord.copy() for coord in INITIAL_SNAKE]
        self.direction = self.vector[INITIAL_DIRECTION]
        self.game_over = False
        self.score = 0
        self.set_apples()  # Создаем яблоки после установки snake_coords
        self.canvas.focus_set()
        self.canvas.delete(ALL)
        self.draw()  # Отрисовываем начальное состояние

    def create_walls(self):
        """Создание фиолетовых стен по периметру"""
        self.walls = []
        # Верхняя и нижняя стены
        for x in range(FIELD_SIZE):
            self.walls.append([x, 0])  # Верхняя
            self.walls.append([x, FIELD_SIZE - 1])  # Нижняя
        # Левая и правая стены (без углов, чтобы не дублировать)
        for y in range(1, FIELD_SIZE - 1):
            self.walls.append([0, y])  # Левая
            self.walls.append([FIELD_SIZE - 1, y])  # Правая

    def set_apples(self):
        """Создание яблок"""
        self.apples = []
        attempts = 0
        while len(self.apples) < APPLES_COUNT and attempts < 1000:
            new_coords = [randint(1, FIELD_SIZE - 2), randint(1, FIELD_SIZE - 2)]
            # Яблоко не должно появляться на змейке, на стенах или на месте другого яблока
            if (new_coords not in self.snake_coords and 
                new_coords not in self.apples and 
                new_coords not in self.walls):
                self.apples.append(new_coords)
            attempts += 1
        
        # Если не удалось разместить все яблоки, заполняем оставшиеся
        if len(self.apples) < APPLES_COUNT:
            for x in range(1, FIELD_SIZE - 1):
                for y in range(1, FIELD_SIZE - 1):
                    if len(self.apples) >= APPLES_COUNT:
                        break
                    new_coords = [x, y]
                    if (new_coords not in self.snake_coords and 
                        new_coords not in self.apples and 
                        new_coords not in self.walls):
                        self.apples.append(new_coords)

    def replace_apple(self, eaten_coords):
        """Замена одного съеденного яблока на новое"""
        attempts = 0
        while attempts < 1000:
            new_coords = [randint(1, FIELD_SIZE - 2), randint(1, FIELD_SIZE - 2)]
            if (new_coords not in self.snake_coords and 
                new_coords not in self.apples and 
                new_coords not in self.walls):
                idx = self.apples.index(eaten_coords)
                self.apples[idx] = new_coords
                return
            attempts += 1
        
        # Если не удалось найти место, просто обновляем координаты
        idx = self.apples.index(eaten_coords)
        self.apples[idx] = [randint(1, FIELD_SIZE - 2), randint(1, FIELD_SIZE - 2)]

    def draw(self):
        """Отрисовка игры"""
        self.canvas.delete(ALL)
        
        # Рисуем стены
        for x_wall, y_wall in self.walls:
            self.canvas.create_rectangle(
                x_wall * CELL_SIZE, y_wall * CELL_SIZE, 
                (x_wall + 1) * CELL_SIZE, (y_wall + 1) * CELL_SIZE, 
                fill=COLORS['wall'], width=0, outline=COLORS['wall_outline']
            )
        
        # Рисуем яблоки
        for x_apple, y_apple in self.apples:
            self.canvas.create_rectangle(
                x_apple * CELL_SIZE, y_apple * CELL_SIZE, 
                (x_apple + 1) * CELL_SIZE, (y_apple + 1) * CELL_SIZE, 
                fill=COLORS['apple'], width=0
            )
        
        # Рисуем змейку
        for i, (x, y) in enumerate(self.snake_coords):
            # Голова змейки рисуется другим цветом
            if i == 0:
                self.canvas.create_rectangle(
                    x * CELL_SIZE, y * CELL_SIZE, 
                    (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE, 
                    fill="lightgreen", width=0
                )
            else:
                self.canvas.create_rectangle(
                    x * CELL_SIZE, y * CELL_SIZE, 
                    (x + 1) * CELL_SIZE, (y + 1) * CELL_SIZE, 
                    fill=COLORS['snake'], width=0
                )
        
        # Рисуем счет
        self.canvas.create_text(
            30, 15, text=f"Score: {self.score}", 
            fill=COLORS['text'], font=("Arial", 12, "bold"), anchor="w"
        )
        
        # Экран проигрыша
        if self.game_over:
            self.canvas.create_text(
                WIDTH // 2, HEIGHT // 2 - 20, text="GAME OVER!", 
                fill=COLORS['game_over'], font=("Arial", 20, "bold")
            )
            self.canvas.create_text(
                WIDTH // 2, HEIGHT // 2 + 10, text=f"Final Score: {self.score}", 
                fill=COLORS['text'], font=("Arial", 14, "bold")
            )
            self.canvas.create_text(
                WIDTH // 2, HEIGHT // 2 + 40, text="Press R to continue", 
                fill=COLORS['restart_text'], font=("Arial", 10, "bold")
            )

    def show_leaderboard_dialog(self):
        """Отображение диалога ввода имени и таблицы рекордов"""
        # Если диалог уже открыт, не создаем новый
        if self.dialog and self.dialog.winfo_exists():
            return
            
        self.stop_game_loop()  # Останавливаем игровой цикл
        
        self.dialog = Toplevel(self.canvas)
        self.dialog.title("Game Over - Leaderboard")
        self.dialog.geometry("350x500")
        self.dialog.resizable(False, False)
        
        # Заголовок
        Label(self.dialog, text=f"Your Score: {self.score}", 
              font=("Arial", 14, "bold")).pack(pady=10)
        
        # Поле ввода ника
        Label(self.dialog, text="Enter your nickname:", font=("Arial", 10)).pack()
        nickname_entry = Entry(self.dialog, font=("Arial", 10))
        nickname_entry.pack(pady=5)
        nickname_entry.focus()  # Устанавливаем фокус на поле ввода
        
        # Таблица рекордов
        Label(self.dialog, text="\nTop 10 Players:", font=("Arial", 12, "bold")).pack()
        
        # Создаем фрейм для таблицы с прокруткой
        leaderboard_frame = Frame(self.dialog)
        leaderboard_frame.pack(pady=10, fill=BOTH, expand=True, padx=10)
        
        # Создаем Canvas для прокрутки
        canvas_scroll = Canvas(leaderboard_frame, height=250, bg='white')
        scrollbar = Scrollbar(leaderboard_frame, orient="vertical", 
                              command=canvas_scroll.yview)
        scrollable_frame = Frame(canvas_scroll, bg='white')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas_scroll.configure(scrollregion=canvas_scroll.bbox("all"))
        )
        
        canvas_scroll.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas_scroll.configure(yscrollcommand=scrollbar.set)
        
        # Заголовки таблицы
        Label(scrollable_frame, text="#", width=5, anchor="w", 
              font=("Arial", 10, "bold"), bg='white').grid(row=0, column=0, sticky="w", padx=5, pady=5)
        Label(scrollable_frame, text="Nickname", width=20, anchor="w", 
              font=("Arial", 10, "bold"), bg='white').grid(row=0, column=1, sticky="w", padx=5, pady=5)
        Label(scrollable_frame, text="Score", width=8, anchor="w", 
              font=("Arial", 10, "bold"), bg='white').grid(row=0, column=2, sticky="w", padx=5, pady=5)
        
        # Отображаем рекорды
        leaderboard = self.db.get_leaderboard()
        if leaderboard:
            for i, (nick, score, date) in enumerate(leaderboard, 1):
                Label(scrollable_frame, text=str(i), width=5, anchor="w",
                      font=("Arial", 9), bg='white').grid(row=i, column=0, sticky="w", padx=5, pady=2)
                Label(scrollable_frame, text=nick, width=20, anchor="w",
                      font=("Arial", 9), bg='white').grid(row=i, column=1, sticky="w", padx=5, pady=2)
                Label(scrollable_frame, text=str(score), width=8, anchor="w",
                      font=("Arial", 9), bg='white').grid(row=i, column=2, sticky="w", padx=5, pady=2)
        else:
            Label(scrollable_frame, text="No records yet", 
                  font=("Arial", 10), bg='white').grid(row=1, column=0, columnspan=3, pady=10)
        
        canvas_scroll.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        def save_and_restart():
            nickname = nickname_entry.get().strip()
            if not nickname:
                nickname = "Anonymous"
            elif len(nickname) > 15:
                nickname = nickname[:15]
            
            self.db.add_score(nickname, self.score)
            self.dialog.destroy()
            self.dialog = None
            self.reset_game()
            self.start_game_loop()  # Запускаем игровой цикл заново
        
        def cancel_and_restart():
            self.dialog.destroy()
            self.dialog = None
            self.reset_game()
            self.start_game_loop()  # Запускаем игровой цикл заново
        
        Button(self.dialog, text="Save Score & Restart", command=save_and_restart, 
               font=("Arial", 10), bg="green", fg="white").pack(pady=10)
        Button(self.dialog, text="Cancel", command=cancel_and_restart, 
               font=("Arial", 10)).pack(pady=5)
        
        # Обработка нажатия Enter в поле ввода
        def on_enter(event):
            save_and_restart()
        
        nickname_entry.bind("<Return>", on_enter)
        
        # Обработка закрытия окна
        def on_closing():
            cancel_and_restart()
        
        self.dialog.protocol("WM_DELETE_WINDOW", on_closing)
        
        self.dialog.transient(self.canvas)
        self.dialog.grab_set()
        
        # Ждем закрытия диалога
        self.canvas.wait_window(self.dialog)

    def on_key_press(self, event):
        """Обработка нажатий клавиш"""
        key = event.keysym
        key_char = event.char  # Получаем символ, который был введен
        
        # Отладка - выводим информацию о нажатой клавише в консоль
        print(f"Нажата клавиша: keysym='{key}', char='{key_char}'")
        
        # Если игра окончена
        if self.game_over:
            # Проверяем все возможные варианты для рестарта
            if (key.lower() == 'r' or           
                key.lower() == 'k' or          
                key_char == 'к' or              
                key_char == 'К'):              
                print("Запускаем диалог рекордов")
                self.show_leaderboard_dialog()
            return
        
        # Управление змейкой (стрелки)
        if key in self.vector:
            new_dir = self.vector[key]
            # Запрещаем разворот на 180 градусов
            if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
                self.direction = new_dir
            return
        
        # Поддержка WASD и русских букв
        rus_to_eng = {
            'ф': 'a',   
            'ы': 's',  
            'в': 'd',   
            'а': 'w',   
        }
        
        # Проверяем английские буквы
        if key.lower() in WASD:
            control_key = key.lower()
        # Проверяем русские буквы через event.char
        elif key_char.lower() in rus_to_eng:
            control_key = rus_to_eng[key_char.lower()]
        else:
            return
        
        # Применяем управление
        if control_key in WASD:
            wasd_key = WASD[control_key]
            new_dir = self.vector[wasd_key]
            if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
                self.direction = new_dir

    def GAME(self):
        """Основной игровой цикл"""
        if not self.game_over:
            # Вычисляем новую голову
            x, y = self.snake_coords[0]
            x += self.direction[0]
            y += self.direction[1]
            
            # Проверка на столкновение со стенами
            if [x, y] in self.walls:
                self.game_over = True
                self.draw()
                # Не вызываем диалог сразу, ждем нажатия R
                return
            
            # Проверка на столкновение с хвостом
            if [x, y] in self.snake_coords:
                self.game_over = True
                self.draw()
                # Не вызываем диалог сразу, ждем нажатия R
                return
            
            # Логика движения и роста
            self.snake_coords.insert(0, [x, y])
            
            # Проверка: съели ли яблоко?
            ate_apple = False
            if [x, y] in self.apples:
                self.replace_apple([x, y])
                self.score += 1
                ate_apple = True
            
            if not ate_apple:
                self.snake_coords.pop()
            
            # Отрисовка
            self.draw()
            
            # Продолжаем игровой цикл
            self.game_loop_id = self.canvas.after(GAME_SPEED, self.GAME)


# Запуск игры
if __name__ == "__main__":
    root = Tk()
    root.title("Snake Game - With Walls")
    root.resizable(False, False)
    canvas = Canvas(root, width=WIDTH, height=HEIGHT, bg=COLORS['background'])
    canvas.pack()
    canvas.focus_set()
    
    game = Game(canvas)
    root.mainloop()
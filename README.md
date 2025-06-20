### 🚀 A Game About Space

Простая космическая игра в терминале на Python. Управляйте кораблём с помощью стрелок и наслаждайтесь мерцающим звёздным небом.

## 📦 Требования

- Python 3.7+

- Linux / macOS / Windows (через терминал, поддерживающий curses)

- Терминал в полноэкранном режиме для лучшего эффекта

## 🛠 Установка

1. Клонируй репозиторий (или просто скачай код):

```bash
git clone https://github.com/AnnaKuryletz/A_game_about_space
cd A_game_about_space
```

2. Установи зависимости:

- Если используешь venv:

```bash
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
pip install
```

## 📁 Структура проекта

```bash
.
├── space_game.py              # Точка входа
├── fire_animation.py          # Анимация выстрелов
├── animation/
│   ├── space_ship.py          # Движение корабля
│   ├── rocket_frame_1.txt     # Первый кадр корабля
│   └── rocket_frame_2.txt     # Второй кадр корабля
```

## 🎮 Управление

- Стрелки — перемещение корабля

## 🚀 Запуск игры

```bash
python space_game.py
```

Важно: окно терминала должно быть достаточно большим, чтобы вместить корабль и звёзды.

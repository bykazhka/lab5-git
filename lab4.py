"""
Лабораторная работа №4. Классы.
Тема: Посты (№, ник автора, текст поста, количество лайков).
Переработка лабораторной работы №3 с применением классов, итераторов,
генераторов, наследования, перегрузки операторов, __setattr__, __getitem__,
статических методов.
"""

import os
import csv


# --------------------------- Класс Post (базовый) ---------------------------
class Post:
    """Базовый класс для представления поста."""

    def __init__(self, number: int, author: str, text: str, likes: int):
        self.number = number
        self.author = author
        self.text = text
        self.likes = likes

    def __setattr__(self, key, value):
        """Перегрузка присваивания атрибутов с проверкой корректности."""
        if key == 'number' and not isinstance(value, int):
            raise TypeError("Номер поста должен быть целым числом")
        if key == 'author' and (not isinstance(value, str) or not value.strip()):
            raise ValueError("Имя автора не может быть пустым")
        if key == 'text' and not isinstance(value, str):
            raise TypeError("Текст поста должен быть строкой")
        if key == 'likes':
            if not isinstance(value, int) or value < 0:
                raise ValueError("Количество лайков должно быть неотрицательным целым")
        super().__setattr__(key, value)

    def __repr__(self):
        """Перегрузка repr для наглядного отображения."""
        return (f"Post(№{self.number}, {self.author}, "
                f"'{self.text[:20]}{'...' if len(self.text) > 20 else ''}', "
                f"лайков: {self.likes})")

    @staticmethod
    def is_valid_nickname(nick: str) -> bool:
        """Статический метод: проверка, что ник состоит только из букв и цифр."""
        return nick.isalnum()


# ---------------------- Класс SponsoredPost (наследник) ----------------------
class SponsoredPost(Post):
    """Класс рекламного поста, наследуется от Post, добавляет бюджет."""

    def __init__(self, number: int, author: str, text: str, likes: int, budget: float):
        super().__init__(number, author, text, likes)
        self.budget = budget

    def __setattr__(self, key, value):
        """Дополнительная проверка бюджета."""
        if key == 'budget':
            if not isinstance(value, (int, float)) or value < 0:
                raise ValueError("Бюджет должен быть неотрицательным числом")
        super().__setattr__(key, value)

    def __repr__(self):
        """Добавляем информацию о бюджете."""
        base = super().__repr__()
        return base[:-1] + f", бюджет: {self.budget})"


# ----------------------- Класс коллекции постов -----------------------------
class PostCollection:
    """
    Коллекция постов с поддержкой итерации, индексации, сортировок,
    фильтрации, генераторов и статических методов чтения/записи CSV.
    """

    def __init__(self):
        self._posts = []   # список объектов Post или SponsoredPost

    # --- Итератор ---
    def __iter__(self):
        """Возвращает итератор по постам коллекции."""
        return iter(self._posts)

    # --- Доступ по индексу ---
    def __getitem__(self, index):
        """Позволяет обращаться к постам по индексу: collection[i]."""
        return self._posts[index]

    def __len__(self):
        return len(self._posts)

    # --- Добавление постов ---
    def add_post(self, post: Post):
        if not isinstance(post, Post):
            raise TypeError("Можно добавить только объект Post или его наследника")
        self._posts.append(post)

    # --- Генератор: посты с лайками выше порога ---
    def filter_by_likes_generator(self, min_likes: int):
        """
        Генератор, возвращающий посты, у которых количество лайков > min_likes.
        Реализован через yield.
        """
        for post in self._posts:
            if post.likes > min_likes:
                yield post

    # --- Методы сортировки (возвращают новые коллекции) ---
    def sorted_by_author(self) -> 'PostCollection':
        """Возвращает новую коллекцию, отсортированную по нику автора (без учёта регистра)."""
        new_coll = PostCollection()
        new_coll._posts = sorted(self._posts, key=lambda p: p.author.lower())
        return new_coll

    def sorted_by_likes(self, reverse: bool = True) -> 'PostCollection':
        """Возвращает новую коллекцию, отсортированную по лайкам (по умолчанию – по убыванию)."""
        new_coll = PostCollection()
        new_coll._posts = sorted(self._posts, key=lambda p: p.likes, reverse=reverse)
        return new_coll

    # --- Фильтрация (обычный метод, не генератор) ---
    def filter_by_min_likes(self, min_likes: int) -> 'PostCollection':
        """Возвращает новую коллекцию с постами, у которых лайков > min_likes."""
        new_coll = PostCollection()
        new_coll._posts = [p for p in self._posts if p.likes > min_likes]
        return new_coll

    # --- Вывод коллекции ---
    def display(self):
        """Выводит все посты коллекции в табличном виде."""
        if not self._posts:
            print("Коллекция пуста.")
            return
        print(f"{'№':<5} {'Ник':<20} {'Текст':<30} {'Лайки':<6}")
        print("-" * 65)
        for post in self._posts:
            if isinstance(post, SponsoredPost):
                extra = f" (реклама, бюджет {post.budget})"
            else:
                extra = ""
            print(f"{post.number:<5} {post.author:<20} {post.text:<30} {post.likes:<6}{extra}")

    # --- Статические методы для работы с CSV ---
    @staticmethod
    def read_from_csv(filename: str) -> 'PostCollection':
        """
        Статический метод: читает данные из CSV-файла и возвращает коллекцию постов.
        Поддерживает обычные и рекламные посты (если есть столбец 'бюджет').
        """
        collection = PostCollection()
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    try:
                        num = int(row['№'])
                        author = row['ник автора']
                        text = row['текст поста']
                        likes = int(row['количество лайков'])
                        if 'бюджет' in row and row['бюджет']:
                            budget = float(row['бюджет'])
                            post = SponsoredPost(num, author, text, likes, budget)
                        else:
                            post = Post(num, author, text, likes)
                        collection.add_post(post)
                    except (ValueError, KeyError, TypeError) as e:
                        print(f"Пропущена некорректная строка: {row}. Ошибка: {e}")
        except FileNotFoundError:
            print(f"Файл {filename} не найден. Будет создана пустая коллекция.")
        return collection

    @staticmethod
    def save_to_csv(filename: str, collection: 'PostCollection'):
        """
        Статический метод: сохраняет коллекцию постов в CSV-файл.
        Для рекламных постов добавляет столбец 'бюджет'.
        """
        fieldnames = ['№', 'ник автора', 'текст поста', 'количество лайков', 'бюджет']
        try:
            with open(filename, 'w', encoding='utf-8', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
                writer.writeheader()
                for post in collection:
                    row = {
                        '№': post.number,
                        'ник автора': post.author,
                        'текст поста': post.text,
                        'количество лайков': post.likes
                    }
                    if isinstance(post, SponsoredPost):
                        row['бюджет'] = post.budget
                    writer.writerow(row)
            print(f"Коллекция сохранена в {filename}.")
        except Exception as e:
            print(f"Ошибка сохранения: {e}")


# --------------------------- Вспомогательные функции ------------------------
def count_files_in_directory(directory: str) -> int:
    """Подсчитывает количество файлов (не папок) в указанной директории."""
    if not os.path.isdir(directory):
        raise FileNotFoundError(f"Директория '{directory}' не найдена.")
    files = [item for item in os.listdir(directory)
             if os.path.isfile(os.path.join(directory, item))]
    return len(files)


def get_next_post_number(collection: PostCollection) -> int:
    """Возвращает следующий номер для нового поста (максимальный номер + 1)."""
    if len(collection) == 0:
        return 1
    return max(p.number for p in collection) + 1


def add_post_interactively(collection: PostCollection):
    """Диалог добавления нового поста (обычного или рекламного)."""
    print("\nДобавление нового поста:")
    is_sponsored = input("Это рекламный пост? (y/n): ").strip().lower() == 'y'

    author = input("Ник автора: ").strip()
    while not author or not Post.is_valid_nickname(author):
        print("Ник должен состоять только из букв/цифр и не быть пустым.")
        author = input("Ник автора: ").strip()

    text = input("Текст поста: ").strip()
    while not text:
        print("Текст не может быть пустым.")
        text = input("Текст поста: ").strip()

    while True:
        try:
            likes = int(input("Количество лайков: "))
            if likes < 0:
                print("Число не может быть отрицательным.")
            else:
                break
        except ValueError:
            print("Введите целое число.")

    number = get_next_post_number(collection)

    if is_sponsored:
        while True:
            try:
                budget = float(input("Бюджет рекламы: "))
                if budget < 0:
                    print("Бюджет не может быть отрицательным.")
                else:
                    break
            except ValueError:
                print("Введите число.")
        post = SponsoredPost(number, author, text, likes, budget)
    else:
        post = Post(number, author, text, likes)

    collection.add_post(post)
    print("Пост успешно добавлен.")


# ------------------------------- Главное меню -------------------------------
def main():
    print("=" * 60)
    print("Лабораторная работа №4. Классы (Посты)")
    print("=" * 60)

    # 1. Подсчёт файлов в папке sample_data (без классов)
    directory = "sample_data"
    try:
        cnt = count_files_in_directory(directory)
        print(f"Количество файлов в папке '{directory}': {cnt}")
    except FileNotFoundError as e:
        print(e)
        print("Создайте папку sample_data с файлами в каталоге программы.")
        return

    # 2. Загрузка постов из data.csv
    filename = "data.csv"
    posts_collection = PostCollection.read_from_csv(filename)
    print(f"Загружено постов: {len(posts_collection)}")

    while True:
        print("\n" + "=" * 40)
        print("Меню:")
        print("1. Показать все посты")
        print("2. Показать посты, отсортированные по нику (А-Я)")
        print("3. Показать посты, отсортированные по лайкам (по убыванию)")
        print("4. Отфильтровать посты по минимальному числу лайков (генератор)")
        print("5. Добавить новый пост")
        print("6. Сохранить в файл")
        print("0. Выход")
        choice = input("Выбор: ").strip()

        if choice == '1':
            posts_collection.display()
        elif choice == '2':
            sorted_coll = posts_collection.sorted_by_author()
            sorted_coll.display()
        elif choice == '3':
            sorted_coll = posts_collection.sorted_by_likes()
            sorted_coll.display()
        elif choice == '4':
            try:
                min_likes = int(input("Минимальное число лайков (показать посты с лайками > этого): "))
                print(f"Посты с лайками > {min_likes}:")
                # Используем генератор
                for post in posts_collection.filter_by_likes_generator(min_likes):
                    print(post)
            except ValueError:
                print("Ошибка: введите целое число.")
        elif choice == '5':
            add_post_interactively(posts_collection)
        elif choice == '6':
            PostCollection.save_to_csv(filename, posts_collection)
        elif choice == '0':
            save = input("Сохранить изменения перед выходом? (y/n): ").lower()
            if save == 'y':
                PostCollection.save_to_csv(filename, posts_collection)
            print("Выход.")
            break
        else:
            print("Неверный ввод, попробуйте снова.")


if __name__ == "__main__":
    main()
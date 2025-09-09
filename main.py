# Импорт необходимых библиотек
import speech_recognition as sr  # Для распознавания речи
import pyttsx3  # Для синтеза речи (текст в голос)
import datetime  # Для работы с датой и временем
import pywhatkit  # Для воспроизведения YouTube видео и поиска
import wikipedia  # Для поиска информации в Wikipedia
import pyjokes  # Для генерации шуток
import time  # Для работы с задержками времени

# Настройка распознавателя с улучшенными параметрами
listener = sr.Recognizer()
listener.energy_threshold = 300  # Порог чувствительности микрофона
listener.dynamic_energy_threshold = True  # Автоподстройка чувствительности
listener.pause_threshold = 0.8  # Пауза для окончания фразы (в секундах)

# Инициализация синтезатора речи
alexa = pyttsx3.init()
voices = alexa.getProperty('voices')  # Получение списка доступных голосов
alexa.setProperty('voice', voices[1].id)  # Выбор женского голоса (обычно voices[1])
alexa.setProperty('rate', 150)  # Скорость речи (слов в минуту)


def talk(text):
    """
    Функция для озвучивания текста и вывода его в консоль
    """
    print(f"Alexa: {text}")  # Вывод текста в консоль
    alexa.say(text)  # Добавление текста в очередь для озвучивания
    alexa.runAndWait()  # Воспроизведение речи и ожидание завершения


def take_command():
    """
    Функция для прослушивания и распознавания голосовых команд
    Возвращает распознанную команду или пустую строку при ошибке
    """
    command = ""  # Инициализация переменной для команды
    try:
        # Открытие микрофона как источника аудио
        with sr.Microphone() as source:
            # Калибровка микрофона для фонового шума
            print("Calibrating microphone for ambient noise...")
            listener.adjust_for_ambient_noise(source, duration=1)

            print('Listening... (say "Alexa" followed by your command)')

            # Прослушивание аудио с улучшенными параметрами
            voice = listener.listen(
                source,
                timeout=3,  # Таймаут ожидания начала речи (3 секунды)
                phrase_time_limit=5  # Максимальная длина фразы (5 секунд)
            )

            # Распознавание речи с помощью Google Speech Recognition
            command = listener.recognize_google(voice, language='en-US')
            command = command.lower()  # Приведение к нижнему регистру
            print(f"Raw command: {command}")  # Вывод сырой команды

            # Проверка наличия ключевого слова "alexa"
            if 'alexa' in command:
                command = command.replace('alexa', '').strip()  # Удаление ключевого слова
                print(f"Processed command: {command}")  # Вывод обработанной команды
                return command
            else:
                print("Wake word 'Alexa' not detected")  # Ключевое слово не найдено
                return ""

    # Обработка различных типов исключений
    except sr.WaitTimeoutError:
        print("No speech detected within timeout")  # Таймаут ожидания речи
    except sr.UnknownValueError:
        print("Could not understand audio")  # Не удалось распознать аудио
    except sr.RequestError as e:
        print(f"Error with speech recognition service: {e}")  # Ошибка сервиса распознавания
    except Exception as e:
        print(f"Unexpected error: {e}")  # Непредвиденная ошибка

    return ""  # Возврат пустой строки при ошибке


def run_alexa():
    """
    Основная функция обработки команд
    Возвращает False для завершения работы, True для продолжения
    """
    print("\n" + "=" * 50)  # Разделитель в консоли
    print("Ready for command...")  # Сообщение о готовности

    command = take_command()  # Получение команды от пользователя

    # Проверка на пустую команду
    if not command:
        print("No valid command received")
        return True  # Продолжаем цикл

    print(f"Executing: {command}")  # Вывод выполняемой команды

    # Обработка команды времени
    if any(word in command for word in ['time', 'what time', 'current time']):
        time_str = datetime.datetime.now().strftime('%I:%M %p')  # Форматирование времени
        print(f"Time: {time_str}")
        talk(f'Current time is {time_str}')

    # Обработка команды воспроизведения музыки
    elif command.startswith('play'):
        song = command.replace('play', '').strip()  # Извлечение названия песни
        if song:
            talk(f'Playing {song}')
            pywhatkit.playonyt(song)  # Воспроизведение на YouTube
        else:
            talk("What would you like me to play?")

    # Обработка запросов информации из Wikipedia
    elif any(phrase in command for phrase in ['tell me about', 'who is', 'what is']):
        # Извлечение поискового запроса в зависимости от формата команды
        if 'tell me about' in command:
            look_for = command.replace('tell me about', '').strip()
        elif 'who is' in command:
            look_for = command.replace('who is', '').strip()
        elif 'what is' in command:
            look_for = command.replace('what is', '').strip()
        else:
            look_for = command.strip()

        if look_for:  # Проверка что запрос не пустой
            try:
                info = wikipedia.summary(look_for, sentences=2)  # Получение краткого описания
                print(f"Wikipedia info: {info}")
                talk(info)
            except wikipedia.exceptions.DisambiguationError as e:
                # Обработка неоднозначного запроса (несколько результатов)
                talk(f"There are multiple results for {look_for}. Please be more specific.")
            except wikipedia.exceptions.PageError:
                # Обработка отсутствия страницы
                talk(f"Sorry, I couldn't find information about {look_for}")
            except Exception as e:
                # Обработка других ошибок Wikipedia
                talk("Sorry, there was an error with Wikipedia")
                print(f"Wikipedia error: {e}")
        else:
            talk("Please tell me what you want to know about")

    # Обработка запроса шутки
    elif any(word in command for word in ['joke', 'tell joke', 'make me laugh']):
        joke = pyjokes.get_joke()  # Генерация шутки
        print(f"Joke: {joke}")
        talk(joke)

    # Обработка романтических предложений
    elif any(word in command for word in ['date', 'go out', 'relationship']):
        talk('Sorry, I am focused on helping you right now')

    # Обработка команд выхода
    elif any(word in command for word in ['stop', 'exit', 'quit', 'goodbye']):
        talk('Goodbye! Have a great day!')
        return False  # Сигнал для завершения работы

    # Обработка всех остальных команд - поиск в интернете
    else:
        talk('Let me search that for you')
        pywhatkit.search(command)  # Поиск через pywhatkit

    # Пауза перед следующей командой для стабильности
    time.sleep(2)
    return True  # Продолжение работы


def main():
    """
    Главная функция, запускающая основной цикл работы ассистента
    """
    talk("Hello! I'm Alexa, your voice assistant. Say 'Alexa' followed by your command.")

    try:
        # Основной бесконечный цикл работы ассистента
        while True:
            if not run_alexa():  # Запуск обработки команды
                break  # Выход из цикла если возвращено False
            # Короткая пауза между циклами для стабильности
            time.sleep(1)

    # Обработка прерывания клавишами Ctrl+C
    except KeyboardInterrupt:
        print("\nAlexa is shutting down. Goodbye!")
        talk("Goodbye!")
    # Обработка всех других исключений
    except Exception as e:
        print(f"Unexpected error: {e}")
        talk("Sorry, I encountered an error. Restarting...")
        time.sleep(2)
        main()  # Рекурсивный перезапуск при ошибке


# Точка входа в программу
if __name__ == "__main__":
    main()  # Запуск главной функции
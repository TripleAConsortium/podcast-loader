# podcast-loader

Скрипт для загрузки подкастов на mave.digital

## Нативный скрипт без внешних зависимостей (native_execution.py)

#### Требования
- Python 3.6 или выше (использует только стандартные библиотеки)
- ID подкаста на mave.digital

#### Инструкция

Скрипт использует только стандартные библиотеки Python и не требует установки дополнительных зависимостей.

```bash
python3 native_execution.py --email your@email.com --password yourpassword --podcast-id your-podcast-id --audio-file "/path/to/audio.mp3" --title "Episode Title" --description "Episode description"
```

#### Параметры

- `--email` - Email для входа на mave.digital
- `--password` - Пароль для входа на mave.digital
- `--podcast-id` - ID подкаста на mave.digital
- `--audio-file` - Путь к аудиофайлу для загрузки
- `--title` - Название эпизода
- `--description` - Описание эпизода
- `--season` - Номер сезона (опционально, по умолчанию 1)
- `--number` - Номер эпизода в сезоне (опционально, по умолчанию 1)
- `--explicit` - Пометить эпизод как содержащий контент для взрослых (опционально)
- `--private` - Пометить эпизод как приватный (опционально)

#### Процесс работы

1. Авторизация на mave.digital
2. Загрузка аудиофайла
3. Ожидание обработки аудио (с отображением статуса)
4. Публикация эпизода с указанными метаданными
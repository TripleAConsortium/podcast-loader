# podcast-loader

## Тебования
Перед работой необходимо установить [venv](https://docs.python.org/3/library/venv.html)

## Инструкция

- Для создания venv и установки зависимостей запустить **install.sh**
- Перед запуском создать файл **.env** и определить в нем:
    * PASSWORD 
    * LOGIN(email)
    * URL
- На сайте заранее должен быть в ручную создан подкаст
- Загрузка запускается c помощью **start.sh**: 

```bash
start.sh relaese_name /home/user/audio.mp3
```
# Загрузка комиксов xkcd в группу в VK

Код выгружает рандомный комикс с сайта [https://xkcd.com/](https://xkcd.com/) и публикует его на стене группы в VK.
Для корректной работы кода, требуется приложение в VK (зарегистрировать можно [тут](http://dev.vk.com/), у которого будет доступ на размещение публикаций в группе.

## Как установить

Python3 должен быть уже установлен.
* Скачайте код
* Установите зависимости  
```pip install -r requirements.txt```
* Запустите программу командой  
```python3 main.py```

## Переменные окружения

Для корректной работы кода необходимо указать переменные окружения. Для этого создайте файл `.env` рядом с `main.py` и запишите туда следующие обязательные переменые:
* `SUPERJOB_SECRET_KEY` - секретный ключ API сайта SuperJob.ru, который можно получить на странице [Superjob.ru API](https://api.superjob.ru/) после регистрации приложения.
* `SUPERJOB_APP_ID` - ID приложения, который присвается после регистрации на [Superjob.ru API](https://api.superjob.ru/).

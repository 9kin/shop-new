Shop
==========


|made-with-python| |GitHub forks| |GitHub stars| |GitHub watchers| |GitHub issues|

Shop - сайт собранный из отсчёта ``1c`` 

Проект для яндекс лицея.

Функционал
=============
    
    * чтение отсчёта из ``1c``
    * админ панель
    * поиск (elasticsearch)
    * cli утилита для сборки 
    * изменение/добавление:
    
        * ``TODO`` файла отсчёта через админ панель
        * изображений
        * администраторов
        * категорий и подкатегорий
        * ключевых слов
    * ``TODO`` введение логов        

----------------------------


build.py
=============

Функционал:
-------------
    
    * ``--sql`` собрать базу данных ``Item`` из отчёта
    * ``--key`` запустить обработку ключевых слов
    * ``--search`` проиндексировать базу данных ``Item``
    
Использует:
-----------

    * ``argparse``   (аргументы запуска)
    * ``multiprocessing.Pool``
    * `tqdm <https://github.com/tqdm/tqdm>`_ Progress Bar
    * `elasticsearch <https://github.com/elastic/elasticsearch-py>`_ для поиска
    * свой ``ext.Parser``
    
Как работает:
--------------

    * ``--sql`` и ``--key`` последовательно работают, используя ``ext.Parser``

    * ``--search`` работает, запуская пул процессов ``multiprocessing.Pool`` + ``elasticsearch`` для поиска

----------------------------

ext.py
=======

.. class:: ext.Parser
    

    используется для чтения и обработки данных

    .. function:: next_keyword

        следующая обработка строки по ключевым словам

    .. function:: next_1c

        следующая строка для db

--------------------

keywords.py
=============

.. class:: Keyword(keyword, routing)

    класс ключевого слова, который хранит:

        * keyword - шаблон (регулярное выражение)
        * routing - путь (куда надо вставить)
    
    .. function:: __eq__ 

        сравнение с использованием ``re.fullmatch``
          

.. class:: KeywordTable(keywords)

    класс ключевых слов
    
    проверка, есть ли слово в шаблонах


    .. function:: contains(item)

         проверка, есть ли слово в шаблонах



.. |made-with-python| image:: https://img.shields.io/badge/Made%20with-Python-1f425f.svg
    :alt: build status
    :scale: 100%


.. |GitHub forks| image:: https://img.shields.io/github/forks/9kin/shop.svg
    :alt: GitHub forks
    :scale: 100%

.. |GitHub stars| image:: https://img.shields.io/github/stars/9kin/shop.svg
    :alt: GitHub stars
    :scale: 100%

.. |GitHub watchers| image:: https://img.shields.io/github/watchers/9kin/shop.svg
    :alt: GitHub watchers
    :scale: 100%

.. |GitHub issues| image:: https://img.shields.io/github/issues/9kin/shop.svg
    :alt: GitHub issues
    :scale: 100%
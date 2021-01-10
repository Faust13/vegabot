# GFM Vega Clan Bot
Этот бот для автоматизации приема заявок на вступление в клан Destiny 2 Guardian FM.

## Настройка и запуск

Сам бот использует в качестве БД [Airtable](https://airtable.com/), поэтому для начала стоит зарегистрировать аккаунт там, после чего создать таблицу со следующими полями:

| Поле            | Тип         | 
| --------------- |:-----------:| 
| tg              | Single-line |
| name            | Single-line |
| xboxlive        | Single-line |
| age             | number(int) |
| about           | Long text   |
| chat_id         | Single-line |
| message_id      | Single-line |

все настройки указываются как переменные окружения в файле `bot.env`

| Параметр        | Default                                            | Описание                                                               | Допустимые значения    |
| --------------- |:--------------------------------------------------:| :----------------------------------------------------------------------| :----------------------|
| CLAN_NAME       | 'VEGA'                                             | Название клана                                                         | str                    |
| PLATFORM        | 'Xbox'                                             | Приоритетная платформа клана                                           | 'Xbox', 'PC' или 'PSN' |
| ATB_API_KEY     | ''                                                 | API-ключ Airtable                                                      | str                    |
| ATB_BASE_KEY    | ''                                                 | ID базы Airtable                                                       | str                    |
| ATB_TABLE       | ''                                                 | Название таблицы                                                       | str                    |
| TG_API_KEY      | ''                                                 | API-ключ Teleram                                                       | str                    |
| TG_ADMN_CHAT_ID | '-123'                                             | ID чата администрации клана, куда будут поступать заявки на вступление | str                    |
| CHAT_CLAN_LINK  | 'https://t.me/GuardianFM'                          | Ссылка на внутренний чат клана                                         | str                    |
| LFG_CLAN_LINK   | 'https://t.me/GuardianFM'                          | Ссылка на лфг-чат клана                                                | str                    |
| BNET_CLAN_LINK  | 'https://www.bungie.net/ru/ClanV2?groupid=2135560' | Ссылка на лфг-чат клана                                                | str                    |

Чтобы узнать ID своих чатов, можно воспользоваться [вот этим ботом](https://t.me/getmyid_bot).

Для запуска бота просто сделайте `docker-compose up -d`


## Благодарности

Хочу выразить благодарность [NikolasII](https://github.com/Nickolasll) за тотальное перелопачивание моего говнокода.
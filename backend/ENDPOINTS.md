****

### cases

**1. GET /api/cases/** \
***Response:***

````
{
  "status": "success",
  "items": [
    {
      "name": "Sigma Case",
      "price": 90.5,
      "image_url": "https://stickercasebucket.s3.eu-north-1.amazonaws.com/cases/plug.png",
      "base_fee": 20.0,
      "status": "active",
      "current_fee": 19.58228694282642
    }
  ]
}
````

Возвращает кейсы со статусом ACTIVE: \

- `name` название кейса
- `price` цена кейса
- `image_url` фоточка для фронтенда
- `base_fee` фи кейса на которую равняется `current_fee`, можно и ее в сериализаторе указать

Если добавить параметр ?pagination=true, то вернет с пагинацией:

````
{
  "status": "success",
  "count": 1,
  "next": null,
  "previous": null,
  "items": [
    {
      "name": "Sigma Case",
      "price": 90.5,
      "image_url": "https://stickercasebucket.s3.eu-north-1.amazonaws.com/cases/plug.png",
      "base_fee": 20.0,
      "status": "active",
      "current_fee": 19.58228694282642
    }
  ]
}
````

Если добавить параметр `name=Test Case`, то вернет один кейс

2. **GET /api/cases/Blum Case/items/** \
   ***Response:***

````
{
  "status": "success",
  "case": "Sigma Case",
  "items": [
    {
      "pack_name": "Gold bone",
      "collection_name": "DOGS Rewards",
      "pack_image": "",
      "chance": 0.0025,
      "case_name": "Sigma Case",
      "pack_floor_price": "18900.000"
    },
    {
      "pack_name": "Not Cap",
      "collection_name": "DOGS OG",
      "pack_image": "",
      "chance": 0.051798642533936665,
      "case_name": "Sigma Case",
      "pack_floor_price": "430.520"
    },
    {
      "pack_name": "Extra Eyes",
      "collection_name": "DOGS OG",
      "pack_image": "",
      "chance": 0.9457013574660634,
      "case_name": "Sigma Case",
      "pack_floor_price": "3.413"
    }
  ]
}
````

Возвращает стикерпаки которые связаны с кейсом (например Blum Case) через CaseItem: \

- `pack_name` название пака
- `pack_image` для фронта
- `chance` шанс на выпадение пака именно в этом кейсе
- `case_name` имя кейса
- `pack_floor_price` цена пака глобально

3. **POST, GET /api/cases/Blum Case/open**

***Request:***

````
{"telegram_id": "123456789"}
````

***Response:***

````
{
  "status": "success",
  "drop": {
    "pack_name": "Extra Eyes",
    "collection_name": "DOGS OG",
    "contributor": "Sticker Pack",
    "floor_price": 3.413,
    "image_url": "",
    "cases": [
      {
        "chance": 0.9457013574660634,
        "case_name": "Sigma Case",
      }
    ]
  },
  "drop_number": 654
}
````

Открытие кейсов. POST: Если отправить `"telegram_id"` то деньги спишутся с баланса юзера и он в инвентарь получит дроп.
GET: Если не отправлять `"telegram_id"` будет демо открытие.

- `pack_name` имя пака
- `collection_name` название коллекции
- `contributor` тот кто выпустил пак
- `floor_price` цена пака
- `status` статус пака
- `image_url` фотка пака
- `drop_number` число пака, нужно для определения в закупленной ликвидности

4. **PATCH /api/cases/update-chances/**

**Эндпоинт не используется для фронтенда!**

***Request:***

````
{
  "data": {
    "DOGS OG Case": [
      {"pack_name": "Cook", "collection_name": "DOGS OG", "chance": 0.047814798788403286},
      {"pack_name": "Teletubby", "collection_name": "DOGS OG", "chance": 0.9043704024231934},
      {"pack_name": "Pilot", "collection_name": "DOGS OG", "chance": 0.047814798788403286}
    ]
  }
}
````

***Response:***

````
{
  "info": 3
}
````

Обновляет шанс на выпадение пака в определенном кейсе:

- `chance` новый шанс на выпадение
- `collection_name` коллекция стикерпака


5. **PATCH /api/cases/update-cases/** \

**Эндпоинт не используется для фронтенда!**

***Request:***

````
{
  "data": {
    "Blum Case": 
      {"fee": 20.852280967709124}
    ,
    "DOGS OG Case": 
      {"price": 3.0, "fee": 19.999999999999986}
    ,
    "DOGS Rewards Case": 
      {"fee": 19.800141337436568}
    
  }
}
````

***Response:***

````
{
  "info": 3
}
````

Обновляет текущий фи и цену кейсов.
****

### packs

1. **GET /api/packs/** \
   ***Response:***

````
{
  "status": "success",
  "items": [
    {
      "pack_name": "Gold bone",
      "collection_name": "DOGS Rewards",
      "contributor": "Sticker Pack",
      "floor_price": 18900.0,
      "image_url": "",
      "cases": [
        {
          "chance": 0.0025,
          "case_name": "Sigma Case",
        }
      ]
    },
    {
      "pack_name": "Not Cap",
      "collection_name": "DOGS OG",
      "contributor": "Sticker Pack",
      "floor_price": 430.52,
      "image_url": "",
      "cases": [
        {
          "chance": 0.051798642533936665,
          "case_name": "Sigma Case",
        }
      ]
    },
    {
      "pack_name": "Pixioznik",
      "collection_name": "Not Pixel",
      "contributor": "Sticker Pack",
      "floor_price": 1.702,
      "image_url": "",
      "cases": []
    }
  ]
}
```` 

Возвращает стикерпаки: \

- `pack_name` название пака
- `collection_name` название коллекции пака
- `contributor` тот кто выпустил пак
- `floor_price` цена пака
- `status` статус пака
- `in_stock_count` сколько закуплено для ликвидности кейсов
- 'image_url' фотка

Если указать параметр `id=2`, вернет пак по его айди:

````
{
  "status": "success",
  "pack": {
    "id": 3,
    "pack_name": "Pixioznik",
    "collection_name": "Not Pixel",
    "contributor": "Sticker Pack",
    "floor_price": 1.702,
    "image_url": "",
    "cases": []
  }
}
````

2. **GET /api/packs/contributor/Sticker Pack/** \

***Response:***

````
{
  "status": "success",
  "items": [
    {
      "pack_name": "Gold bone",
      "collection_name": "DOGS Rewards",
      "contributor": "Sticker Pack",
      "floor_price": 18900.0,
      "image_url": "",
      "cases": [
        {
          "chance": 0.0025,
          "case_name": "Sigma Case"
        }
      ]
    },
    {
      "pack_name": "Not Cap",
      "collection_name": "DOGS OG",
      "contributor": "Sticker Pack",
      "floor_price": 430.52,
      "image_url": "",
      "cases": [
        {
          "chance": 0.051798642533936665,
          "case_name": "Sigma Case"
        }
      ]
    }
  ]
}
````

Фильтрует все паки по контрибьютору, например Sticker Pack \
Подключен кэш

3. **PATCH /api/packs/update-stickers-price/**

**Эндпоинт не используется для фронтенда!**

***Request:***

````
{"packs_data": {"DOGS OG": {"Cook": 5.969}}}
````

***Response:***

````
{
  "info": 1
}
````

Обновляет цены на стикеры

****

### users

1. GET /api/users/{telegram_id}/

***Response:***

````
{
  "status": "success",
  "user": {
    "telegram_id": 1380639458,
    "username": "vvalera808",
    "balance": 2312221.5,
    "image_url": "https://stickercasebucket.s3.eu-north-1.amazonaws.com/users/users/1380639458.jpg",
    "first_name": "Валера",
    "last_name": null,
    "language": "en",
    "is_bot": false
  }
}
````

Получить информацию о пользователе

2. GET /api/users/{telegram_id}/inventory/

***Response:***

````
{
  "status": "success",
  "inventory_count": 1,
  "inventory": [
    {
      "pack": {
        "id": 4,
        "pack_name": "Extra Eyes",
        "collection_name": "DOGS OG",
        "contributor": "Sticker Pack",
        "floor_price": 3.413,
        "image_url": "",
        "cases": [
          {
            "chance": 0.9457013574660634,
            "case_name": "Sigma Case"
          }
        ]
      },
      "number": 111,
      "id": 15
    }
  ]
}
````

Получить инвентарь пользователя

3. GET /api/users/{telegram_id}/transactions/

***Response:***

````
{
  "status": "success",
  "transaction_count": 28,
  "transactions": [
    {
      "type": "Case open",
      "data": {
        "price": 3.413,
        "date": "2025-10-12T10:41:16.473864Z",
        "drop_image_url": ""
      }
    },
    {
      "type": "Case open",
      "data": {
        "price": 3.413,
        "date": "2025-10-12T10:32:15.585404Z",
        "drop_image_url": ""
      }
    },
    {
      "type": "Sticker sell",
      "data": {
        "price": 13.3,
        "date": "2025-10-11T14:26:03.343895Z",
        "sticker_image_url": ""
      }
    },
    {
      "type": "Case open",
      "data": {
        "price": 18900.0,
        "date": "2025-10-11T13:29:35Z",
        "drop_image_url": ""
      }
    },
    {
      "type": "Upgrade",
      "data": {
        "success": false,
        "date": "2025-10-11T13:24:51.148736Z",
        "bet_image_url": "",
        "drop_image_url": "",
        "price": -121.56
      }
    }
  ]
}
````

Возвращает все транзакции совершенные пользователем отсортированно по времени (депозит, вывод, открытие кейса, продажа
стикера, апгрейд)

4. POST /api/users/user/

***Request:***

````
{
    "telegram_id": user_id,
    "first_name": first_name,
    "last_name": last_name,
    "username": username,
    "language": language_code,
    "is_bot": is_bot,
    "image_url": None
}
````

При нажатии /start в боте на этом эндпоинте создается юзер. `image_url` это ссылка на аватарку пользователя в бакете S3.

****

### wallet

1. POST /api/wallet/{telegram_id}/get-nonce/
   ***Request:***

````

{"telegram_id": 213113123}

````

***Response:***

````

{
"nonce": "A9cPYa107z5SjmHFwgc01jvcUi34Mg3s"
}

````

Получает серверный nonce для формирования message и подписи на сервере для подтверждения что юзер владеет кошем. Для
одного юзера нельзя создать несколько nonce одновременно. Работает только если юзер уже есть в бд.

2. POST /api/wallet/connect-wallet/
   ***Request:***

````

{
"signature": "Wm6MjqZRJ/kubFN2646dMswslHDfBOYX/ROCNeu3BKuPC9aGFmF6L7fnoF8FFVGG3jXDnPRCwEt+JztPpri+Ag==",
"message": "
wallet=v-syrom-formate-kosh&telegram_id=213123123&timestamp=1600002213&nonce=e4w101gYi1f-baoB07HqkoYiHi6Mc58K",
"public": "FrVLJTyLUYvDGp01ek0OWnMK82+9Ti4RChebSj8E+WE="
}

````

3. POST /api/wallet/withdrawal/

***Response:***

````

{
"message": "Wallet connected successfully"
}

````

Сверяет подпись и сообщение. Одноразовое использование. Работает только с nonce который сгенерировал сервер. В message
передается кош, телеграм айди, когда был подключен кош и nonce. Кош и подключение записывается в бд при 200 статусе.

3. POST /api/wallet/{telegram_id}/create-invoice/

***Response***

````

{"message": "Invoice created",
"address_to_pay": address,
"invoice_id": invoice_id
}

````

`address_to_pay` - возращает адрес на который нужно депнуть в красивом формате\
`invoice_id` - его нужно указать в комментарии при депе

Создание инвойса для оплаты пользователем. На одного пользователя может быть максимум один инвойс. Вызывается при
нажатии кнопки "пополнить". Инвойс живет сутки. Не фиксированная сумма депа

4. POST /api/wallet/{telegram_id}/check-deposit

***Response:***

````

{
"message": "Invoice is paid",
"status": InvoiceStatus.PAID,
"new_balance": balance
}

````

Срабатывает после того как пользователь нажимает кнопку "я депнул" или что то в этом духе. Если инвойс оплачен,
возвращает 200 и новый баланс. Чистится кэш и пользователь может снова создавать инвойс. Этот этап не скипаем. На
будущее, в случае если пользователь не нажал на кнопку, нужно будет все равно очистить кэш (придумаю на каком этапе). Во
всех остальных случаях вернет 400.
****

### Вебхуки и дополнительное

1. POST webhook/tonconsole/{uuid}/

***Request:***

````

{
"id": "string",
"status": "pending | paid | cancelled | expired",
"amount": "string",
"description": "string",
"date_create": 1234567890,
"date_expire": 1234567890,
"date_change": 1234567890,
"payment_link": "string",
"pay_to_address": "0:<hash>",
"paid_by_address": "0:<hash>",
"overpayment": "string"
}

````

Вебхук для получения статусов инвойсов от TonConsole.
****
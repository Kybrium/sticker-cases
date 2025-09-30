****

### cases

**1. GET /api/cases/** \
***Response:***

````
[
  {
    "name": "DOGS OG Case",
    "price": "3.500",
    "image_url": null,
    "base_fee": 20.0
  },
  {
    "name": "DOGS Rewards Case",
    "price": "2844.500",
    "image_url": null,
    "base_fee": 20.0
  },
  {
    "name": "Blum Case",
    "price": "1.500",
    "image_url": null,
    "base_fee": 20.0
  }
]
````

Возвращает кейсы со статусом ACTIVE: \

- `name` название кейса
- `price` цена кейса
- `image_url` фоточка для фронтенда
- `base_fee` фи кейса на которую равняется `current_fee`, можно и ее в сериализаторе указать

Пагинация возвращает по 2 объекта на раз. \

Если добавить параметр ?pagination=true, то вернет с пагинацией:

````
{ 
  "count": 3, 
  "next": "http://127.0.0.1:8000/api/cases/?limit=2&offset=2", 
  "previous": null, 
  "results": [ 
    { 
      "name": "DOGS OG Case", 
      "price": "3.500", 
      "image_url": null, 
      "base_fee": 20.0 
    }, 
    { 
      "name": "DOGS Rewards Case", 
      "price": "2844.500", 
      "image_url": null, 
      "base_fee": 20.0 
    } 
  ] 
} 
````

2. **GET /api/cases/case/Blum Case/** \
   ***Response:***

````
[
  {
    "pack_name": "Cook",
    "pack_image": "",
    "chance": 0.4,
    "case_name": "Blum Case",
    "pack_floor_price": "0.850"
  },
  {
    "pack_name": "Curly",
    "pack_image": "",
    "chance": 0.287767499166936,
    "case_name": "Blum Case",
    "pack_floor_price": "0.820"
  },
  {
    "pack_name": "Cap",
    "pack_image": "",
    "chance": 0.3075561556651276,
    "case_name": "Blum Case",
    "pack_floor_price": "2.588"
  }
]
````

Возвращает стикерпаки которые связаны с кейсом (например Blum Case) через CaseItem: \

- `pack_name` название пака
- `pack_image` для фронта
- `chance` шанс на выпадение пака именно в этом кейсе
- `case_name` имя кейса
- `pack_floor_price` цена пака глобально

3. **POST, GET /api/cases/case/Blum Case/open**

***Request:***

````
{"telegram_id": "123456789"}
````

***Response:***

````
{
  "drop": {
    "pack_name": "Cook",
    "collection_name": "Blum",
    "contributor": "Sticker Pack",
    "floor_price": "0.850",
    "status": "in_stock",
    "in_stock_count": 0,
    "image_url": null
 },
  "drop_number": "213" 
}
````

Открытие кейсов. POST: Если указать `"telegram_id"` то деньги спишутся с баланса юзера и он в инвентарь получит дроп.
GET: Если не указывать, никакой логике на сервере указано не будет.

- `pack_name` имя пака
- `collection_name` название коллекции
- `contributor` тот кто выпустил пак
- `floor_price` цена пака
- `status` статус пака
- `image_url` фотка пака
- `drop_number` число пака, нужно для определения в закупленной ликвидности

4. **PATCH /api/cases/update-chances/** \
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

Эндпоинт используется только в логике с price_update

5. **PATCH /api/cases/update-cases/** \
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

Обновляет текущий фи и цену кейсов. \

Используется только внутри логики price_update
****

### packs

1. **GET /api/packs/** \
   ***Response:***

````
[
  {
    "pack_name": "Silver bone",
    "collection_name": "DOGS Rewards",
    "contributor": "Sticker Pack",
    "floor_price": "51.228",
    "status": "out_of_stock",
    "in_stock_count": 0,
    "image_url": null
  },
  {
    "pack_name": "Full dig",
    "collection_name": "DOGS Rewards",
    "contributor": "Sticker Pack",
    "floor_price": "1.080",
    "status": "out_of_stock",
    "in_stock_count": 0,
    "image_url": null
  },
  {
    "pack_name": "Cook",
    "collection_name": "DOGS OG",
    "contributor": "Sticker Pack",
    "floor_price": "5.738",
    "status": "in_stock",
    "in_stock_count": 1,
    "image_url": null
  }]
```` 

Возвращает стикерпаки: \

- `pack_name` название пака
- `collection_name` название коллекции пака
- `contributor` тот кто выпустил пак
- `floor_price` цена пака
- `status` статус пака
- `in_stock_count` сколько закуплено для ликвидности кейсов
- 'image_url' фотка

2. **GET /api/packs/contributor/?contributor=Sticker Pack** \
   ***Response:***

````
[
  {
    "pack_name": "Silver bone",
    "collection_name": "DOGS Rewards",
    "contributor": "Sticker Pack",
    "floor_price": "51.228",
    "status": "out_of_stock",
    "in_stock_count": 0,
    "image_url": null
  },
  {
    "pack_name": "Full dig",
    "collection_name": "DOGS Rewards",
    "contributor": "Sticker Pack",
    "floor_price": "1.080",
    "status": "out_of_stock",
    "in_stock_count": 0,
    "image_url": null
  },
  {
    "pack_name": "Cook",
    "collection_name": "DOGS OG",
    "contributor": "Sticker Pack",
    "floor_price": "5.738",
    "status": "in_stock",
    "in_stock_count": 1,
    "image_url": null
  }]
````

Фильтрует все паки по контрибьютору, например Sticker Pack \
Подключен кэш

3. **GET /api/packs/DOGS OG/Pilot/** \
   ***Response***

````
{
  "pack_name": "Pilot",
  "collection_name": "DOGS OG",
  "contributor": "Sticker Pack",
  "floor_price": "5.589",
  "status": "in_stock",
  "in_stock_count": 0,
  "image_url": null
}
````

Возвращает стикерпак по его названию и коллекции

4. **PATCH /api/packs/update-stickers-price/**
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

****

### wallet

1. POST /api/wallet/get-nonce/
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
  "message": "wallet=v-syrom-formate-kosh&telegram_id=213123123&timestamp=1600002213&nonce=e4w101gYi1f-baoB07HqkoYiHi6Mc58K",
  "public": "FrVLJTyLUYvDGp01ek0OWnMK82+9Ti4RChebSj8E+WE="
}
````

***Response:***

````
{
    "message": "Wallet connected successfully"
}


````

Сверяет подпись и сообщение. Одноразовое использование. Работает только с nonce который сгенерировал сервер. В message
передается кош, телеграм айди, когда был подключен кош и nonce. Кош и подключение записывается в бд при 200 статусе.

3. POST /api/wallet/create-invoice

***Request***

````
{"telegram_id": "321321"}
````

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

4. POST /api/wallet/check-deposit

***Request:***

````
{"telegram_id": "321321"}
````

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

1. GET /tonconnect-manifest.json/
   ***Response:***

````
{
  "url": "http://localhost:8080",
  "name": "TON Connect Demo"
}
````

Необходим для корректной работы ton connect на клиенте

2. POST webhook/tonconsole/uuid

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
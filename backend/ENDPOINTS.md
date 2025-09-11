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
- `base_fee` фи кейса на которую равняется `current_fee`, можно и ее  в сериализаторе указать

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
Возвращает стикерпаки которые связаны с кейсом (например Blum Case) через CaseItems: \
- `pack_name` название пака
- `pack_image` для фронта
- `chance` шанс на выпадение пака именно в этом кейсе
- `case_name` имя кейса
- `pack_floor_price` цена пака глобально

3. **GET /api/cases/case/Blum Case/demo-open**
***Response:***
````
{
  "pack": {
    "pack_name": "Cook",
    "collection_name": "Blum",
    "contributor": "Sticker Pack",
    "floor_price": "0.850",
    "status": "in_stock",
    "in_stock_count": 0,
    "image_url": null
  }
}
````
Позволяет открыть кейс в демо режиме. Никаких записей в бд нету:
- `pack_name` имя пака
- `collection_name` название коллекции
- `contributor` тот кто выпустил пак
- `floor_price` цена пака
- `status` статус пака
- `in_stock_count` сколько закуплено паков для ликвидности 
- "image_url" фотка пака

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
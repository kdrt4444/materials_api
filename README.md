# Materials API

API-сервис на Django + DRF для работы с иерархией категорий и связанных с ними материалов. Поддерживает загрузку данных из Excel, расчёт стоимости материалов по категориям и дерево категорий.

---

## Возможности

- Получение дерева всех **корневых категорий**:  
  `GET /api/categories/`

- Получение дерева **определённой категории по коду**:  
  `GET /api/categories/<code>/`

- Загрузка материалов из Excel-файла:  
  `POST /api/materials/upload-excel/`

- Работа с материалами (CRUD):  
  `POST /api/materials/`, `PUT`, `DELETE`

- Работа с материалами (CRUD):  
  `GET /api/materials/`, `POST`, `PUT`, `DELETE`

---

## Структура проекта

```bash
materials_api/
├── materials/                # Основное приложение
│   ├── migrations/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py            
│   ├── serializers.py        
│   ├── urls.py
│   ├── views.py              
├── materials_api/            # Конфигурация проекта
│   ├── settings.py
│   ├── urls.py
├── fixtures/                 # Пример фикстур
│   └── categories.example.json
├── docker-compose.yml
├── Dockerfile
├── manage.py
├── requirements.txt
└── .env.example              # Пример конфигурации окружения
```

---

## Установка

### 1. Клонируйте репозиторий

```bash
git clone https://github.com/yourusername/materials_api.git
cd materials_api
```

### 2. Создайте и настройте `.env`

Скопируйте `.env.example`:

```bash
cp .env.example .env
```


### 3. Запуск в Docker

```bash
docker-compose up --build
```

## Формат Excel-файла

При импорте материалов через `/api/materials/upload-excel/` файл должен содержать колонки:

- `name` — название материала
- `code` — уникальный код
- `category_code` — код категории
- `price` — цена

---

## Примеры запросов

### Получить дерево корневых категорий

```http
GET /api/categories/
```

### Получить конкретную категорию и её подкатегории

```http
GET /api/categories/ABC123/
```

### Загрузить Excel-файл с материалами

```http
POST /api/materials/upload-excel/
Content-Type: multipart/form-data
```

---

## Используемые технологии

-   Python 3.11
    
-   Django 5.2
    
-   Django REST Framework
    
-   PostgreSQL
    
-   Docker / Docker Compose
    
-   pandas

---

## Автор

Контакт: `nikitazinovkin676@gmail.com`

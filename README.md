# UNI-T UDP1306C Power Supply Control

Python-додаток для керування лабораторним блоком живлення **UNI-T UDP1306C** через USB.

## Вимоги

- Python **3.13+** ([python.org](https://www.python.org/downloads/) — потрібен вбудований `tkinter`)
- [PDM](https://pdm-project.org/)
- USB-з'єднання з блоком живлення


## Встановлення

### 1. Створити віртуальне середовище і встановити PDM

```bash
python3 -m venv .venv
source .venv/bin/activate      # macOS / Linux
# або .venv\Scripts\activate   # Windows
pip install pdm
```

### 2. Встановити залежності проекту

```bash
pdm install
```

## Запуск

```bash
pdm run gui
```

## Графічний інтерфейс

| Зона | Опис |
|------|------|
| Дисплей | Реальний час: напруга (V), струм (A), потужність (W), режим CV/CC |
| Параметри | Задання напруги та струму — спінбокс + слайдер |
| M1–M5 | Слоти пам'яті: коротке натискання = recall, довге (600 мс) = save |
| OVP / OCP | Увімк/вимк захист від перенапруги/перевантаження + поріг |
| OUTPUT | Увімкнення/вимкнення виходу |
| Графік | Voltage / Current / Power у реальному часі, збереження як зображення |
| Таблиця | Журнал вимірювань з експортом у CSV |

### Налаштування (кнопка Options)

| Параметр | За замовч. | Опис |
|----------|-----------|------|
| Мова | Українська | uk / en |
| Sample points | 10 000 | Макс. кількість точок у графіку та таблиці |
| Infinite | ✓ | Не обмежувати кількість точок |
| Skip repeated | ✗ | Пропускати однакові виміри підряд |
| Poll interval | 4 с | Інтервал опитування пристрою |

### Підключення по USB

На macOS порт зазвичай `/dev/cu.usbmodem*`. Для пошуку:

```bash
python -c "from device import find_port; print(find_port())"
```

Швидкість: 9600 бод, 8N1.

## Структура проекту

```
.
├── device.py               # Драйвер UDP1306C — SCPI по USB, threading.Lock
├── settings.py             # AppSettings dataclass + JSON-персистентність
├── i18n.py                 # Таблиці рядків uk/en + Translator
├── poller.py               # PollWorker (фонова нитка), Sample, PollError
├── main.py                 # Точка входу
├── gui/
│   ├── app.py              # App — з'єднує всі панелі
│   ├── widgets.py          # HoldButton, Debounce
│   ├── dialogs.py          # ConnectDialog, OptionsDialog
│   └── panels/
│       ├── display.py      # LCD-дисплей
│       ├── setpoint.py     # V/I спінбокси + слайдери
│       ├── memctrl.py      # M1–M5, OVP, OCP, OUTPUT
│       ├── chart.py        # matplotlib-графік
│       └── datalog.py      # treeview + CSV
└── tests/
    ├── unit/               # Юніт-тести (unittest + coverage.py)
    └── features/           # BDD acceptance-тести (behave) — потрібен пристрій
        └── README.md
```

## Тести

### Юніт-тести

Запуск без підключеного пристрою. Serial-порт замінений моком.

```bash
pdm run unit
```

Виводить покриття у термінал та HTML-звіт у `htmlcov/index.html`.  
Покриття: **100%** (device / i18n / poller / settings).

### BDD acceptance-тести

Потребують фізично підключеного блоку живлення.  
Детальніше: [tests/features/README.md](tests/features/README.md)

```bash
pdm run bdd
```

## SCPI команди

| Команда | Опис |
|---------|------|
| `*IDN?` | Ідентифікація пристрою |
| `*SAV <1-5>` | Зберегти налаштування в слот |
| `*RCL <1-5>` | Завантажити налаштування зі слоту |
| `VOLTage <V>` | Задати напругу |
| `CURRent <A>` | Задати струм |
| `MEASure:VOLTage?` | Виміряти напругу |
| `MEASure:CURRent?` | Виміряти струм |
| `MEASure:POWEr?` | Виміряти потужність |
| `OUTPut ON\|OFF` | Керування виходом |
| `OVP:STATus ON\|OFF` | Захист від перенапруги |
| `OVP:SETting <V>` | Поріг OVP |
| `OCP:STATus ON\|OFF` | Захист від перевантаження |
| `OCP:SETting <A>` | Поріг OCP |
| `SYSTem:STATus?` | Стан пристрою (hex-бітмаска: 0x01=CC, 0x02=OUT, 0x04=OVP, 0x08=OCP) |

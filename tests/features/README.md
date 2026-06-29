# BDD Acceptance Tests — UNI-T UDP1306C

Acceptance-тести перевіряють поведінку реального блоку живлення через USB.  
Написані на [Behave](https://behave.readthedocs.io/) (Gherkin + Python).

> Тести потребують **фізично підключеного** пристрою. Без пристрою сценарії автоматично переходять у стан `SKIP`.

## Структура

```
tests/features/
├── environment.py          # Хуки before/after scenario: відкрити/закрити USB-порт
├── connection.feature      # IDN, версія прошивки
├── voltage.feature         # Задання напруги (0–32 V)
├── current.feature         # Задання струму (0–6 A)
├── output.feature          # Увімкнення/вимкнення виходу
├── protection.feature      # OVP та OCP (enable/disable + threshold)
├── memory.feature          # Збереження та відновлення пресетів M1–M5
└── steps/
    ├── connection_steps.py # IDN, version
    ├── control_steps.py    # voltage, current, output, memory
    └── protection_steps.py # OVP, OCP
```

## Вимоги

```bash
pdm install   # behave встановлюється автоматично як dev-залежність
```

## Запуск

### Всі тести

```bash
pdm run bdd
```

### Один feature-файл

```bash
pdm run bdd tests/features/voltage.feature
```

### Явно вказати порт

```bash
UDP1306C_PORT=/dev/cu.usbmodem1401 pdm run bdd
```

### Фільтрація за тегом

```bash
pdm run bdd --tags @device        # тільки тести з пристроєм (всі)
pdm run bdd --tags ~@device       # пропустити тести з пристроєм
```

### Dry-run (перевірити кроки без запуску)

```bash
pdm run bdd --dry-run
```

## Пошук порту

Якщо `UDP1306C_PORT` не задано, `environment.py` викликає `find_port()` з `device.py`, яка шукає порт за ключовими словами (`uni-t`, `udp`, `usbmodem`, `ttyACM`).

Щоб знайти порт вручну:

```bash
pdm run test --list-ports
# або
python -c "from device import find_port; print(find_port())"
```

## Поведінка при відсутності пристрою

Кожен сценарій позначений тегом `@device`. У хуку `before_scenario` відбувається:

1. Пошук порту через `find_port()` або `UDP1306C_PORT`
2. Якщо порт не знайдено → `scenario.skip(...)` — сценарій пропускається, **не падає**
3. Якщо порт знайдено, але порт не відповідає → `scenario.skip(...)`
4. Після кожного сценарію — `output(False)` (безпека) + `device.close()`

## Features та сценарії

### connection.feature

```gherkin
Scenario: Identify the power supply
  When I query identification
  Then the response contains "UDP1306C"

Scenario: Read firmware version
  When I query the firmware version
  Then the response is not empty
```

### voltage.feature

Перевіряє задання напруги для 5 значень: 0, 5, 12, 24, 32 V.  
Допуск: ±0.05 V (обмеження АЦП пристрою).

```gherkin
Scenario Outline: Set output voltage
  When I set voltage to <volts> V
  Then the voltage setpoint reads <volts> V within 0.05
```

### current.feature

Перевіряє задання струму для 5 значень: 0, 0.5, 1, 3, 6 A.  
Допуск: ±0.01 A.

### output.feature

```gherkin
Scenario: Turn output ON
Scenario: Turn output OFF
```

Перевіряє `SYSTem:STATus?` після кожної команди.

### protection.feature

```gherkin
Scenario: Enable OVP with threshold 13.00 V
Scenario: Disable OVP
Scenario: Enable OCP with threshold 2.000 A
Scenario: Disable OCP
```

Кожен сценарій перевіряє і прапорець у статусі, і числове значення порогу.

### memory.feature

Зберігає 10 V / 1 A у слот, скидає значення до 0, відновлює зі слоту.  
Перевіряє слоти M1, M3, M5.

```gherkin
Scenario Outline: Save and recall a preset
  Given I set voltage to 10.00 V
  And I set current to 1.000 A
  When I save to memory slot <slot>
  And I set voltage to 0.00 V
  ...
  And I recall memory slot <slot>
  Then the voltage setpoint reads 10.00 V within 0.05
```

## Безпека

- Вихід завжди вимикається (`output(False)`) після кожного сценарію у `after_scenario`
- Тести задають напругу та струм **тільки на спінбоксах**, вихід вмикається явно лише у `output.feature`
- Перед запуском переконайтесь, що до виходу нічого не підключено

## Приклад виводу

```
Feature: Voltage setpoint control

  Scenario Outline: Set output voltage -- @1.1
    Given the power supply is connected        ... passed in 0.001s
    And the output is OFF                      ... passed in 0.320s
    When I set voltage to 0.00 V               ... passed in 0.352s
    Then the voltage setpoint reads 0.00 V within 0.05 ... passed in 0.302s

  Scenario Outline: Set output voltage -- @1.2
    ...

5 features passed, 0 failed, 0 skipped
21 scenarios passed, 0 failed, 0 skipped
```

## Додавання нових тестів

1. Створити або відредагувати `.feature`-файл у `tests/features/`
2. Якщо потрібні нові кроки — додати їх у відповідний файл у `steps/`
3. Перевірити кроки без запуску: `pdm run bdd --dry-run`
4. Запустити з пристроєм: `pdm run bdd`

---

## Синтаксис Gherkin — як писати нові тести

### Структура `.feature` файлу

```gherkin
@device
Feature: Назва функціональності

  Background:
    Given the power supply is connected   # виконується перед КОЖНИМ сценарієм
    And the output is OFF

  Scenario: Назва сценарію
    Given початковий стан
    When  дія
    Then  очікуваний результат
```

---

### Ключові слова

| Слово | Роль |
|-------|------|
| `Feature` | Назва групи сценаріїв (один файл = один feature) |
| `Background` | Кроки, що виконуються перед кожним сценарієм у файлі |
| `Scenario` | Один тест-кейс |
| `Scenario Outline` | Параметризований сценарій з таблицею |
| `Given` | Встановлює початковий стан |
| `When` | Дія або команда |
| `Then` | Перевірка результату |
| `And` | Продовжує попередній Given / When / Then |
| `But` | Те саме, що `And` (зазвичай для заперечень) |
| `@тег` | Мітка для фільтрації: `@device`, `@slow` тощо |

`And` і `But` — це синтаксичний цукор для читабельності, behave виконує їх як продовження попереднього типу.

---

### Числові параметри у кроках

Там де в кроках є `{V}`, `{A}`, `{W}`, `{tol}`, `{N}` — підставляй конкретне число:

```gherkin
When  I set voltage to 12.00 V          # {V} = 12.00
Then  the voltage setpoint is 12.00 V   # автоматичний допуск ±0.05
Then  the voltage setpoint reads 12.00 V within 0.10   # явний допуск
When  I save to memory slot 2           # {N} = 2  (ціле число)
```

Параметр `{ON|OFF}` — підставляй одне з двох слів:

```gherkin
Given  the output is OFF
When   I turn the output ON
Then   the status shows output is ON
```

Параметр `{enabled|disabled}` — для OVP/OCP:

```gherkin
Given  OVP is disabled
Then   the status shows OVP is enabled
```

---

### `Scenario Outline` — один сценарій для багатьох значень

```gherkin
Scenario Outline: Set output voltage
  Given the power supply is connected
  And the output is OFF
  When  I set voltage to <volts> V
  Then  the voltage setpoint is <volts> V

  Examples:
    | volts |
    |  0.00 |
    |  5.00 |
    | 12.00 |
    | 24.00 |
```

Behave запускає сценарій окремо для кожного рядка таблиці. `<volts>` — назва стовпця.  
Таблиця може мати кілька стовпців:

```gherkin
  Examples:
    | volts | current |
    |  5.00 |   1.000 |
    | 12.00 |   2.000 |
```

---

### Теги — фільтрація при запуску

```gherkin
@device
Feature: Voltage control       # тег на весь feature — всі сценарії отримають @device

  @slow
  Scenario: Long stabilisation  # додатковий тег лише на цей сценарій
```

```bash
pdm run bdd                                    # всі тести
pdm run bdd --tags @device                     # тільки @device
pdm run bdd --tags ~@slow                      # виключити @slow
pdm run bdd --tags "@device and not @slow"     # комбінація
```

Усі поточні feature-файли вже мають тег `@device` — без підключеного пристрою вони автоматично пропускаються (`SKIP`).

---

### Всі доступні кроки

**З'єднання та запити**
```gherkin
Given  the power supply is connected              # підтверджує що пристрій підключений (обов'язковий перший крок)
When   I query identification                     # надсилає *IDN? → зберігає відповідь у context.response
When   I query the firmware version               # надсилає SYSTem:VERSion? → context.response
When   I query the error status                   # надсилає SYSTem:ERRor? → context.response
When   I read the device status                   # надсилає SYSTem:STATus? → context.response (hex)
Then   the response contains "TEXT"               # перевіряє що context.response містить підрядок TEXT
Then   the response equals "TEXT"                 # перевіряє точну відповідність відповіді
Then   the response is not empty                  # перевіряє що відповідь не порожня
```

**Режим та статус**
```gherkin
Then   the device is in CV mode                   # перевіряє що пристрій у режимі стабілізації напруги
Then   the device is in CC mode                   # перевіряє що пристрій у режимі стабілізації струму
Then   the device mode is {CV|CC}                 # перевіряє режим: CV або CC
Then   the status shows output is {ON|OFF}        # перевіряє стан виходу через SYSTem:STATus?
Then   the status shows OVP is {enabled|disabled} # перевіряє стан захисту від перенапруги
Then   the status shows OCP is {enabled|disabled} # перевіряє стан захисту від перевантаження
```

**Напруга (setpoint)**
```gherkin
Given/When  I set voltage to {V} V                # надсилає VOLTage {V} — задає напругу на виході
Given/When  the voltage is set to {V} V           # те саме, alias для читабельності в Given
Then        the voltage setpoint reads {V} V within {tol}  # зчитує VOLTage? і перевіряє з явним допуском
Then        the voltage setpoint is {V} V         # зчитує VOLTage? і перевіряє з допуском ±0.05 V
```

**Струм (setpoint)**
```gherkin
Given/When  I set current to {A} A                # надсилає CURRent {A} — задає ліміт струму
Given/When  the current is set to {A} A           # те саме, alias для читабельності в Given
Then        the current setpoint reads {A} A within {tol}  # зчитує CURRent? і перевіряє з явним допуском
Then        the current setpoint is {A} A         # зчитує CURRent? і перевіряє з допуском ±0.01 A
```

**Живий вимір на виході**
```gherkin
When   I measure the output voltage               # надсилає MEASure:VOLTage? → context.measured_voltage
When   I measure the output current               # надсилає MEASure:CURRent? → context.measured_current
When   I measure the output power                 # надсилає MEASure:POWEr?   → context.measured_power
When   I take a measurement                       # вимірює V, A, W одночасно → зберігає всі три
Then   the measured voltage is {V} V within {tol} # перевіряє context.measured_voltage з явним допуском
Then   the measured current is {A} A within {tol} # перевіряє context.measured_current з явним допуском
Then   the measured power is {W} W within {tol}   # перевіряє context.measured_power з явним допуском
Then   the measured voltage is approximately {V} V # перевіряє напругу з допуском ±0.20 V (навантаження)
Then   the measured current is approximately {A} A # перевіряє струм з допуском ±0.05 A
```

**Вихід**
```gherkin
Given/When  the output is {ON|OFF}                # вмикає або вимикає вихід (OUTPut ON/OFF)
When        I turn the output {ON|OFF}            # те саме, більш природній варіант для When
When        I enable the output                   # вмикає вихід (OUTPut ON)
When        I disable the output                  # вимикає вихід (OUTPut OFF)
```

**OVP — захист від перенапруги**
```gherkin
Given  OVP is {enabled|disabled}                  # вмикає або вимикає OVP як передумову
Given  OVP threshold is {V} V                     # задає поріг OVP без зміни стану enabled/disabled
When   I enable OVP                               # вмикає OVP (OVP:STATus ON)
When   I disable OVP                              # вимикає OVP (OVP:STATus OFF)
When   I enable OVP with threshold {V} V          # задає поріг і одночасно вмикає OVP
When   I set the OVP threshold to {V} V           # тільки задає поріг (OVP:SETting), не вмикає
When   I set OVP to {V} V                         # те саме, скорочений alias
Then   the OVP threshold reads {V} V within {tol} # зчитує OVP:VALUE? і перевіряє з явним допуском
Then   the OVP threshold is {V} V                 # зчитує OVP:VALUE? і перевіряє з допуском ±0.05 V
```

**OCP — захист від перевантаження**
```gherkin
Given  OCP is {enabled|disabled}                  # вмикає або вимикає OCP як передумову
Given  OCP threshold is {A} A                     # задає поріг OCP без зміни стану enabled/disabled
When   I enable OCP                               # вмикає OCP (OCP:STATus ON)
When   I disable OCP                              # вимикає OCP (OCP:STATus OFF)
When   I enable OCP with threshold {A} A          # задає поріг і одночасно вмикає OCP
When   I set the OCP threshold to {A} A           # тільки задає поріг (OCP:SETting), не вмикає
When   I set OCP to {A} A                         # те саме, скорочений alias
Then   the OCP threshold reads {A} A within {tol} # зчитує OCP:VALUE? і перевіряє з явним допуском
Then   the OCP threshold is {A} A                 # зчитує OCP:VALUE? і перевіряє з допуском ±0.01 A
```

**Слоти пам'яті (1–5)**
```gherkin
When   I save to memory slot {N}                  # зберігає поточні V/I в слот N (*SAV N)
When   I save settings to memory slot {N}         # те саме, повна форма
When   I recall memory slot {N}                   # відновлює V/I зі слоту N (*RCL N)
When   I load memory slot {N}                     # те саме, alias
When   I restore memory slot {N}                  # те саме, alias
```

**Пауза**
```gherkin
When   I wait {N} seconds                         # пауза N секунд (для стабілізації або витримки)
```

---

### Приклад тесту

```gherkin
# tests/features/measure.feature
@device
Feature: Live output measurements

  Background:
    Given the power supply is connected
    And the output is OFF

  Scenario: Voltage on output matches setpoint
    Given I set voltage to 5.00 V
    And I set current to 1.000 A
    When I enable the output
    And I take a measurement
    Then the measured voltage is approximately 5.00 V
    And the status shows output is ON
    And the device is in CV mode

  Scenario Outline: Verify multiple voltage levels
    Given I set voltage to <volts> V
    When I enable the output
    Then the measured voltage is <volts> V within 0.20

    Examples:
      | volts |
      |  3.30 |
      |  5.00 |
      | 12.00 |
```

Зберегти файл → запустити:

```bash
pdm run bdd tests/features/measure.feature
# або перевірити без пристрою:
pdm run bdd --dry-run
```

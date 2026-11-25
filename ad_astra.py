"""
Ad astra

Карта світу:
  Кафе — Площа — Дослідницький центр — Бібліотека
           |               |
          Дім         Обсерваторія
           |
          Дах
"""

import random
import textwrap

# ------- Just basic game data

SETTINGS = {
    "max_days": 3,
    "actions_per_day": 6,
    "max_energy": 10,
    "max_bond": 5,
    "quit_word": "q",
    "commands": {
        "i": "inventory",
        "s": "status",
        "j": "journal",
        "?": "help",
        "g": "glossary",
    },
    "required": {"фотометрія", "спектроскопія", "астрометрія"},
    "measure_order": ("фотометрія", "спектроскопія", "астрометрія"),
    "measure_text": {
        "фотометрія": "Крива блиску: яскравість коливається з амплітудою {:.2f} зор. вел.",
        "спектроскопія": "Спектр: лінії зміщені в червоний бік, z = {:.3f}.",
        "астрометрія": "Положення: об'єкт зсувається на {:.3f}″ за годину.",
    },
}


# словничок незнайомих слів: слово -> пояснення
GLOSSARY = {
    "Аномалія": "Щось у небі, що поводиться не так, як очікується, і чого "
    "немає в жодному каталозі. Може виявитися новим відкриттям.",
    "Артефакт": "Хибний сигнал, який лише здається аномалією: відблиск "
    "супутника, космічного модуля чи збій приладу. Справжнього об'єкта немає.",
    "Фотометрія": "Вимірювання яскравості об'єкта з часом. Показує, наскільки "
    "сильно він спалахує чи тьмяніє (амплітуда в зоряних величинах).",
    "Спектроскопія": "Розкладання світла об'єкта на кольори (спектр). За "
    "зсувом ліній у спектрі можна дізнатися, як далеко об'єкт і як він рухається.",
    "Астрометрія": "Точне вимірювання положення об'єкта на небі. Далекі об'єкти "
    "майже не зсуваються, а близькі (супутники, модулі) рухаються помітно.",
    "Орерій": "Механічна модель Сонячної системи: планети на дротах обертаються "
    "навколо Сонця, як справжні.",
}


WORLD = {
    "home": {
        "name": "Дім",
        "description": (
            "Твоя затишна квартира в будинку, який наче з іншого світу. "
            "На столі стоїть чайничок, який ти купив у міжзоряній 'Дзизі', "
            "всюди розкидані нотатки, стоїть телескоп біля вікна і драбина на дах."
        ),
        "exits": ("plaza", "roof"),
        "sky_quality": 0.3,
    },
    "roof": {
        "name": "Дах",
        "description": (
            "Дах твого будинку. Довкола пливуть повітряні квартали, а над "
            "ними — небо, всипане зорями так густо, що аж світло."
        ),
        "exits": ("home",),
        "sky_quality": 0.8,
    },
    "plaza": {
        "name": "Площа Світанку",
        "description": (
            "Серце міста. Над головою повітряні квартали, між ними літають "
            "ракети. Тут усі зустрічаються, тож тут народжуються чутки."
        ),
        "exits": ("cafe", "home", "center"),
        "sky_quality": 0.5,
    },
    "cafe": {
        "name": "Кафе «Альмукантарат»",
        "description": (
            "Маленьке кафе на терасі над хмарами. Пахне корицею, а на стелі "
            "мерехтить жива карта сузір'їв."
        ),
        "exits": ("plaza",),
        "sky_quality": 0.2,
    },
    "center": {
        "name": "Дослідницький центр",
        "description": (
            "Величезна скляна споруда, що світиться зсередини. В центрі головної зали "
            "стоїть гігантський механічний орерій: золоте сонце і планети на орбітах. "
            "Світло падає зверху крізь вікна, а на підлозі стоять кілька людей у довгих мантіях.\n"
        ),
        "exits": ("plaza", "observatory", "library"),
        "sky_quality": 0.1,
    },
    "observatory": {
        "name": "Обсерваторія",
        "description": (
            "Купол відчиняється з тихим гудінням. Головний телескоп центру "
            "бачить галактики, яких не видно жодним іншим приладом у місті."
        ),
        "exits": ("center",),
        "sky_quality": 1.0,
    },
    "library": {
        "name": "Бібліотека",
        "description": (
            "Нескінченні полиці до самого куполу: паперові атласи трьохсотрічної "
            "давнини поруч із цифровими каталогами мільярдів зір."
        ),
        "exits": ("center",),
        "sky_quality": 0.3,
    },
}


NPCS = {
    "Корвус": {
        "place": "plaza",
        "role": "доглядач площі",
        "lines": [
            "Раночку, ad astra. На площі можна почути набагато більше, ніж у новинах.",
            "Пам'ятаю часи, коли будинки ще стояли на землі.",
            "Найкращі зорі — ті, на які дивишся не сам.",
            "Поклич колись друзів на дах. Старому буде приємно.",
        ],
    },
    "Міра": {
        "place": "cafe",
        "role": "бариста",
        "lines": [
            "Привіт! Каву та чай тут варять на воді з самих хмар — я тобі реально кажу.",
            "Знову ти! Тобі як завжди — з корицею?",
            "Я з вікна рахую падаючі зорі. Учора було шість чи сім? Вже сама не знаю.",
            "Покличеш на дах дивитися зорі — я принесу обліпиховий чай.",
        ],
    },
    "Тео": {
        "place": "cafe",
        "role": "інженер марсоходу",
        "lines": [
            "Приві, я Тео, інженер марсоходу. Вибач, трішки задивився на небо.",
            "Найкращий вид — з лабораторії о третій ночі.",
            "Іноді вимикаю ноут, щоб побачити Чумацький Шлях.",
            "Будеш дивитися на зорі — кажи. Прилечу:).",
        ],
    },
    "Драко": {
        "place": "center",
        "role": "колега-астрофізик",
        "lines": [
            "Привіт, я Драко. Якщо знайдеш щось цікаве, то неси графіки.",
            "Головне, спершу перевір, чи не наша техніка в кадрі.",
            "З тобою класно працювати, бо ти приносиш не висновки, а питання.",
            "Давай колись просто подивимось на зорі. Без тих всіх графіків.",
        ],
    },
    "Оріон": {
        "place": "center",
        "role": "керівник дослідницького центру",
        "lines": [
            "Доктор Оріон, керівник центру. Звіти приймаю лише з даними — здогадки залиш собі.",
            "Тобі потрібно зробити три заміри, думка колеги, перевірка каталогів. Лише тоді "
            "можна робити висновок. Не інакше.",
            "Бачив твої нотатки в журналі. Акуратно. Рідко таке кажу.",
            "Колись і я починав з даху й невеликого телескопа. Не забувай, "
            "навіщо ми дивимось угору.",
        ],
    },
    "Ара": {
        "place": "library",
        "role": "бібліотекарка",
        "lines": [
            "Ш-ш-ш... Вітаю. Тут є кожен каталог неба від XVII століття.",
            "Каталоги не брешуть, але й не все кажуть. Порівнюй уважно.",
            "Класифікуючи, дивись не лише на яскравість. Зсув каже, як далеко.",
            "Знаєш, я ніколи не бачила зорі з даху. Тільки в книжках.",
        ],
    },
}


# чутки які мали б натякнути на те що є якась аномалія і вона реальна
RUMORS = [
    ("Кажуть, у сузір'ї Ліри третю ніч щось дивно мерехтить.", True),
    (
        "Над північним кварталом повісили житловий модуль «Лелека-3». "
        "Уночі блищить, як зоря.",
        True,
    ),
    ("Міра пече новий десерт — «Зірочка палай». Кажуть, він світиться.", False),
    ("Доктор Оріон терпіти не може висновків без перевірки.", False),
    ("Драко шукає, з ким обговорити свої графіки.", False),
]


ANOMALIES_CLASSES = (
    (
        "Пульсуюча змінна зоря",
        "Ритмічно пульсує, зміни помірні.",
        (0.2, 0.9),
        (0.0, 0.01),
    ),
    (
        "Гравітаційне мікролінзування",
        "Світло підсилене гравітацією ближчого тіла.",
        (1.0, 2.2),
        (0.0, 0.01),
    ),
    (
        "Приливне руйнування зорі",
        "Чорна діра розриває зорю і відбувається потужний спалах.",
        (2.5, 4.0),
        (0.05, 0.3),
    ),
    ("Блазар", "Активне ядро дуже далекої галактики.", (0.4, 1.5), (0.8, 3.0)),
)

# ending: key -> (title, text, is_victory)
ENDINGS = {
    "discovery": (
        "Відкриття століття",
        "Доктор Оріон довго мовчить над твоїм звітом, а потім усміхається. "
        "Дані, каталоги, любі друзі, дорога родино — усе сходиться, і класифікація бездоганна. "
        "Про відкриття говорить уся площа, а Міра навіть назве десерт на твою честь.",
        True,
    ),
    "misclassified": (
        "Чув дзвін, та не знаєш, де він",
        "Аномалія таки справжня — ти був правий. Але за місяць інша обсерваторія "
        "доводить, що об'єкт належить до іншого класу. Драко каже: «Знайти — "
        "половина справи. Зрозуміти — друга половина».",
        False,
    ),
    "honest": (
        "Чесна доповідь",
        "Ти доповідаєш: це не аномалія, а відблиск модуля «Лелека-3». Оріон "
        "киває: «Нарешті хтось, хто щось перевіряє, а не просто вірить». Відкриття не "
        "сталося, але тобі доручають нову програму спостережень.",
        True,
    ),
    "fitting": (
        "Підганяння під задачу",
        "Ти впевнено називаєш об'єкт аномалією. Оріон відкриває каталог — і там "
        "житловий модуль «Лелека-3». «Ти не досліджуєш небо. Ти підганяєш "
        "дані під задачу», — каже він. Проєкт закривають.",
        False,
    ),
    "missed": (
        "Пропущене відкриття",
        "Ти вирішуєш, що це артефакт. Через два тижні інша група публікує "
        "статтю про нову аномалію в тих самих координатах. Іноді найбільша "
        "помилка — не повірити власним даним.",
        False,
    ),
    "rushed": (
        "Поспішний висновок",
        "Ти приходиш до Оріона, не завершивши перевірок. «Де заміри? Де "
        "каталоги? Де думка колег? Висновок без доказів — це підганяння». "
        "Аномалію передають іншій команді.",
        False,
    ),
    "chill": (
        "Тихий вечір",
        "Того вечора на твоєму даху вперше тісно. Хтось приносить какао, "
        "хтось ковдри. Квартали гасять вогні, і над вами розгортається "
        "Чумацький Шлях. Великого відкриття не сталося — зате ти знаходиш "
        "людей, з якими хочеться дивитися вгору.",
        True,
    ),
    "ordinary": (
        "Звичайне життя під зорями",
        "Сезон закінчується без сенсацій. Але на площі тобі махають знайомі, "
        "Міра пам'ятає твою каву, а вечори на даху стали традицією.",
        True,
    ),
    "burnout": (
        "Вигорання",
        "Енергія скінчилася, і ти засинаєш просто біля телескопа. "
        "Лікар призначає два тижні спокою без екранів і неба. Наступного "
        "разу частіше пий чай.",
        False,
    ),
    "season": (
        "Сезон минув",
        "Сезон позаду. Звіт порожній, а людей, з якими можна розділити небо, "
        "так і не з'явилося. Зорі ті самі, але цей сезон — уже ні.",
        False,
    ),
}


def new_game():
    """Game initialisation"""
    settings = SETTINGS.copy()
    npcs = NPCS.copy()
    bonds = {}
    for name in npcs:
        bonds[name] = 0
    rumors = RUMORS[:]
    random.shuffle(rumors)
    return {
        "cfg": settings,
        "world": WORLD,
        "npcs": NPCS,
        "classes": ANOMALIES_CLASSES,
        "endings": ENDINGS,
        "season": range(1, settings["max_days"] + 1),
        "day": 1,
        "actions_left": settings["actions_per_day"],
        "location": "home",
        "energy": settings["max_energy"],
        "mood": 5.0,
        "inventory": ["ключ-картка", "нотатник"],
        "journal": [],
        "visited": {"home"},
        "met": set(),
        "bonds": bonds,
        "rumors": rumors,
        "sky_hint": 0,
        "survey_tries": 0,
        "coffees_today": 0,
        "atlas_read": False,
        "anomaly": None,
        "measurements": {},
        "colleague_consulted": False,
        "catalog_checked": False,
        "verdict": None,
        "chosen_class": None,
        "ending": None,
        "quit": False,
    }


# ----- Inp and Out


def say(text: str) -> None:
    """Prints formatted text"""
    paragraphs = text.split("\n")

    for paragraph in paragraphs:
        print(textwrap.fill(paragraph, 70))


def read_input(state: dict) -> str | None:
    """Reads line. Returns None, if the player wants to quit"""
    try:
        raw = input(">>> ")
    except (EOFError, KeyboardInterrupt):
        print()
        return None

    text = raw.strip().lower()

    if text == state["cfg"]["quit_word"]:
        return None

    return text


def ask_choice(state: dict, options: list) -> int | None:
    """Shows the menu and returns ind of the choice or None when quitting"""
    for i, val in enumerate(options):
        print(f"  {i + 1}. {val}")

    valid = range(1, len(options) + 1)

    while True:
        print(
            f"Введи номер від 1 до {len(options)} "
            "(i — інвентар, j — журнал, g — словничок, ? — довідка, q — вийти):"
        )

        text = read_input(state)

        if text is None:
            state["quit"] = True
            return None

        command = state["cfg"]["commands"].get(text)

        if command is not None:
            run_command(state, command)
            continue

        try:
            number = int(text)
        except ValueError:
            print(f"Не розумію {text}. Потрібен номер пункту")
            continue

        if number in valid:
            return number - 1

        print("Такого пункту немає")


def run_command(state: dict, command: str) -> None:
    """Executes a system command (inventory, status, journal, help, glossary)"""
    if command == "inventory":
        if state["inventory"]:
            print("Інвентар: " + ", ".join(state["inventory"]))
        else:
            print("Інвентар порожній.")

    elif command == "status":
        show_status(state)

    elif command == "journal":
        print("Журнал:")

        if not state["journal"]:
            print("  поки порожньо")

        for entry in state["journal"][-8:]:
            say("  • " + entry)

    elif command == "help":
        show_help(state)
    elif command == "glossary":
        print("Словничок:")

        for word, meaning in GLOSSARY.items():
            say(f"  • {word} — {meaning}")


def show_help(state: dict) -> None:
    """Explains the game rules and goals"""
    cfg = state["cfg"]

    say(
        f"ЧАС: сезон відкриттів триває {cfg['max_days']} дні. Щодня в тебе "
        f"{cfg['actions_per_day']} дій. Переходи між локаціями дій не забирають. "
        "Коли дії закінчуються, ти йдеш спати і прокидаєшся вдома.\n\n"
        f"ЕНЕРГІЯ (0–{cfg['max_energy']}): наукова робота її витрачає (бо це не "
        "так просто як ти міг собі думати), кава і чай — повертають, сон відновлює "
        "повністю. Скільки коштує дія, написано в дужках біля неї. Якщо енергія дійде "
        "до 0 — це вигорання і кінець гри, тому не допусти цього!\n\n"
        "НАСТРІЙ (0–10): спілкування з людьми, чай і десерт підвищують настрій, "
        "а вигорання і надмірна кава його знижують. Тримай свій настрій на позитиві, "
        "і все буде добре.\n\n"
        "ІДЕЯ ГРИ: в тебе є два шляхи. Вибирай який тобі ближчий до душі)\n\n"
        "\033[1m ЯК ГРАТИ!!! ШЛЯХИ\033[0m\n" # to make this bold
        "ШЛЯХ ДОСЛІДНИКА: знайди аномалію в обсерваторії → зроби 3 заміри → "
        "поговори з Драко у центрі → перевір каталоги в бібліотеці → "
        "доповідай доктору Оріону у центрі.\n\n"
        "ЧІЛАУТ ШЛЯХ: спілкуйся з людьми, частуй їх, тримай гарний настрій — "
        "і поклич друзів на дах."
    )


def show_status(state: dict) -> None:
    """Shows the current day, actions left, energy and mood"""
    cfg = state["cfg"]

    state_bar = "■" * state["energy"] + "□" * (cfg["max_energy"] - state["energy"])
    print(
        f"День {state['day']}/{cfg['max_days']}  |  Дій сьогодні: "
        f"{state['actions_left']}/{cfg['actions_per_day']}"
    )
    print(
        f"Енергія {state_bar} {state['energy']}/{cfg['max_energy']}  |  "
        f"Настрій {state['mood']:.1f}/10"
    )


def add_journal(state: dict, text: str) -> None:
    """Just adds a line to the journal"""
    state["journal"].append(f"День {state['day']}: {text}")


def change_mood(state: dict, delta: float) -> None:
    """Changes mood by delta (keeps it in [0, 10])"""
    state["mood"] = max(0.0, min(10.0, state["mood"] + delta))


# ------ Time and energy


def spend(state: dict, energy: int) -> None:
    """Spends one action and some energy. If energy is 0 or less, the game ends"""
    state["energy"] = min(state["cfg"]["max_energy"], state["energy"] + energy)

    if state["energy"] <= 0:
        state["ending"] = "burnout"
        return

    state["actions_left"] -= 1

    if state["actions_left"] <= 0:
        say("\nУже пізно. Ти повертаєшся додому й одразу засинаєш.")
        end_day(state)


def end_day(state):
    """Ends the day, restores energy and actions, checks for season end"""
    cfg = state["cfg"]
    state["day"] += 1

    if state["day"] not in state["season"]:
        if total_bonds(state) >= 6:
            state["ending"] = "ordinary"
        else:
            state["ending"] = "season"
        return

    state["actions_left"] = cfg["actions_per_day"]
    state["energy"] = cfg["max_energy"]
    state["coffees_today"] = 0
    state["location"] = "home"

    say(
        f"\n☀ День {state['day']} з {cfg['max_days']}. Ти прокидаєшся вдома, "
        "енергію відновлено."
    )


def tired_ok(state: dict, cost: int) -> bool:
    """
    Tells the player that they may be too tired to do the action.
    Returns True if they can proceed
    """
    if state["energy"] - cost > 0:
        return True
    say(
        f"⚠ У тебе {state['energy']} енергії, а дія коштує {cost}. "
        "Це вигорання і кінець гри!"
    )
    return ask_choice(state, ("Все одно зробити", "Ні, спершу відпочину")) == 0


def total_bonds(state: dict) -> int:
    """Returns the sum of all friendship levels"""
    return sum(state["bonds"].values())


def close_friends(state: dict) -> set:
    """Returns the set of NPCs with friendship level 2 or higher (close)"""
    friends = set()
    for name in state["bonds"]:
        if state["bonds"][name] >= 2:
            friends.add(name)
    return friends


def chill_ready(state: dict) -> bool:
    """Returns True if the player can invite friends to the roof"""
    return (
        total_bonds(state) >= 8
        and state["mood"] >= 7.5
        and len(close_friends(state)) >= 3
    )


# ----- Actions


def move(state: dict, dest: str) -> None:
    """Teleportation between the locations (doesn't cost energy or action)"""
    world = state["world"]

    if dest == "observatory" and "ключ-картка" not in state["inventory"]:
        say("Двері не відчиняються без ключ-картки.")
        return

    state["location"] = dest

    if dest in state["visited"]:
        say(f"Ти тут: {world[dest]['name']}.")
    else:
        state["visited"].add(dest)
        say(world[dest]["description"])


def listen_rumors(state: dict) -> None:
    """Listens to rumors on the plaza. If there are no rumors, says so"""
    if not state["rumors"]:
        say("Сьогодні на площі говорять лише про погоду, нецікаві вони люди :(")
    else:
        text, is_hint = state["rumors"].pop()
        say("Чутка: " + text)
        if is_hint:
            state["sky_hint"] += 1
            add_journal(state, "Чутка: " + text)
    change_mood(state, 0.3)
    spend(state, 0)


def talk(state: dict, name: str) -> None:
    """Talks to an NPC, increases friendship level, may give a hint about the anomaly"""
    npc = state["npcs"][name]
    bond = state["bonds"][name]
    line = npc["lines"][min(bond, len(npc["lines"]) - 1)]

    if name == "Драко" and "астрометрія" in state["measurements"]:
        motion = state["measurements"]["астрометрія"]

        if motion > 1.0:
            line = (
                f"Зсув {motion:.2f}″ за годину? Для далекого об'єкта забагато. "
                "Схоже на щось близьке — супутник чи модуль."
            )
        else:
            line = (
                f"Зсув {motion:.3f}″ за годину — в межах похибки. "
                "Об'єкт далекий, це не наш сусід по орбіті."
            )

        if not state["colleague_consulted"]:
            state["colleague_consulted"] = True
            add_journal(state, "Драко: " + line)

    if name == "Оріон" and state["anomaly"] is not None and state["verdict"] is None:
        missing = state["cfg"]["required"] - set(state["measurements"])
        if not missing and state["colleague_consulted"] and state["catalog_checked"]:
            line = "Бачу, всі перевірки зроблено. Доповідай — я слухаю."

    say(f"{name}: «{line}»")

    state["met"].add(name)
    state["bonds"][name] = min(state["cfg"]["max_bond"], bond + 1)
    change_mood(state, 0.5)

    gift = "тістечко «Зірочка палай»"
    if gift in state["inventory"]:
        say(f"У тебе є {gift}. Пригостити?")
        answer = ask_choice(state, ("Так, пригостити", "Ні, залишити собі"))

        if answer is None:
            return

        if answer == 0:
            state["inventory"].remove(gift)
            state["bonds"][name] = min(
                state["cfg"]["max_bond"], state["bonds"][name] + 1
            )
            say(f"{name} усміхається: «Ти знаєш, як зробити день кращим!»")
    spend(state, 0)


def drink_coffee(state: dict) -> None:
    """Drinks coffee, increases energy and mood, but too much coffee decreases mood"""
    state["coffees_today"] += 1

    if state["coffees_today"] > 2:
        say("Третя кава за день... Серце калатає, настрій псується.")
        change_mood(state, -1.0)

    else:
        say("Міра ставить перед тобою каву з корицею. Сили повертаються.")

    spend(state, 3)


def eat_dessert(state):
    """Eat dessert, increases mood and gives a gift if not already in inventory"""
    say("Десерт «Зірочка палай» справді ледь світиться. Смакує як дитинство.")

    change_mood(state, 1.2)
    gift = "тістечко «Зірочка палай»"

    if gift not in state["inventory"]:
        state["inventory"].append(gift)
        say(
            "Міра загортає ще одне тістечко тобі з собою, може захочеш когось пригостити)"
        )

    spend(state, 1)


def brew_tea(state):
    """Brew tea, increases mood and takes some time"""
    say("Чайник тихо свистить. Ти грієш руки об чашку й дивишся на хмари.")

    change_mood(state, 0.6)
    spend(state, 2)


def watch_stars(state):
    """
    Watching stars on the roof, increases mood depending on sky quality,
    may give a hint about the anomaly
    """
    scenes = [
        "Квартали гасять вогні один за одним, і небо розкривається, як книга.",
        "Над північним кварталом пропливає щось світле, а за ним — Чумацький Шлях.",
        "Падаюча зірочка. Ти не встигаєш загадати бажання, але усміхаєшся.",
    ]

    say(random.choice(scenes))
    change_mood(state, 1.5 * state["world"]["roof"]["sky_quality"])

    if state["anomaly"] is None and random.random() < 0.5:
        state["sky_hint"] += 1

        say(
            "У сузір'ї Ліри щось ледь помітно мерехтить. Варто глянути в "
            "телескоп обсерваторії."
        )

        add_journal(state, "З даху помічено мерехтіння в Лірі.")

    if chill_ready(state):
        say("Тобі спадає на думку: а що, як покликати сюди друзів? ")

    spend(state, 0)


def sleep(state):
    """Sleeping and the day ends"""
    say("Ти загортаєшся в ковдру. За вікном пропливає повітряний квартал...")
    end_day(state)


def create_anomaly(classes: tuple) -> dict:
    """Creates an anomaly: real (65%) or an artificial one"""
    is_real = random.random() < 0.65

    coords = (
        round(random.uniform(18.0, 19.5), 2),
        round(random.uniform(25.0, 45.0), 2),
    )

    class_index = None
    values = {}

    if is_real:
        class_index = random.randrange(len(classes))

        amp_low, amp_high = classes[class_index][2]
        z_low, z_high = classes[class_index][3]
        amp_margin = (amp_high - amp_low) * 0.1
        z_margin = (z_high - z_low) * 0.1

        values["фотометрія"] = random.uniform(
            amp_low + amp_margin, amp_high - amp_margin
        )
        values["спектроскопія"] = random.uniform(z_low + z_margin, z_high - z_margin)
        values["астрометрія"] = random.uniform(0.005, 0.05)
    else:
        values["фотометрія"] = random.uniform(0.3, 3.0)
        values["спектроскопія"] = random.uniform(0.0005, 0.004)
        values["астрометрія"] = random.uniform(12.0, 40.0)

    return {
        "real": is_real,
        "coords": coords,
        "class_index": class_index,
        "true": values,
    }


def survey(state: dict) -> None:
    """Does a survey in the observatory. May find an anomaly or not"""
    if not tired_ok(state, 2):
        return

    state["survey_tries"] += 1
    chance = 0.5 + 0.2 * state["sky_hint"] + 0.5 * (state["survey_tries"] - 1)

    if random.random() < chance:
        state["anomaly"] = create_anomaly(state["classes"])
        ra, dec = state["anomaly"]["coords"]

        say(
            f"Є! У координатах RA {ra}h, Dec +{dec}° щось поводиться дивно. "
            "Тепер зроби три заміри: фотометрію, спектроскопію й астрометрію."
        )

        add_journal(state, f"Знайдено можливу аномалію: RA {ra}h, Dec +{dec}°.")
    else:
        say(
            "Нічого незвичного. Спробуй ще раз або пошукай підказки "
            "в чутках на площі чи з даху."
        )

    spend(state, -2)


def measure(state: dict, kind: str) -> None:
    """Does a measurement of the given kind (photometry, spectroscopy, astrometry)"""
    if not tired_ok(state, 2):
        return

    value = state["anomaly"]["true"][kind] * random.uniform(0.98, 1.02)
    state["measurements"][kind] = value
    text = state["cfg"]["measure_text"][kind].format(value)

    say(text)

    add_journal(state, text)
    missing = state["cfg"]["required"] - set(state["measurements"])

    if missing:
        say("Ще бракує: " + ", ".join(sorted(missing)) + ".")
    else:
        say(
            "Усі заміри готові! Далі: обговори їх з Драко у центрі й "
            "перевір каталоги в бібліотеці."
        )

    spend(state, -2)


def read_atlas(state: dict) -> None:
    """Reads the atlas, gives a hint about the anomaly and a star chart"""
    say("Ти гортаєш старовинний атлас, де сузір'я намальовані у вигляді звірів.")
    change_mood(state, 1.0)

    if not state["atlas_read"]:
        state["atlas_read"] = True
        state["inventory"].append("зоряна карта")
        state["sky_hint"] += 1
        say(
            "Між сторінками стара зоряна карта з обведеним сузір'ям Ліри. "
            "Ара тобі її дає з собою (можливо вона тобі пригодиться)."
        )

    spend(state, 0)


def check_catalog(state: dict) -> None:
    """Checks the catalog for the anomaly. If all measurements are done, gives a verdict"""
    missing = state["cfg"]["required"] - set(state["measurements"])

    if missing:
        say(
            "Ара: «Каталог шукає за повним набором даних. Бракує: "
            + ", ".join(sorted(missing))
            + "»."
        )
        return

    if not tired_ok(state, 1):
        return

    if state["anomaly"]["real"]:
        result = "Збігів не знайдено в жодному каталозі. Це щось нове."
    else:
        result = (
            "Збіг: житловий модуль «Лелека-3» на орбіті над північним "
            "кварталом. Час проходу збігається з твоїми спостереженнями."
        )
    say("Ти запускаєш пошук у мільярдах записів...\n" + result)
    say("Тепер можна йти з доповіддю до доктора Оріона у Дослідницький центр.")

    state["catalog_checked"] = True
    add_journal(state, "Каталоги: " + result)
    spend(state, -1)


def report(state: dict) -> None:
    """Gives a report to Orion. If all checks are done, he asks for a verdict"""
    if state["verdict"] == "real":
        say("Оріон: «Аномалію визнано. Чекаю класифікацію, а тобі в бібліотеку».")
        return

    m = state["measurements"]

    checks = (
        ("Фотометрія", "фотометрія" in m),
        ("Спектроскопія", "спектроскопія" in m),
        ("Астрометрія", "астрометрія" in m),
        ("Розмова з Драко про астрометрію", state["colleague_consulted"]),
        ("Перевірка за каталогами в бібліотеці", state["catalog_checked"]),
    )

    ready = True
    print("Твої перевірки:")

    for label, done in checks:
        mark = " "
        if done:
            mark = "x"
        else:
            ready = False
        print(f"  [{mark}] {label}")

    say("Доктор Оріон дивиться поверх окулярів: «Слухаю. Що це за об'єкт?»")

    choice = ask_choice(
        state,
        (
            "Це справжня аномалія",
            "Це артефакт, а не аномалія",
            "Повернуся пізніше",
        ),
    )

    if choice is None or choice == 2:
        return

    said_real = choice == 0
    is_real = state["anomaly"]["real"]

    if not ready:
        state["ending"] = "rushed"
    elif said_real and is_real:
        state["verdict"] = "real"
        say("Оріон киває: «Дані переконливі. Тепер класифікуй об'єкт у бібліотеці».")
        add_journal(state, "Аномалію визнано. Лишилась класифікація в бібліотеці.")
        spend(state, 0)
    elif said_real:
        state["ending"] = "fitting"
    elif not is_real:
        state["ending"] = "honest"
    else:
        state["ending"] = "missed"


def classify(state: dict) -> None:
    """Classifies the anomaly. If the choice is correct, it's a discovery yaaaaay"""
    m = state["measurements"]
    classes = state["classes"]

    say(
        f"Твої дані: амплітуда {m['фотометрія']:.2f} зор. вел., "
        f"зсув z = {m['спектроскопія']:.3f}.\nДовідник класів:"
    )

    for name, desc, amp, z in classes:
        say(f"  {name}: амплітуда {amp[0]}–{amp[1]}, z {z[0]}–{z[1]}. {desc}")

    if state["bonds"]["Ара"] >= 2:
        say("Ара шепоче: «Дивись на обидва числа одразу».")

    say("До якого класу належить твій об'єкт?")
    labels = []

    for cls in classes:
        labels.append(cls[0])

    labels.append("Ще подумаю")
    idx = ask_choice(state, labels)

    if idx is None or idx == len(classes):
        return

    state["chosen_class"] = classes[idx][0]

    if idx == state["anomaly"]["class_index"]:
        state["ending"] = "discovery"
    else:
        state["ending"] = "misclassified"


def invite_friends(state):
    """
    Invites friends to the roof. If the player has enough bonds and mood,
    it's a happy ending yaaay
    """
    state["ending"] = "chill"


def do_action(state: dict, key: str, arg: str | None) -> None:
    """Does the action by its key"""
    if key == "move":
        move(state, arg)
    elif key == "talk":
        talk(state, arg)
    elif key == "measure":
        measure(state, arg)
    elif key == "rumors":
        listen_rumors(state)
    elif key == "coffee":
        drink_coffee(state)
    elif key == "dessert":
        eat_dessert(state)
    elif key == "tea":
        brew_tea(state)
    elif key == "sleep":
        sleep(state)
    elif key == "stars":
        watch_stars(state)
    elif key == "invite":
        invite_friends(state)
    elif key == "survey":
        survey(state)
    elif key == "atlas":
        read_atlas(state)
    elif key == "catalog":
        check_catalog(state)
    elif key == "report":
        report(state)
    elif key == "classify":
        classify(state)


def build_actions(state: dict) -> list:
    """List of actions in the current location (text, action key, argument)"""
    loc = state["location"]
    actions = []

    if loc == "home":
        actions.append(("Заварити чай  (1 дія, +2 енергії)", "tea", None))
        actions.append(("Лягти спати — завершити день", "sleep", None))

    elif loc == "roof":
        actions.append(("Дивитися на зорі  (1 дія)", "stars", None))
        if chill_ready(state):
            actions.append(("✦ Покликати друзів на дах (фінал)", "invite", None))

    elif loc == "plaza":
        actions.append(("Послухати чутки  (1 дія)", "rumors", None))

    elif loc == "cafe":
        actions.append(("Випити каву  (1 дія, +3 енергії)", "coffee", None))
        actions.append(
            (
                "З'їсти смачненький зоряний десертик  (1 дія, +1 енергії)",
                "dessert",
                None,
            )
        )

    elif loc == "center":
        if state["anomaly"] is not None:
            actions.append(("Доповісти доктору Оріону", "report", None))

    elif loc == "observatory":
        if state["anomaly"] is None:
            actions.append(
                ("Шукати аномалії в небі  (1 дія, -2 енергії)", "survey", None)
            )
        else:
            for kind in state["cfg"]["measure_order"]:
                note = ""

                if kind in state["measurements"]:
                    note = " — вже є, повторити"

                actions.append(
                    (f"Заміряти: {kind}{note}  (1 дія, -2 енергії)", "measure", kind)
                )
    elif loc == "library":
        actions.append(("Гортати старовинні атласи  (1 дія)", "atlas", None))

        if state["anomaly"] is not None:
            actions.append(
                (
                    "Перевірити об'єкт за каталогами  (1 дія, -1 енергії)",
                    "catalog",
                    None,
                )
            )

        if state["verdict"] == "real":
            actions.append(("Класифікувати аномалію (фінал)", "classify", None))

    for name in state["npcs"]:
        npc = state["npcs"][name]

        if npc["place"] == loc:
            actions.append(
                (f"Поговорити: {name}, {npc['role']}  (1 дія)", "talk", name)
            )

    for dest in state["world"][loc]["exits"]:
        actions.append((f"Піти → {state['world'][dest]['name']}", "move", dest))

    return actions


# ------- Finally the game


def intro(state: dict) -> None:
    """Intro to the game"""
    print("\n" + "═" * 70)
    print("✦  AD ASTRA  ✦".center(70))
    print("═" * 70)

    say(
        "Далеке майбутнє. Міста висять у повітрі, а зорі видно навіть удень. "
        "Ти — астроном, і попереду сезон спостережень.\n"
        "Можна розгадати таємницю галактики. А можна просто чілити: пити каву, "
        "слухати чутки й дивитися на зорі з даху (все як люблять справжні астрономи:).\n"
    )

    show_help(state)
    print()
    say("Ти прокидаєшся вдома. " + state["world"]["home"]["description"])


def game_loop(state: dict) -> None:
    """Main game loop"""
    while state["ending"] is None and not state["quit"]:
        print("\n" + "─" * 70)
        print(f"✦ {state['world'][state['location']]['name']}")

        show_status(state)

        if state["energy"] <= 2:
            print("⚠ Енергії мало! Випий кави в кафе або чаю вдома.")

        print("Що робиш далі?")
        actions = build_actions(state)
        labels = []

        for action in actions:
            labels.append(action[0])

        idx = ask_choice(state, labels)

        if idx is None:
            return

        print()
        _, key, arg = actions[idx]
        do_action(state, key, arg)

        if state["ending"] is None and state["mood"] <= 0.0:
            state["ending"] = "burnout"


def show_ending(state: dict) -> None:
    """The ending of the game"""
    title, text, is_win = state["endings"][state["ending"]]

    print("\n" + "═" * 70)
    print(f"КІНЕЦЬ: {title}".center(70))
    print("═" * 70)

    say(text)

    if state["ending"] == "discovery" or state["ending"] == "misclassified":
        true_name = state["classes"][state["anomaly"]["class_index"]][0]
        say(f"\nТвій вибір: {state['chosen_class']}. Справжній клас: {true_name}.")

    if state["ending"] == "chill":
        say("\nПоруч із тобою: " + ", ".join(sorted(close_friends(state))) + ".")

    print()

    if is_win:
        print("Результат: ПЕРЕМОГА (yaaaay) ✦")
    else:
        print("Результат: ПОРАЗКА (well...skill issue)")

    print(
        f"Знайомих: {len(state['met'])}  |  Записів у журналі: {len(state['journal'])}"
    )


def main():
    """Main function"""
    playing = True

    while playing:
        state = new_game()
        intro(state)
        game_loop(state)

        if state["quit"]:
            break

        show_ending(state)
        print("\nЗіграти ще раз?")
        answer = ask_choice(state, ("Так", "Ні"))
        playing = answer == 0

    print("\nДо зустрічі під зорями! ✦")


main()

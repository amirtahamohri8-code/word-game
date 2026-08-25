import os
import random
import math
import json

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.graphics import Color, RoundedRectangle, Ellipse

import arabic_reshaper
from bidi.algorithm import get_display

Window.clearcolor = (0.015, 0.01, 0.035, 1)

# =========================================================
# تنظیمات
# =========================================================

MAX_LEVEL = 1000

WIN_REWARD = 53
HINT_COST = 40

SAVE_FILE = "player.dat"

DEFAULT_DATA = {
    "level": 1,
    "coins": 500,
    "sound": True,
    "music": True,
    "animations": True,
    "quality": "auto",
    "vibration": True
}


# =========================================================
# مسیر فونت (نسبی به پوشه برنامه)
# =========================================================

FONT_PATH = os.path.join(os.path.dirname(__file__), "mopi.ttf")

if not os.path.exists(FONT_PATH):
    FONT_PATH = None


# =========================================================
# اصلاح متون فارسی برای نمایش در Kivy
# =========================================================

def reshape_text(text):
    if not text:
        return ""
    reshaped_text = arabic_reshaper.reshape(str(text))
    return get_display(reshaped_text)


# =========================================================
# نرمال‌سازی فارسی
# =========================================================

def normalize_farsi(text):

    table = {
        "ي": "ی",
        "ى": "ی",
        "ك": "ک",
        "ۀ": "ه",
        "ة": "ه",
        "ؤ": "و",
        "إ": "ا",
        "أ": "ا",
        "ٱ": "ا",
        "\u200c": "",
        "\u200d": "",
        "َ": "",
        "ِ": "",
        "ُ": "",
        "ّ": "",
        "ْ": "",
        "ً": "",
        "ٌ": "",
        "ٍ": ""
    }

    text = str(text)

    for old, new in table.items():
        text = text.replace(old, new)

    return text.strip()


# =========================================================
# ذخیره ساده
# =========================================================

def save_data(data):

    try:

        with open(
            SAVE_FILE,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                ensure_ascii=False
            )

    except Exception:
        pass


def load_data():

    if not os.path.exists(SAVE_FILE):
        return DEFAULT_DATA.copy()

    try:

        with open(
            SAVE_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        result = DEFAULT_DATA.copy()

        for key in result:

            if key in data:
                result[key] = data[key]

        result["level"] = max(
            1,
            min(
                MAX_LEVEL,
                int(result["level"])
            )
        )

        result["coins"] = max(
            0,
            int(result["coins"])
        )

        return result

    except Exception:

        return DEFAULT_DATA.copy()


# =========================================================
# بانک مرحله‌ها
# =========================================================

LEVELS = [

    {
        "letters": ["س", "ر", "ا", "د"],
        "words": ["در", "دار", "درس", "سرد"]
    },

    {
        "letters": ["ک", "ت", "ا", "ب"],
        "words": ["کتاب", "تاب", "تاک", "بت"]
    },

    {
        "letters": ["م", "ا", "د", "ر"],
        "words": ["مادر", "در", "مار", "دار"]
    },

    {
        "letters": ["خ", "و", "ر", "ش"],
        "words": ["خور", "روش", "خروش"]
    },

    {
        "letters": ["ب", "ا", "ر", "ا"],
        "words": ["بار", "آرا"]
    },

    {
        "letters": ["گ", "ل", "ا", "ب"],
        "words": ["گل", "بال", "باغ"]
    },

    {
        "letters": ["د", "و", "س", "ت"],
        "words": ["دو", "دوست", "دست"]
    },

    {
        "letters": ["ش", "ه", "ر"],
        "words": ["شهر", "هر", "ره"]
    },

    {
        "letters": ["ز", "م", "ی", "ن"],
        "words": ["زمین", "مین", "نی"]
    },

    {
        "letters": ["ک", "و", "ه"],
        "words": ["کوه", "که", "کو"]
    }

]


def generate_level(number):

    index = (number - 1) % len(LEVELS)

    base = LEVELS[index]

    rng = random.Random(
        2026 + number * 7919
    )

    letters = list(
        base["letters"]
    )

    words = list(
        base["words"]
    )

    rng.shuffle(letters)
    rng.shuffle(words)

    return {
        "letters": letters,
        "words": [
            normalize_farsi(w)
            for w in words
        ]
    }


# =========================================================
# بک‌گراند
# =========================================================

class Background(Widget):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.t = 0

        with self.canvas:

            Color(
                0.015,
                0.01,
                0.035,
                1
            )

            self.bg = RoundedRectangle(
                pos=self.pos,
                size=self.size
            )

            Color(
                0.25,
                0.05,
                0.5,
                0.18
            )

            self.circle1 = Ellipse(
                size=(300, 300),
                pos=(10, 400)
            )

            Color(
                0.02,
                0.4,
                0.55,
                0.15
            )

            self.circle2 = Ellipse(
                size=(260, 260),
                pos=(300, 100)
            )

        self.bind(
            pos=self.update,
            size=self.update
        )

        Clock.schedule_interval(
            self.animate,
            1 / 60
        )

    def update(self, *args):

        self.bg.pos = self.pos
        self.bg.size = self.size

    def animate(self, dt):

        self.t += dt

        self.circle1.pos = (
            20 + math.sin(self.t) * 20,
            400 + math.cos(self.t) * 15
        )

        self.circle2.pos = (
            300 + math.cos(
                self.t * .7
            ) * 30,
            100 + math.sin(
                self.t * .7
            ) * 20
        )


# =========================================================
# دکمه
# =========================================================

class GameButton(Button):

    def __init__(self, **kwargs):

        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""

        self.background_color = (
            0.20,
            0.07,
            0.42,
            1
        )

        self.color = (
            1,
            1,
            1,
            1
        )

        self.font_size = "18sp"

        if FONT_PATH:
            self.font_name = FONT_PATH

        self.size_hint_y = None
        self.height = 58


# =========================================================
# خانه
# =========================================================

class HomeScreen(Screen):

    def on_pre_enter(self):

        self.clear_widgets()

        root = FloatLayout()

        root.add_widget(
            Background()
        )

        box = BoxLayout(
            orientation="vertical",
            padding=30,
            spacing=15
        )

        title = Label(
            text=reshape_text("کلمه‌ساز"),
            font_size="42sp",
            bold=True,
            size_hint_y=None,
            height=90
        )

        coins = Label(
            text="",
            font_size="20sp",
            size_hint_y=None,
            height=55
        )

        level = Label(
            text="",
            font_size="18sp",
            size_hint_y=None,
            height=45
        )

        play = GameButton(
            text=reshape_text("🎮 شروع بازی")
        )

        settings = GameButton(
            text=reshape_text("⚙️ تنظیمات")
        )

        if FONT_PATH:

            title.font_name = FONT_PATH
            coins.font_name = FONT_PATH
            level.font_name = FONT_PATH

        play.bind(
            on_release=lambda x:
            setattr(self.manager, 'current', 'game')
        )

        settings.bind(
            on_release=lambda x:
            setattr(self.manager, 'current', 'settings')
        )

        box.add_widget(title)
        box.add_widget(coins)
        box.add_widget(level)
        box.add_widget(play)
        box.add_widget(settings)

        root.add_widget(box)

        self.add_widget(root)

        self.coins_label = coins
        self.level_label = level

        self.refresh()

    def refresh(self):

        self.coins_label.text = reshape_text(
            f"🪙 {self.app.data['coins']} سکه"
        )

        self.level_label.text = reshape_text(
            f"مرحله {self.app.data['level']} "
            f"از {MAX_LEVEL}"
        )


# =========================================================
# بازی
# =========================================================

class GameScreen(Screen):

    def on_pre_enter(self):

        self.clear_widgets()

        self.current_word = ""
        self.found_words = set()

        root = FloatLayout()

        root.add_widget(
            Background()
        )

        main = BoxLayout(
            orientation="vertical",
            padding=15,
            spacing=10
        )

        top = BoxLayout(
            size_hint_y=None,
            height=55
        )

        self.level_label = Label(
            font_size="19sp"
        )

        self.coin_label = Label(
            font_size="18sp"
        )

        self.answer = Label(
            text="",
            font_size="30sp",
            bold=True,
            size_hint_y=None,
            height=80
        )

        self.status = Label(
            text="",
            font_size="17sp",
            size_hint_y=None,
            height=45
        )

        if FONT_PATH:

            self.level_label.font_name = FONT_PATH
            self.coin_label.font_name = FONT_PATH
            self.answer.font_name = FONT_PATH
            self.status.font_name = FONT_PATH

        top.add_widget(
            self.level_label
        )

        top.add_widget(
            self.coin_label
        )

        self.words_area = GridLayout(
            cols=2,
            spacing=8
        )

        self.letters_area = GridLayout(
            cols=4,
            spacing=8,
            size_hint_y=None,
            height=240
        )

        self.hint_button = GameButton(
            text=reshape_text("💡 راهنمایی — ۴۰ سکه")
        )

        self.clear_button = GameButton(
            text=reshape_text("⌫ پاک کردن")
        )

        self.back_button = GameButton(
            text=reshape_text("🏠 خروج")
        )

        self.hint_button.bind(
            on_release=self.hint
        )

        self.clear_button.bind(
            on_release=self.clear_word
        )

        self.back_button.bind(
            on_release=lambda x:
            setattr(self.manager, 'current', 'home')
        )

        main.add_widget(top)
        main.add_widget(self.answer)
        main.add_widget(self.status)
        main.add_widget(self.words_area)
        main.add_widget(self.letters_area)
        main.add_widget(self.hint_button)
        main.add_widget(self.clear_button)
        main.add_widget(self.back_button)

        root.add_widget(main)

        self.add_widget(root)

        self.load_level()

    def load_level(self):

        number = self.app.data["level"]

        self.level = generate_level(
            number
        )

        self.valid_words = set(
            self.level["words"]
        )

        self.found_words.clear()

        self.current_word = ""

        self.answer.text = ""
        self.status.text = ""

        self.level_label.text = reshape_text(
            f"مرحله {number}/{MAX_LEVEL}"
        )

        self.update_coins()

        self.letters_area.clear_widgets()

        for letter in self.level["letters"]:

            btn = GameButton(
                text=reshape_text(letter)
            )

            btn.bind(
                on_release=lambda b,
                x=letter:
                self.add_letter(x)
            )

            self.letters_area.add_widget(
                btn
            )

        self.refresh_words()

    def update_coins(self):

        self.coin_label.text = reshape_text(
            f"🪙 {self.app.data['coins']}"
        )

    def add_letter(self, letter):

        self.current_word += letter

        self.answer.text = reshape_text(
            self.current_word
        )

        self.check_current()

    def check_current(self):

        word = normalize_farsi(
            self.current_word
        )

        if not word:
            return

        if word in self.valid_words:

            if word in self.found_words:

                self.status.text = reshape_text(
                    "⚠️ این کلمه قبلاً پیدا شده"
                )

                return

            self.found_words.add(word)

            self.app.data["coins"] += WIN_REWARD

            save_data(
                self.app.data
            )

            self.status.text = reshape_text(
                f"✅ درست! +{WIN_REWARD} سکه"
            )

            self.current_word = ""
            self.answer.text = ""

            self.update_coins()
            self.refresh_words()

            if self.found_words == self.valid_words:

                Clock.schedule_once(
                    lambda dt:
                    self.finish_level(),
                    .8
                )

    def refresh_words(self):

        self.words_area.clear_widgets()

        for word in sorted(
            self.valid_words,
            key=lambda x: len(x)
        ):

            if word in self.found_words:
                text = "✓ " + word
            else:
                text = "• • •"

            label = Label(
                text=reshape_text(text),
                font_size="19sp"
            )

            if FONT_PATH:
                label.font_name = FONT_PATH

            self.words_area.add_widget(
                label
            )

    def clear_word(self, *args):

        self.current_word = ""
        self.answer.text = ""

    def hint(self, *args):

        if self.app.data["coins"] < HINT_COST:

            self.status.text = reshape_text(
                "❌ سکه کافی نیست"
            )

            return

        remaining = [
            w for w in self.valid_words
            if w not in self.found_words
        ]

        if not remaining:

            return

        self.app.data["coins"] -= HINT_COST

        save_data(
            self.app.data
        )

        answer = remaining[0]

        self.status.text = reshape_text(
            "💡 راهنمایی: "
            + answer[0]
            + "..."
        )

        self.update_coins()

    def finish_level(self):

        if self.app.data["level"] < MAX_LEVEL:

            self.app.data["level"] += 1

        save_data(
            self.app.data
        )

        self.status.text = reshape_text(
            "🏆 مرحله کامل شد!"
        )

        Clock.schedule_once(
            lambda dt:
            self.load_level(),
            1
        )


# =========================================================
# تنظیمات
# =========================================================

class SettingsScreen(Screen):

    def on_pre_enter(self):

        self.clear_widgets()

        root = FloatLayout()

        root.add_widget(
            Background()
        )

        box = BoxLayout(
            orientation="vertical",
            padding=25,
            spacing=15
        )

        title = Label(
            text=reshape_text("⚙️ تنظیمات"),
            font_size="32sp",
            bold=True,
            size_hint_y=None,
            height=80
        )

        if FONT_PATH:
            title.font_name = FONT_PATH

        animation = GameButton()
        sound = GameButton()
        vibration = GameButton()

        back = GameButton(
            text=reshape_text("↩️ برگشت")
        )

        def refresh():

            anim_status = "روشن" if self.app.data["animations"] else "خاموش"
            sound_status = "روشن" if self.app.data["sound"] else "خاموش"
            vib_status = "روشن" if self.app.data["vibration"] else "خاموش"

            animation.text = reshape_text(f"✨ انیمیشن: {anim_status}")
            sound.text = reshape_text(f"🔊 صدا: {sound_status}")
            vibration.text = reshape_text(f"📳 لرزش: {vib_status}")

        def toggle_animation(*args):

            self.app.data["animations"] = not self.app.data["animations"]

            save_data(
                self.app.data
            )

            refresh()

        def toggle_sound(*args):

            self.app.data["sound"] = not self.app.data["sound"]

            save_data(
                self.app.data
            )

            refresh()

        def toggle_vibration(*args):

            self.app.data["vibration"] = not self.app.data["vibration"]

            save_data(
                self.app.data
            )

            refresh()

        animation.bind(
            on_release=toggle_animation
        )

        sound.bind(
            on_release=toggle_sound
        )

        vibration.bind(
            on_release=toggle_vibration
        )

        back.bind(
            on_release=lambda x:
            setattr(self.manager, 'current', 'home')
        )

        box.add_widget(title)
        box.add_widget(animation)
        box.add_widget(sound)
        box.add_widget(vibration)
        box.add_widget(back)

        root.add_widget(box)

        self.add_widget(root)

        refresh()


# =========================================================
# برنامه
# =========================================================

class WordGameApp(App):

    def build(self):

        self.data = load_data()

        manager = ScreenManager(
            transition=FadeTransition(
                duration=.2
            )
        )

        home = HomeScreen(
            name="home"
        )

        game = GameScreen(
            name="game"
        )

        settings = SettingsScreen(
            name="settings"
        )

        manager.add_widget(home)
        manager.add_widget(game)
        manager.add_widget(settings)

        return manager


if __name__ == "__main__":

    WordGameApp().run()

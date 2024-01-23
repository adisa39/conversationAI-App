from kivy.config import Config
from kivy.lang import Builder

Config.set('graphics', 'width', '350')
Config.set('graphics', 'height', '550')

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.material_resources import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.snackbar import Snackbar


class ContentNavigationDrawer(MDBoxLayout):
    pass


class Test(MDApp):

    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Light"
        menu_list = ["Chat", "Logout"]

        menu_items = [
            {
                "viewclass": "OneLineListItem",
                "text": "Chat",
                "height": dp(46),
                "on_release": lambda x=f"Chat pressed": self.menu_callback(x)

            },
            {
                "viewclass": "OneLineListItem",
                "text": "Logout",
                "height": dp(46),
                "color": "red",
                "on_release": lambda x=f"Logout pressed": self.menu_callback(x)

            }
        ]

        self.menu = MDDropdownMenu(items=menu_items, width_mult=2, border_margin=dp(24))

        return Builder.load_file("design.kv")

    def callback(self, button):
        self.menu.caller = button
        self.menu.open()

    def menu_callback(self, text_item):
        self.menu.dismiss()
        Snackbar(text=text_item).open()


Test().run()

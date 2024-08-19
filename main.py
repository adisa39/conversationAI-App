import os
import shutil
import queue
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.filemanager import MDFileManager
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.button import MDFlatButton, MDIconButton

# Global Lists
selected_files = []
selected_sources = []

def get_or_create_dir(directory_name):
    """Function to create a directory if it doesn't exist."""
    dir_path = os.path.join(os.getcwd(), directory_name)
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    return dir_path

docs_dir = get_or_create_dir("docs")
db_dir = get_or_create_dir("db")

def notification(text):
    """Function to show a notification using MDSnackbar."""
    MDSnackbar(
        text=text,
        md_bg_color=(0.8, 0, 0, 1),
        duration=3
    ).open()

def update_selection(files, file_name, is_selected):
    """Function to add and remove files from the selected list."""
    if is_selected:
        if file_name not in files:
            files.append(file_name)
    else:
        try:
            files.remove(file_name)
        except ValueError:
            pass

class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior, RecycleBoxLayout):
    '''Adds selection and focus behavior to the view.'''

class SourceToggleView(RecycleDataViewBehavior, Label):
    '''Add selection support to the Label'''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    fn = StringProperty("")

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(SourceToggleView, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(SourceToggleView, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        file_name = rv.data[index]['fn']
        update_selection(selected_sources, file_name, is_selected)

class DocsLayout(RecycleDataViewBehavior, Label):
    '''Add selection support to the Label'''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)
    fn = StringProperty("")

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(DocsLayout, self).refresh_view_attrs(rv, index, data)

    def on_touch_down(self, touch):
        if super(DocsLayout, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        file_name = rv.data[index]['fn']
        update_selection(selected_files, file_name, is_selected)

class RV(RecycleView):
    """Document List View Page"""
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.refresh_data()

    def refresh_data(self):
        self.data = [{'fn': str(x)} for x in self.show_docs()]

    def show_docs(self):
        filenames = [i for i in os.listdir(docs_dir) if i.endswith(".pdf")]
        return filenames

class SourceToggleButton(MDFlatButton, MDIconButton, MDToggleButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.background_down = self.theme_cls.primary_color

class MessageLayout(MDBoxLayout):
    msg = StringProperty("")
    doc = StringProperty("")
    sent = BooleanProperty(False)

    def __init__(self, msg, doc, sent, **kwargs):
        super().__init__(**kwargs)
        self.msg = msg
        self.doc = doc
        self.sent = sent
        self.adaptive_height = True
        self.orientation = "vertical"
        self.padding_bottom = "5dp"

        text_body = MDLabel(
            text=self.msg,
            halign='right' if self.sent else 'left',
            theme_text_color="Custom",
            text_color=(0, 0.5, 1, 1) if self.sent else (0, 0, 0, 1),
            adaptive_height=True,
            markup=True
        )

        source_text = MDLabel(
            text="" if self.sent else self.doc,
            theme_text_color="Custom",
            text_color=(0.8, 0, 0, 1),
            halign='right' if self.sent else 'left',
            adaptive_height=True
        )

        self.add_widget(text_body)
        self.add_widget(source_text)

class BackGround(MDScreen):
    docs_layout = ObjectProperty(None)
    select_source_layout = ObjectProperty(None)
    txtbox = ObjectProperty(None)
    chat_scroll = ObjectProperty(None)
    chat_layout = ObjectProperty(None)
    message_queue = queue.Queue()
    messages = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_focus(self, instance, value):
        if value:  # When the text field is focused
            self.ids.chat_scroll.scroll_to(instance, padding=10)

    def send_message(self, msg):
        if msg == "":
            notification("Enter query text")
            return
        self.ids.send_btn.disabled = True
        self.display_message(f"Me: \n{msg}", "query", sent=True)
        self.txtbox.text = ""
        self.ids.send_btn.disabled = False

    def display_message(self, message, response_doc, sent):
        message_layout = MessageLayout(message, response_doc, sent)
        self.chat_layout.add_widget(message_layout)
        Clock.schedule_once(lambda dt: self.chat_scroll.scroll_to(message_layout), 0.1)

    def delete_file(self, files):
        """Method to delete files from storage."""
        for file in files:
            try:
                os.remove(os.path.join(docs_dir, file))
                self.docs_layout.refresh_data()
            except FileNotFoundError:
                print(f"File {file} not found")
            except Exception as e:
                print(f"An error occurred: {str(e)}")

    def delete_doc(self):
        self.delete_file(selected_files)
        selected_files.clear()
        self.docs_layout.refresh_data()
        self.select_source_layout.refresh_data()

    def clear_storage(self):
        shutil.rmtree(docs_dir)
        shutil.rmtree(db_dir)
        os.makedirs(docs_dir)
        os.makedirs(db_dir)
        self.docs_layout.refresh_data()

class ChatDocApp(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager, select_path=self.select_path, ext=['.pdf']
        )

    def build(self):
        self.title = 'ChatDocApp'
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        return Builder.load_file("chatdocapp.kv")

    def file_manager_open(self, *args):
        self.file_manager.show(os.path.expanduser("~"))
        self.manager_open = True
        self.file_manager.show_disks()

    def open_file_manager(self, *args):
        Clock.schedule_once(self.file_manager_open, 0.1)

    def select_path(self, path: str):
        self.exit_manager()
        fn = os.path.basename(path)
        if fn.lower().endswith(".pdf"):
            file_path = os.path.join(docs_dir, fn)
            if fn in os.listdir(docs_dir):
                notification("File already exists")
            else:
                shutil.copy(path, file_path)
                self.root.ids.docs_layout.refresh_data()
        else:
            notification("Only PDF files are allowed")

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def on_stop(self):
        # Perform cleanup here if necessary
        pass

if __name__ == "__main__":
    ChatDocApp().run()

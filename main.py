import os
from kivy.utils import platform
# Ensure the path is correctly set for Android
if platform == 'android':
    from jnius import autoclass
    Environment = autoclass('android.os.Environment')
    documents_dir = Environment.getExternalStorageDirectory().getPath()
    env_path = os.path.join(documents_dir, '.env')
    android_storage_path = Environment.getExternalStorageDirectory().getAbsolutePath()
else:
    # Default to current working directory for other platforms
    env_path = os.path.join(os.getcwd(), '.env')

from resource import load_split_pdf, message_handler, initialize_api

import shutil
import queue
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
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
        MDLabel(
            text=text,
        ),
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

        # Disable the send button and change its icon to show loading state
        self.ids.send_btn.disabled = True
        self.ids.send_btn.icon = "loading"  # Replace with a spinner icon or any loading indicator

        # Display the message immediately
        self.display_message(f"Me: \n{msg}", "query", sent=True)

        # Schedule the message processing after a short delay to allow UI to update
        Clock.schedule_once(lambda dt: self.process_message(msg), 0.2)

    def process_message(self, msg):
        try:
            # Send query to the backend with message_handler
            answer, file = message_handler(msg, selected_sources)
            self.display_message(answer, file, sent=False)
        except Exception as err:
            notification(f"{err}! Try Again")
        finally:
            # Re-enable the send button and restore the icon
            self.ids.send_btn.disabled = False
            self.ids.send_btn.icon = "send"  # Restore original send icon
            self.txtbox.text = ""

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
                notification(f"File {file} not found")
            except Exception as e:
                notification(f"An error occurred: {str(e)}")

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
        self.loading_dialog = None  # Placeholder for loading dialog
        self.api_status = None

    def build(self):
        self.title = 'ChatDocApp'
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.api_status = initialize_api()
        return Builder.load_file("chatdocapp.kv")

    def file_manager_open(self, *args):
        # current_platform = platform()
        # if current_platform == 'android':
        #     documents_path = os.path.join(android_storage_path, "Documents")
        # else:
        #     documents_path = os.path.expanduser("~")
        #
        self.file_manager.show(os.path.expanduser("~"))
        self.manager_open = True
        self.file_manager.show_disks()

    def open_file_manager(self, *args):
        if not self.api_status:
            return notification("API key not initialized")
        else:
            Clock.schedule_once(self.file_manager_open, 0.1)

    def select_path(self, path: str):
        # Close the file manager immediately
        self.exit_manager()
        # Clock.schedule_once(lambda dt: self.show_loading_screen(), 0.1)
        fn = os.path.basename(path)
        if fn.lower().endswith(".pdf"):
            if fn in os.listdir(docs_dir):
                notification("File already exists")
            else:
                # Show the loading screen right after closing the file manager
                self.show_loading_screen()
                # Start processing the PDF with a small delay
                Clock.schedule_once(lambda dt: self.process_pdf(path), 0.5)
        else:
            notification("Only PDF files are allowed")

    def process_pdf(self, path):
        try:
            fn = os.path.basename(path)
            file_path = os.path.join(docs_dir, fn)
            uploaded_fl = load_split_pdf(path)
            if uploaded_fl:
                shutil.copy(path, file_path)
                self.root.ids.docs_layout.refresh_data()
                notification(f"{os.path.basename(uploaded_fl)} processed and saved.")
            else:
                notification("Failed to process the PDF.")
        finally:
            # Hide loading screen after processing is complete
            self.hide_loading_screen()

    def exit_manager(self, *args):
        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True

    def show_loading_screen(self):
        """Show a loading screen dialog."""
        if not self.loading_dialog:
            self.loading_dialog = MDDialog(
                text="Processing PDF, please wait...",
                auto_dismiss=False
            )
        self.loading_dialog.open()

    def hide_loading_screen(self):
        """Hide the loading screen dialog."""
        if self.loading_dialog:
            self.loading_dialog.dismiss()

    def on_stop(self):
        # Perform cleanup here if necessary
        pass

if __name__ == "__main__":
    ChatDocApp().run()

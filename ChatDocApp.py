# kivymd-1.2.0
import os
import shutil
import queue
import requests
from kivy.clock import Clock
from kivy.config import Config
from kivy.lang import Builder

Config.set('graphics', 'width', '350')
Config.set('graphics', 'height', '550')

from kivy.core.window import Window
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.metrics import dp
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.filemanager import MDFileManager
from kivymd.icon_definitions import md_icons
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.behaviors import FocusBehavior
from kivy.properties import BooleanProperty, ListProperty
from kivy.uix.recycleview.layout import LayoutSelectionBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.snackbar import MDSnackbar
from kivymd.uix.behaviors.toggle_behavior import MDToggleButton
from kivymd.uix.button import MDFlatButton, MDIconButton
# from kivymd.toast import toast

# from resource import message_handler
from resource import StorageManager, ChatDocBackend

sm = StorageManager()
backend = ChatDocBackend()
selected_files = []
selected_sources = []

def notification(text):
    # toast(text=text, background=[0.8,0,0,1], duration=6.0,)
    MDSnackbar(
        MDLabel(
            text=text,
        ),
        # y=dp(300),
        pos_hint={"center_x": 0.5},
        # size_hint_x=0.5,
        md_bg_color=(0.8,0,0,1)
    ).open()
        

def update_selection(files, file_name, is_selected):
    """
    Function to add and remove file from selected list
    """
    if is_selected:
        if file_name not in files:
            files.append(file_name)
        print(files)
    else:
        try:
            files.remove(file_name)
        except ValueError:
            pass
        print(files)


class SelectableRecycleBoxLayout(FocusBehavior, LayoutSelectionBehavior,
                                 RecycleBoxLayout):
    ''' Adds selection and focus behavior to the view. '''


class SourceToggleView(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)    

    fn = StringProperty("")

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(SourceToggleView, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(SourceToggleView, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        file_name = rv.data[index]['fn']
        update_selection(selected_sources,file_name,is_selected)


class DocsLayout(RecycleDataViewBehavior, Label):
    ''' Add selection support to the Label '''
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)    

    fn = StringProperty("")

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        self.index = index
        return super(DocsLayout, self).refresh_view_attrs(
            rv, index, data)

    def on_touch_down(self, touch):
        ''' Add selection on touch down '''
        if super(DocsLayout, self).on_touch_down(touch):
            return True
        if self.collide_point(*touch.pos) and self.selectable:
            return self.parent.select_with_touch(self.index, touch)

    def apply_selection(self, rv, index, is_selected):
        ''' Respond to the selection of items in the view. '''
        self.selected = is_selected
        file_name = rv.data[index]['fn']
        update_selection(selected_files,file_name,is_selected)


class RV(RecycleView):
    """
    Dcocument List View Page
    """
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        
        self.refresh_data()

    def refresh_data(self):
        self.data = [{'fn': str(x)} for x in sm.show_docs()]


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
            theme_text_color= "Custom", 
            text_color=(0, 0.5, 1, 1) if self.sent else (0, 0, 0, 1),
            adaptive_height=True,        
            markup=True
        )

        source_text = MDLabel(
            text="" if self.sent else self.doc,
            theme_text_color= "Custom",
            text_color=(0.8,0,0,1),
            halign='right' if self.sent else 'left',
            adaptive_height=True
        )

        self.add_widget(text_body)
        self.add_widget(source_text)


class BackGround(MDScreen):
    docs_layout = ObjectProperty(None)
    select_source_layout = ObjectProperty(None)
    txtbox = ObjectProperty(None)
    chat_scroll = ObjectProperty(None)  # Referencing the ScrollView
    chat_layout = ObjectProperty(None)
    message_queue = queue.Queue()
    messages = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def send_message(self, msg):
        if msg == "":
            notification("Enter query text")
            return
        self.ids.send_btn.disabled = True
        self.display_message(f"Me: \n{msg}", "query", sent=True)

        # send query to the backend with message_handler
        try:
            answer, file = backend.message_handler(msg, selected_sources)
            self.display_message(answer, file, sent=False)
        except Exception as err:
            notification(f"{err}! Try Again")

        self.txtbox.text = ""
        self.ids.send_btn.disabled = False

    def display_message(self, message, response_doc, sent):
        message_layout = MessageLayout(message, response_doc, sent)
        self.chat_layout.add_widget(message_layout)
        Clock.schedule_once(lambda dt: self.chat_scroll.scroll_to(message_layout), 0.1)  # Ensure scrolling happens after the UI update


    def delete_doc(self):
        # Delete files from docs
        sm.delete_doc(selected_files)
        # Reload Vector Store when file(s) is deleted
        if selected_files:
            backend.unload_docs()
            print("vectore store finish re-loading")

        # refresh DocsLayout
        rv_instance = self.docs_layout
        rv_instance.refresh_data()

        # Remove deleted files from selected_files list
        for file_name in selected_files.copy():
            if file_name not in [item['fn'] for item in rv_instance.data]:
                selected_files.remove(file_name)

        # Refresh SourceToggleView
        src_rv_instance = self.select_source_layout
        src_rv_instance.refresh_data()

        # Remove deleted files from selected_sources list
        for file_name in selected_sources.copy():
            if file_name not in [item['fn'] for item in src_rv_instance.data]:
                selected_sources.remove(file_name)


    def clear_storage(self):
        sm.clear_storage()
        # Refresh Chat History 
        backend.clr_history()

class ChatDocApp(MDApp):
    #docs_layout = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Window.bind(on_keyboard=self.events)
        self.manager_open = False
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager, select_path=self.select_path
        )

    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        return Builder.load_file("chatdocapp.kv")
        
    def file_manager_open(self):
        self.file_manager.show(os.path.expanduser("~"))  # output manager to the screen
        self.manager_open = True

    def select_path(self, path: str):
        '''
        It will be called when you click on the file name
        or the catalog selection button.

        :param path: path to the selected directory or file;
        '''

        self.exit_manager()
        fn = os.path.basename(path)
        if fn.endswith(".pdf") or fn.endswith(".PDF"):
            output_folder = "docs"
            if fn in os.listdir(output_folder):
                notification("file already exist")
            else:
                file_path = os.path.join(output_folder, fn)
                os.makedirs(output_folder, exist_ok=True)
                shutil.copy(path, file_path)                
                rv_instance = self.root.ids.docs_layout
                rv_instance.refresh_data()     
                
                # try:           
                backend.load_doc(fn)
                # except  Exception as err:
        #             notification("Embeddings Error! \n \t Delete Document and Try Again")
        #         notification("Document Uploaded Successfully")
        else:
            notification("only pdf file")

    def exit_manager(self, *args):
        '''Called when the user reaches the root of the directory tree.'''

        self.manager_open = False
        self.file_manager.close()

    def events(self, instance, keyboard, keycode, text, modifiers):
        '''Called when buttons are pressed on the mobile device.'''

        if keyboard in (1001, 27):
            if self.manager_open:
                self.file_manager.back()
        return True
    
    

ChatDocApp().run()

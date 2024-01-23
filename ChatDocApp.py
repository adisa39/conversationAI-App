import os
import shutil
import queue
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivymd.uix.label import MDLabel
from kivymd.uix.scrollview import MDScrollView

Config.set("graphics", "width", "400")

from kivy.core.window import Window
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.properties import ObjectProperty, NumericProperty, StringProperty
from kivy.uix.recycleview import RecycleView
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.filemanager import MDFileManager
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen

from resource import message_handler


class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)


class Chat(RecycleDataViewBehavior, MDBoxLayout):
    msg = StringProperty("")
    result = StringProperty("")

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''

        self.index = index
        return super(Chat, self).refresh_view_attrs(rv, index, data)


class BackGround(MDScreen):
    recycleView = ObjectProperty(None)
    txtbox = ObjectProperty(None)
    chat_box = ObjectProperty(None)
    message_queue = queue.Queue()
    messages = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Clock.schedule_interval(self.update_display, 0.1)

    def send_message(self, msg):
        if msg == "":
            toast("Enter query text")
            return
        self.ids.send_btn.disabled = True
        self.display_message(f"Me: {msg}", sent=True)
        message_handler(msg, display_func=self.display_message)

        # self.messages.append(f"Doc: {result['result']}")
        # self.recycleView.data = [{"msg": str(i)} for i in self.messages]
        # print(self.messages)
        self.txtbox.text = ""
        self.ids.send_btn.disabled = False

    def display_message(self, message, sent=False):
        message_label = MDLabel(text=message, size_hint_y=None)
        message_label.adaptive_height = True
        message_label.padding_y = "15dp"
        #message_label.height = max(message_label.texture_size[1], 30)
        if sent:
            message_label.color = (0, 0.5, 1, 1)
            message_label.halign = 'right'
            #message_label.text =message

        else:
            message_label.color = "black"
            message_label.halign = 'left'
            #message_label.text = message
        self.chat_box.add_widget(message_label)
        self.chat_box.scroll_y = 0


class ChatDocApp(MDApp):
    #bg = ObjectProperty(None)

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
        #self.bg = BackGround()
        return Builder.load_string(
            '''
#:import utils kivy.utils
#:set color1 "#DD7835"
#:set color2 "#000000"

<LeftAlignLabel@Label>:
    text_size: self.size
    halign: "left"
    valign: "center"
    canvas.before:
        Color:
            rgb: utils.get_random_color(color1)
            rgba: 0, 0, 0, 0
        Rectangle:
            pos: self.pos
            size: self.size


<FitLabel@MDLabel>:
    # size_hint: None, None
    # size: self.texture_size
    #adaptive_size: True

BackGround:
    # recycleView: recycleView
    txtbox: text_box_id
    chat_box: chat_box

    MDBottomNavigation:
        #panel_color: "#eeeaea"
        selected_color_background: "orange"
        text_color_active: "lightgrey"

        MDBottomNavigationItem:
            name: 'screen 1'
            text: 'Chat'
            icon: 'gmail'
            badge_icon: "numeric-10"

            MDFloatLayout:
                md_bg_color: "#f1f1f1"
                                
                BoxLayout:
                    orientation: 'vertical'
                    pos: self.pos
                    size: self.size
                    padding: dp(10)
                    spacing: dp(10)
                              
                    MDBoxLayout:
                        adaptive_height: True
                        
                        MDLabel:
                            md_bg_color: "lightblue"
                            text: 'Chats'
                            halign: 'center'
                            color: 'black'
                            bold: True
                            #adaptive_height: True
                            padding: "20dp"
                            font_size: "30sp"
                            pos_hint: {"top":1, "center_x": .5}                    
                    
                    # ----- CHATBOX VIEW LAYOUT ---------
                    ScrollView:
                        BoxLayout:
                            padding: dp(20), dp(20)
                            id: chat_box
                            orientation: 'vertical'
                            size_hint_y: None
                            height: self.minimum_height                        
                        
                    MDBoxLayout:
                        padding: "10dp"
                        #adaptive_size: True
                        size_hint: 1, None
                        height: "70dp"
                        pos_hint: {"bottom": 1, "center_x": .5}
                
                        MDTextFieldRect:
                            id: text_box_id
                            hint_text: "Enter your text here"                            
                            size_hint_x: .7                            
                        
                        MDRaisedButton:
                            id: send_btn
                            text: "Send"
                            #size_hint_x: .3
                            size_hint: .2, 1
                            on_press: root.send_message(text_box_id.text)      
                    

        MDBottomNavigationItem:
            name: 'screen 2'
            text: 'Configuration'
            icon: 'twitter'
            badge_icon: "numeric-5"

            MDFloatLayout:
                md_bg_color: "#f1f1f1"
                
                MDRoundFlatIconButton:
                    text: "Upload File"
                    icon: "file"
                    pos_hint: {"center_x": .5, "center_y": .5}
                    on_release: app.file_manager_open()

        MDBottomNavigationItem:
            name: 'screen 3'
            text: 'History'
            icon: 'linkedin'

            MDLabel:
                text: 'History'
                halign: 'center'

<Chat>:
    MDBoxLayout:
        adaptive_height: True
        
        MDLabel:
            text: root.msg
            color: "black"
        

'''
        )

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
                toast("file already exist")
            else:
                file_path = os.path.join(output_folder, fn)
                os.makedirs(output_folder, exist_ok=True)
                shutil.copy(path, file_path)
                toast("uploaded successfully")
        else:
            toast("only pdf file")

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

import string
import random
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivy.clock import Clock
from kivy.uix.popup import Popup



alphabet = list(string.ascii_letters)
digits = list(string.digits)
special = list("!@#$%^&*()")
chars = list(string.ascii_letters+string.digits+"!@#$%^&*()")

#This is a popup to ensure validation
class Splash(Screen):
    pass
class LogIn(Screen):
    pass
class CreateAccount(Screen):


    def verify_pass(self):
        close = MDFlatButton(text = 'Close', on_press = self.dismiss)
        self.dialog = MDDialog(title = 'Error Encountered', text = 'Please ensure that passwords match!', buttons = [close])
        first = self.ids.userpass.text
        second = self.ids.second.text
        if first != second:
            self.dialog.open()
        else:
            self.manager.transition.direction = 'left'
            self.manager.current = 'pass'

            
    def dismiss(self, obj):
        self.dialog.dismiss()
        self.ids.userpass.text = ''
        self.ids.second.text = ''


class PasswordScreen(Screen):
    def buildPassword(self):
        
        #Create dialog box to handle errors!
        close = MDFlatButton(text = 'Close', on_press = self.dismissDigit)
        self.digit = MDDialog(title = 'Error Encountered', text = 'Fill all fields and only use digits', buttons = [close], auto_dismiss = False)

        #Give intial assignment and value attribute
        pass_length = 0
        a_count = 0
        d_count = 0
        s_count = 0
        total_count = 0
        errorFound = False
        #Grab initial counts
        try:
            pass_length = int(self.ids.length.text)
            a_count = int(self.ids.pass_letter.text)
            d_count = int(self.ids.pass_number.text)
            s_count = int(self.ids.pass_special.text)
        except ValueError:
            errorFound = True
            self.digit.open()
        total_count = a_count + d_count + s_count

        #Holder for our password, will be populated by following loops
        password = []

        #3 loops to add in each amount of digits, chars, and specials
        for i in range(a_count):
            password.append(random.choice(alphabet))  #Populate with alphabet
    
        for i in range(d_count):
            password.append(random.choice(digits))    #Populate with digits

        for i in range(s_count):
            password.append(random.choice(special))   #Populate with special chars

        random.shuffle(password)

        #Check to ensure that total count is less than the password length
        if(total_count < pass_length):
            if total_count==0:  #Ensure no overlap of error messages
                pass
            else:
                random.shuffle(chars)  #Shuffle the created password
                for i in range(pass_length - total_count):
                    password.append(random.choice(chars))

        close = MDFlatButton(text = 'Close', on_press = self.dismissLength)
        self.length = MDDialog(title = 'Error Encountered', text = 'Please ensure entered char total less than length', buttons = [close], auto_dismiss = False)
        if(total_count > pass_length):
            errorFound = True
            self.length.open()
        
        
        
        random.shuffle(password)
        holder = "".join(password)
        if errorFound == False:
            self.ids.generated.text = holder
        else:
            self.ids.generated.text = 'Lets try again'
            self.ids.pass_number.text = ''
            self.ids.pass_letter.text = ''
            self.ids.pass_special.text = ''
            self.ids.length.text = ''
    def dismissLength(self, obj):
        self.length.dismiss()
    
    
    def dismissDigit(self, obj):
        self.digit.dismiss()

class Saved(Screen):
    pass


class WindowManager(ScreenManager):
    pass

class LoginPage(MDApp):
    def build(self):
        self.theme_cls.theme_style = 'Light'   #Background color
        self.theme_cls.accent_palette = 'BlueGray'
        screen = Builder.load_file('log.kv')
        return screen

LoginPage().run()



#holder area for checkbox instead of digit entry

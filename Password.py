import string
import random
import keyring
from kivymd.app import MDApp
from kivy.lang.builder import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import ObjectProperty, StringProperty
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.dialog import MDDialog
from kivy.uix.popup import Popup
from kivymd.uix.list import TwoLineIconListItem, IconLeftWidget
import sqlite3

service_id = 'PassWordGenerator'


#List reference for how to populate password field from generator
alphabet = list(string.ascii_letters)
digits = list(string.digits)
special = list("!@#$%^&*()")
chars = list(string.ascii_letters+string.digits+"!@#$%^&*()")



#This is a popup to ensure validation


class Splash(Screen):
    pass


class LogIn(Screen):
    
    #Ensures that there is a user within stored local encryption that matches credentials
    def verify(self):
        close = MDFlatButton(text = 'Close', on_press = self.dismiss)
        self.dialog = MDDialog(title = 'Error Encountered', text = 'This user does not exist! \n\nPlease create an account', buttons = [close])
        user = self.ids.user.text
        password = self.ids.userpass.text
        if keyring.get_password(service_id, user) == password:
            self.manager.current= 'pass'
            self.manager.transition.direction = 'left'
        else:
            self.dialog.open()

    #Helper to dismiss popup
    def dismiss(self, obj):
        self.dialog.dismiss()
        self.ids.user.text = ''
        self.ids.userpass.text = ''



class DeleteAccount(Screen):
    
    #Function to delete user/account from database
    def delete_pass(self):
        user = self.ids.user.text

        #Dialog if removal failed
        closeFail = MDFlatButton(text = 'Close', on_press = self.dismissFail)
        closeSuccess = MDFlatButton(text = 'Close', on_press = self.dismissSuccess)

        #Dialog if removal succeeds 
        self.fail = MDDialog(title = 'Error Encountered', text = 'This user does not exist!', buttons = [closeFail])
        self.success = MDDialog(title = 'Success!', text = 'This user has been deleted from the database', buttons = [closeSuccess])

        #Try/Except block to catch error and call dialog box correctly
        try:
            keyring.delete_password(service_id, user)
            self.success.open()
        except keyring.errors.PasswordDeleteError:
            self.fail.open()
            user = ''

    #Helper to dismiss success dialog box
    def dismissSuccess(self, obj):
        self.success.dismiss()
        self.manager.current = 'login'
        self.manager.transition.direction = 'up'


    #Helper to dismiss success dialog box
    def dismissFail(self, obj):
        self.fail.dismiss()
        self.ids.user.text = ''
            
        


class CreateAccount(Screen):

    # Function to ensure passwords match
    # Don't want user to enter two different passwords by accident (stop human error)
    def verify_pass(self):

        #Dialog box to be opened if error encountered
        close = MDFlatButton(text = 'Close', on_press = self.dismiss)
        self.dialog = MDDialog(title = 'Error Encountered', text = 'Please ensure that passwords match!', buttons = [close])
        #Grab necessary variables
        user = self.ids.username.text
        first = self.ids.userpass.text
        second = self.ids.second.text

        #Conditional to check if passwords match
        #If not open dialog for user to notify them of error
        if first != second:
            self.dialog.open()
        else:
            keyring.set_password(service_id, user, first)
            self.manager.current = 'login'

    #Helper to dismiss dialog box      
    def dismiss(self, obj):
        self.dialog.dismiss()
        self.ids.userpass.text = ''
        self.ids.second.text = ''

#TODO: There is stacking of dialog boxes: "Enter only Digits" and "Filling in gaps"
        # Both of these appear upon a user entering in a letter instead of a digit in boxes
class PasswordScreen(Screen):
    
    #This is main function within the application to generate our password for the user
    #   Uses predetermined global lists at top of file for alphabet, digits, and special characters
    #   Based upon a random.choice application of each list dependent on the users preferences
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
        #Handle error if they enter anything OTHER than a digit (due to INT casting)
        except ValueError:
            errorFound = True
            self.digit.open()
        #Calculate total
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

        #Shuffle to ensure randomness of password
        random.shuffle(password)

        #Dialog box to inform user we are strengthening their password to fill in remaining space
        #     Triggers if user desired length > total # of each char type
        close = MDFlatButton(text = 'Close', on_press = self.dismissFill)
        self.fill = MDDialog(title = 'Filling in the gaps', text = 'Adding in additional random characters to satisfy length', buttons = [close], auto_dismiss = False)

        #Check to ensure that total count is less than the password length
        if(total_count < pass_length):
            if total_count==0:  #Ensure no overlap of error messages
                pass
            else:
                random.shuffle(chars)  #Shuffle the created password
                for i in range(pass_length - total_count):
                    password.append(random.choice(chars))
                self.fill.open()   #Open dialog to inform user we are filling in gaps, if their entered numbers less than total desired length



        #Dialog box to handle error that total counts from digit, char, and special !> total length
        close = MDFlatButton(text = 'Close', on_press = self.dismissLength)
        self.length = MDDialog(title = 'Error Encountered', text = 'Please ensure entered char total less than length', buttons = [close], auto_dismiss = False)
        #Conditional to ensure this does not happen
        if(total_count > pass_length):
            errorFound = True
            self.length.open()
        
        
        #Another random shuffle and turn list into string to be printed
        random.shuffle(password)
        holder = "".join(password)
        
        #Conditional to ensure that if error is found we don't print anything to generated password box
        #   IF no errors than print password
        #   If any errors, reset all text boxes and allow user to try again
        if errorFound == False:
            self.ids.generated.text = holder
        else:
            self.resetText()
    
    #Function called to clear passed information from user
    def clear(self):
        self.manager.get_screen('login').ids.user.text = ''
        self.manager.get_screen('login').ids.userpass.text = ''
    
    #Method to add generated password to next pages list
    def save(self):

        pic = IconLeftWidget(icon = 'eye-off')
        name = self.ids.ID.text
        password = self.ids.generated.text

        #Ensure user clicked the generate password button so we grab something
        if password == '':
            close = MDFlatButton(text = 'Close', on_press = self.dismissGen)
            self.gen = MDDialog(title = 'Error Encountered', text = 'Remember to click generate!', buttons = [close], auto_dismiss = False)
            self.gen.open()
        else:
            #Create list item based upon entries
            item = TwoLineIconListItem(text = name, secondary_text = password)
            item.add_widget(pic)

            #Adds item to next page list
            self.manager.get_screen('save').ids.main.add_widget(item)
            self.resetText()
        

    #Helpers for all dialog boxes to ensure dismissal
    def dismissGen(self, obj):
        self.gen.dismiss()
    def dismissLength(self, obj):
        self.length.dismiss()
    def dismissDigit(self, obj):
        self.digit.dismiss()
    def dismissFill(self, obj):
        self.fill.dismiss()

    def resetText(self):
        self.ids.ID.text = ''
        self.ids.generated.text = ''
        self.ids.length.text = ''
        self.ids.pass_number.text = ''
        self.ids.pass_letter.text = ''
        self.ids.pass_special.text = ''

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





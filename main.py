from kivy.config import Config
#from kivymd.icon_definitions import md_icons
#Config.set('graphics', 'resizable', False)
import math
from datetime import datetime
from create_table_fpdf2 import PDF
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp 
from kivy.lang import Builder
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty, NumericProperty
from kivymd.uix.list import ThreeLineListItem, TwoLineListItem
from kivy.uix.popup import Popup
import re
import sqlite3
import os
import glob
import sys
import json
from functools import partial
import shutil
# from kivymd.uix.filemanager import MDFileManager
from tkinter import filedialog
from tkinter import *
from test.dtracedata import instance
root = Tk()
root.withdraw()


Window.size = (370, 630)

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class SplashWin(Screen):
    pass

class AboutWin(Screen):
    pass

class LoginWin(Screen):
    login_uname = ObjectProperty(None)
    login_pw = ObjectProperty(None)
    auth_txt = StringProperty("")
        
    def logButt(self):
        username = self.login_uname.text
        password = self.login_pw.text
        print("Login_Username : ",self.login_uname.text,"\nLogin_Password : ",self.login_pw.text)
        self.authent(username, password)
        auth = self.authent(username, password)
        if (auth == 0):
            if(username=="" or password==""):
                self.auth_txt = "         Authentication Failed !"
            else:
                self.auth_txt = "  Username or Password is Incorrect !"
            self.login_msg.color = [215/255, 49/255, 49/255, 1]
            print("login failed")
        else:
            self.auth_txt = "      Authentication Succeeded !"
            self.login_msg.color = [31/255, 108/255, 153/255, 1]
            Clock.schedule_once(self.sup_txt, 1.2)
            Clock.schedule_once(self.switch_to_main, 1.2)
            user_screen = self.manager.get_screen("Home")
            user_screen.user_name = username
            newpath = f'calibres_docs/{username}/' 
            if not os.path.exists(newpath):
                os.makedirs(newpath)
        
    def authent(self, username, password):
        aut = 0
        try:
            connec = sqlite3.connect(resource_path("appdb.db"))
            curs = connec.cursor()
            print("Connected to SQLite")
            select_query = """SELECT * from users"""
            curs.execute(select_query)
            rows = curs.fetchall()
            print("total rows : ",len(rows))
            for row in rows:
                if (row[0]==username and row[2]==password):
                    aut = 1
            connec.commit()
            curs.close()
            if (aut == 1):
                print("Successful authentication")
        except sqlite3.Error as e:
            print("Failed authentication ",e)
        finally:
            if connec:            
                connec.close()
                print("Disconnected from SQLite")
                return aut
            
    def sup_auth_txt(self):
        self.auth_txt = ""
        
    def sup_txt(self, *args):
        self.auth_txt = ""
    
    def switch_to_main(self, *args):
        app = MDApp.get_running_app()
        app.root.current = "Home"

class SignupWin(Screen):
    signup_uname = ObjectProperty(None)
    signup_email = ObjectProperty(None)
    signup_pw = ObjectProperty(None)
    signup_cpw = ObjectProperty(None)
    uname_req= BooleanProperty(False)
    email_req = BooleanProperty(False)
    pw_req = BooleanProperty(False)
    cpw_req = BooleanProperty(False)
    req_fields_txt = StringProperty("") 
    
    def signButt(self):
        username = self.signup_uname.text
        email = self.signup_email.text
        password = self.signup_pw.text
        confpassword = self.signup_cpw.text
        
        notblank = 1
        
        print("SignUp_Username : ",username,"\nSignUp_Email : ",email,
              "\nSignUp_Password : ",self.signup_pw.text)
        
        if (username=="" or email=="" or password=="" or confpassword==""):
            self.req_fields_txt = "              All Fields are Required !"
            self.signup_msg.color = [215/255, 49/255, 49/255, 1]
            notblank = 0
        else:
            self.req_fields_txt = ""
        
        error = self.errorCheck(username, email, password, confpassword)
        redd = self.redondCheck(username, email)
        
        if (redd == 1):
            self.req_fields_txt = "         Username already existing !"
            self.signup_msg.color = [25/255, 137/255, 180/255, 1]
        elif ((notblank - error) == 1):
            self.req_fields_txt = "   Sign Up Successful ! Back to log in"
            self.signup_msg.color = [18/255, 153/255, 45/255, 1]
            self.register(username, email, password)
            
            
        
        
    def errorCheck(self, username, email, password, confpassword):
        err = 0
        uname_patt = "^[A-Za-z0-9]+$"
        email_patt = "^[_a-zA-Z0-9\.]+@([a-zA-Z]|[um5\.ac])+[\.]\w{2,3}$"
        pw_patt = "(?![A-Za-z]{8}|[0-9]{8})[0-9a-zA-Z]{8}" 
        
        if (username=="" or re.search(uname_patt, username)):
            self.uname_req = False
        else:
            self.uname_req = True
            err = 1
        
        if (email=="" or re.search(email_patt, email)):
            self.email_req = False
        else:
            self.email_req = True
            err = 1
        
        if (password=="" or re.search(pw_patt, password)):
            self.pw_req = False
        else:
            self.pw_req = True
            err = 1
        if (confpassword=="" or password==confpassword):
            self.cpw_req = False
        else:
            self.cpw_req = True
            err = 1
        
        return err
    
    def redondCheck(self, username, email):
        red = 0
        try:
            connec = sqlite3.connect(resource_path("appdb.db"))
            curs = connec.cursor()
            print("Connected to SQLite")
            select_query = """SELECT * from users"""
            curs.execute(select_query)
            rows = curs.fetchall()
            print("total rows : ",len(rows))
            for row in rows:
                if (row[0]==username or row[1]==email):
                    red = 1
            connec.commit()
            curs.close()
            print("Successful check")
        except sqlite3.Error as e:
            print("Failed check ",e)
        finally:
            if connec:            
                connec.close()
                print("Disconnected from SQLite")
                return red
        
    
    def register(self, username, email, password):
        try:
            connec = sqlite3.connect(resource_path("appdb.db"))
            curs = connec.cursor()
            print("Connected to SQLite")
            insert_query = """INSERT INTO users(username, email, password) VALUES (?, ?, ?);"""
            data_insert = (username, email, password)
            print("{} , {} , {}".format(username, email, password))
            curs.execute(insert_query,data_insert)
            connec.commit()
            curs.close()
            print("Successful insertion")
        except sqlite3.Error as e:
            print("Failed insertion ",e)
        finally:
            if connec:            
                connec.close()
                print("Disconnected from SQLite")
    

class HomeWin(Screen):
    
    def historyConstructor(self):
        screen = self.manager.get_screen("History")
        screen.getHistory()

class NetworkWin(Screen):
    voltage_value = ObjectProperty()
    voltage = NumericProperty()
    networkType = NumericProperty()
    
    def network_properties(self):
        try:
            self.voltage = int(self.voltage_value.text)
            self.ids.network_error.text = ""
            if (self.ids.mono_box.state == 'normal' and self.ids.tri_box.state == 'normal'):
                self.ids.network_error.text = "Choisir le type de votre réseau !"
            else:
                if(self.ids.mono_box.state == 'down'):
                    self.networkType = 1
                else:
                    self.networkType = 3
                app = MDApp.get_running_app()
                app.root.current = "Load"
                app.root.transition.direction = "left"
            
            print("voltage = "+str(self.voltage))
            print("network = "+str(self.networkType))
                
        except ValueError:
            if (self.ids.mono_box.state == 'normal' and self.ids.tri_box.state == 'normal'):
                self.ids.network_error.text = "Choisir le type de votre réseau !\nEntrer la valeur de tension simple"
            else:
                self.ids.network_error.text = "Entrer la valeur de tension simple"

            
class LoadWin(Screen):
    load_number = NumericProperty(0)
    load_type_labels = NumericProperty(10)
    load_type_boxes = NumericProperty(10)
    load_types = NumericProperty(10)
    puissance = NumericProperty()
    cosphi = NumericProperty()
    
    jsondata= '''
    {
        "usersdeparts":
        [  
        ]
    } 
    '''
    data = json.loads(jsondata)

    
    def __init__(self, **kwargs): 
        super(Screen, self).__init__(**kwargs)
        # self.depart_label = "Départ "+str(self.depart_number)+" :"

    
    def show_load_boxes(self):
        self.ids.load_error.text = ""
        if (self.ids.add_load.text == "Valider"):
            self.load_properties()
        else:
            self.ids.add_load.text = "Valider"
            self.load_type_labels = 10.9 - self.load_type_labels
            self.load_type_boxes = 10.85 - self.load_type_boxes
            self.load_types = 10.85 - self.load_types
    
    def load_properties(self):
        try:
            popup = PopupWin()
            if (self.ids.res_box.state == 'normal' and self.ids.ind_box.state == 'normal'):
                self.ids.load_error.text = "Choisir le type de votre charge"
            elif(self.ids.res_box.state == 'down'):
                self.puissance = float(self.ids.power_rating.text)
                self.cosphi = 1.0
                self.set_up_load_page()
                self.add_user_load()
                popup.open()
                self.load_number += 1
                
            else:
                self.puissance = float(self.ids.power_rating.text)
                self.cosphi = math.sqrt(1-float(self.ids.cos_phi.text))
                self.cosphi = float(self.ids.cos_phi.text)
                self.set_up_load_page()                 
                self.add_user_load()
                popup.open()
                self.load_number += 1
                            
        except ValueError:
            self.ids.load_error.text = "Remplir correctement les champs !"
                        

    
    def set_up_load_page(self):
        self.ids.res_box.active = False
        self.ids.ind_box.active = False
        self.load_type_labels = 10
        self.load_type_boxes = 10
        self.load_types = 10
        self.ids.add_load.text = "+ Charge"
        self.ids.load_error.text = ""
        # self.ids.power_rating.text = ""
        # self.ids.cos_phi.text = ""

    def load_next(self):
        self.ids.load_error.text = ""
        if(self.load_number < 2):
            self.ids.load_error.text = "Ajouter au moins deux charges !"
        else:
            loadscalc_screen = self.manager.get_screen("LoadsCalc")
            loadscalc_screen.write_loads()
            app = MDApp.get_running_app()
            app.root.current = "LoadsCalc"
            app.root.transition.direction = "left"
            
            
    def add_user_load(self):
        name = self.ids._uname.text
        network_screen = self.manager.get_screen("Network")
        simple_voltage = network_screen.voltage
        network_type = network_screen.networkType
        if(self.load_number == 0):
            departsArray = self.data['usersdeparts']
            newDepart = {
            "user_name": name,
            "network": network_type,
            "voltage": simple_voltage,
            "loads":[
                    {
                        "rating_power": self.puissance,
                        "cos_phi": self.cosphi
                    }
                ]    
            }
            departsArray.append(newDepart)
            with open('appdata.json', 'w') as f:
                json.dump(self.data, f, indent=2)
            
        else:
            with open('appdata.json') as f:
                data = json.load(f)
                proprti = data['usersdeparts']
                proprti[0]['network'] = network_type
                proprti[0]['voltage'] = simple_voltage
                print(proprti[0]['network'])
                print(proprti[0]['voltage'])


            for item in data['usersdeparts']:
                if(item['user_name']==name):
                    user_loads = item['loads']
                    new_load = {
                        "rating_power": self.puissance,
                        "cos_phi": self.cosphi
                    }
                    user_loads.append(new_load)
                    
            with open('appdata.json', 'w') as f:
                json.dump(data, f, indent=2)

        print("voltage = "+str(simple_voltage))
        print("network = "+str(network_type))
                
    def reset_loads(self):
        name = self.ids._uname.text
        self.load_number = 0.1
        with open('appdata.json') as f:
            data = json.load(f)
        for item in data['usersdeparts']:
            if(item['user_name']==name):
                user_loads = item['loads']
                user_loads.clear()
                
        with open('appdata.json', 'w') as f:
            json.dump(data, f, indent=2)
            

class LoadsCalcWin(Screen):
    
    def write_loads(self):
        with open('appdata.json') as f:
            data = json.load(f)
        for item in data['usersdeparts']:
            loadsArray = item['loads']
            for i,load in zip(range(0,len(loadsArray)),loadsArray):
                self.ids.container.add_widget(
                    ThreeLineListItem(
                        text = "Charge "+str(i+1)+" :",
                        secondary_text=" Puissance nominale : "+str(load['rating_power'])+" kW",
                        tertiary_text =" Facteur de puissance : "+str(load['cos_phi'])
                    )
                )
    
    def calculateBreakers(self):
        calibre_screen = self.manager.get_screen("Calibre")
        calibre_screen.breaker_rating()
        app = MDApp.get_running_app()
        app.root.current = "Calibre"
        app.root.transition.direction = "left"

    def removeWidget(self):
        self.ids.container.clear_widgets()
        
    def remove_loads(self):
        self.removeWidget()
        calibre_screen = self.manager.get_screen("Load")
        calibre_screen.reset_loads()
        app = MDApp.get_running_app()
        app.root.current = "Load"
        app.root.transition.direction = "right"




class CalibreWin(Screen):
    Ptot = NumericProperty(0)
    Qtot = NumericProperty(0)
    Stot = NumericProperty()
    norm_calibres = [1,2,3,4,6,10,16,20,25,40,50,63,80,100,125,160,200,250,400,630,800,1000,1250,1600,2000,2500,3200,4000,6300]
    dataArray = []
    download_path = StringProperty()
    
    _name = StringProperty()
    _reseau = NumericProperty()
    _tension_simple = NumericProperty()
    
    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)
    #     self.file_manager_obj = MDFileManager(
    #             select_path =self.choose_path,
    #             exit_manager =self.exit_manager,
    #             preview = True
    #         )
    
    def breaker_rating(self):
        name = self.ids._uname.text
        print(name)
        self.dataArray = [["Disjoncteurs","Puissance (kVA)","Facteur de puissance","Courant nominale (A)","Calibre (A)"]]
        with open('appdata.json') as f:
            data = json.load(f)
        for item in data['usersdeparts']:
            print("about to enter")
            if(item['user_name']==name):
                print("entred") 
                loadsArray = item['loads']
                tension_simple = item['voltage']
                reseau = item['network']
                print(tension_simple)
                for i,load in zip(range(0,len(loadsArray)),loadsArray):
                    self.Ptot += load['rating_power']*1000
                    self.Qtot += load['rating_power']*1000*math.tan(math.acos(load['cos_phi']))
                    current = load['rating_power']*1000/(reseau*tension_simple*load['cos_phi'])
                    S = math.sqrt(load['rating_power']*load['rating_power']+load['rating_power']*math.tan(math.acos(load['cos_phi']))*load['rating_power']*math.tan(math.acos(load['cos_phi'])))
                    arrayElem = ["Charge "+str(i+1),str(round(S,3)),str(load['cos_phi']),str(round(current,3)),str(self.chooseCalibre(current))]
                    self.dataArray.append(arrayElem)
                    current = self.chooseCalibre(current)
                        
                    self.ids.container.add_widget(
                        TwoLineListItem(
                            text = "Calibre du disjoncteur "+str(i+1)+" :",
                            secondary_text=" "+str(current)+" A"
                        )
                    )
                self.Stot = math.sqrt((self.Ptot)*(self.Ptot)+(self.Qtot)*(self.Qtot))
                global_current = self.Stot/(reseau*tension_simple)
                cosfi = self.Ptot/(reseau*tension_simple*global_current)
                arrayElem = ["En-tête",str(round((self.Stot/1000),3)),str(round(cosfi,2)),str(round(global_current,3)),str(self.chooseCalibre(global_current))]
                self.dataArray.append(arrayElem)
                global_current = self.chooseCalibre(global_current)
                self.ids.container.add_widget(
                    TwoLineListItem(
                        text = "Calibre du disjoncteur d'en-tête :",
                        secondary_text=" "+str(global_current)+" A"
                    )
                )
                
                self._name = name
                self._reseau = reseau
                self._tension_simple = tension_simple    
        
    # def choose_path(self, path):
    #     print(path)
    #     self.exit_manager()
    #
    # def open_file_manager(self):
    #     self.file_manager_obj.show('/')
    #
    # def exit_manager(self):
    #     self.file_manager_obj.close()
    
    def choose_path(self):
        self.download_path = filedialog.askdirectory(title="Select folder")
        if (self.download_path != ''):
            print(self.download_path)
            pdf = PDF()
            pdf.add_page()
            pdf.set_font("Times", size=12)
            pdf.image("logo4pdf.png", x=10, y=10, w=80)
            pdf.text(150, 17, "User : "+self._name)
            
            datenow = datetime.now().strftime("%B %d, %Y")
            timenow = datetime.now().strftime("%H:%M")
            pdf.text(150, 22, datenow)
            pdf.text(150, 27, timenow)
            pdf.ln(40)
            pdf.create_table(table_data = self.dataArray, title = self.reseauName(self._reseau, self._tension_simple), cell_width='even')
        
            pdf.output("calibres_docs/{}/breaker_doc_{}.pdf".format(self._name,datetime.now().strftime("%y%m%d%H%M")))
            self.download_path = self.download_path+"/breaker_doc_{}.pdf".format(datetime.now().strftime("%y%m%d%H%M"))
            pdf.output(self.download_path)
            print(self.dataArray)
    
    def chooseCalibre(self,current):
        for j in range(0,len(self.norm_calibres)):
            if (self.norm_calibres[j] > current):
                return self.norm_calibres[j]
    
    def removeWidget(self):
        self.Ptot = 0
        self.Qtot = 0
        self.Stot = 0
        self.ids.container.clear_widgets()
        
    def reseauName(self,reseau,tension):
        if(reseau==3):
            return "Calibres des disjoncteurs du départ sous le réseau triphasé de tension simple "+str(tension)+" V"
        else:
            return "Calibres des disjoncteurs du départ sous le réseau monophasé "+str(tension)+" V"
        

class HistoryWin(Screen):
    
    def getHistory(self):
        username = self.ids._uname.text
        rep = f'calibres_docs/{username}'
        curdir = os.getcwd()
        os.chdir(rep)
        breakerdocs = glob.glob('*.pdf')
        # breakerdocs.sort(key=lambda x: int(x.split("_")[2]))
        for f,i in zip(breakerdocs,range(0,len(breakerdocs))):
            breakerdocs[i]=f[0:len(f)-4]
        breakerdocs.sort(key=lambda x: int(x.split("_")[2]))
        for f,i in zip(breakerdocs,range(0,len(breakerdocs))):
            listItemWidget = TwoLineListItem(text = str(i+1)+") "+f, secondary_text="     [DOWNLOAD PDF]")
            # listItemWidget.bind(on_press=self.downloadPDFdoc(i))
            self.ids.container.add_widget(listItemWidget)
            #self.TwoLineListItem.bind(on_press=self.downloadPDFdoc(i))
        for child,i in zip(reversed(self.ids.container.children),range(0,len(breakerdocs))):
            if isinstance(child, TwoLineListItem):
                print(f"child: text={child.text}")
                # child.bind(on_press=self.downloadPDFdoc(i))
                # child.bind(on_press=self.downloadPDFdoc(i))
                child.bind(on_press=partial(self.downloadPDFdoc, i))
                
        os.chdir(curdir)
        
    def deleteHistory(self):
        username = self.ids._uname.text
        rep = f'calibres_docs/{username}'
        for filename in os.listdir(rep) :
            os.remove(rep + "/" + filename)
            
        app = MDApp.get_running_app()
        app.root.current = "Home"
        app.root.transition.direction = "right"
            
    def removeWidget(self):
        self.ids.container.clear_widgets()
        
    def downloadPDFdoc(self, n, instance):
        download_path = filedialog.askdirectory(title="Select folder")
        username = self.ids._uname.text
        rep = f'calibres_docs/{username}'
        for filename,i in zip(os.listdir(rep),range(0,len(os.listdir(rep)))):
            if (i==n and download_path!=''):
                src = f'calibres_docs/{username}/'+filename
                shutil.copy(src, download_path)
        print(n)
        
            
        
        
class PopupWin(Popup):
    # power = ObjectProperty()
    # cosphi = ObjectProperty()
    pass

class WinManager(ScreenManager):
    pass



class caliBREaker(MDApp):
    
    def build(self):
        connec = sqlite3.connect(resource_path("appdb.db"))
        curs = connec.cursor()
        curs.execute("""CREATE TABLE if not exists
            users
            (
                username text,
                email text,
                password text
            )
        """)
        connec.commit()
        connec.close()
        
        return Builder.load_file(resource_path("kvfile.kv"))
    
    def on_start(self):
        Clock.schedule_once(self.login, 6)
    
    def login(self, *args):
        print('transition')
        app = MDApp.get_running_app()
        app.root.current = "Login"
        app.root.transition.direction = "left"


caliBREaker().run()
    
    

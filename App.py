#GUI Libraries
import sv_ttk
import tkinter
import customtkinter
from PIL import Image, ImageDraw
from tkinter import messagebox, ttk

#OS Handling Libraries
import os
import datetime
import threading
from pathlib import Path

#Camera Handling and face recognitions
import cv2
import face_recognition
        
#Database Library
import sqlite3
import pandas
import numpy as np

#-------------------------------------------- Main Settings --------------------------------------------
class Settings:
    CURRENT_DIR = os.path.dirname(__file__)
    
    APP_SIZE = (1280, 720)
    TITLE = "Bank Locker System"
    ICON = f'{CURRENT_DIR}/assets/locker.ico'
    COLOR = f'{CURRENT_DIR}/assets/theme.json'
    
    CAMERA = 0
    SAMPLES = 5
    TOLERANCE = 0.5
    MODEL = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    if not os.path.exists(r'./DATA'): os.makedirs(r'./DATA')
    if not os.path.exists(r'./DATA/DATABASE'): os.makedirs(r'./DATA/DATABASE')
    if not os.path.exists(r'./DATA/SAMPLES'): os.makedirs(r'./DATA/SAMPLES')
    
#-------------------------------------- Windows color settings ----------------------------------------
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme(Settings.COLOR)

class WindowSettings:    
    def changeAppearance(self, new_appearance_mode : str):
        customtkinter.set_appearance_mode(new_appearance_mode)
        sv_ttk.set_theme(new_appearance_mode)
        self.changeTablestyle()

    def changeTablestyle(self):
        style = ttk.Style()
        style.configure("Treeview", font=("", 12), rowheight=30)
        style.configure("Treeview.Heading", font=("", 13, "bold"))

#-------------------------------------------- Database class  ------------------------------------------
class DatabaseManager:
    def __init__(self):
        self.connection = sqlite3.connect("./" + "/DATA/" + "/DATABASE/" +"/locker.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.cursor = self.connection.cursor()
        self.create_tables()
    
    def create_tables(self):        
        TABLES = {
            "Small":"""
                CREATE TABLE IF NOT EXISTS Small (
                Partitions VARCHAR(5),
                Locker_Count VARCHAR(5),
                deposite VARCHAR(10),
                rent VARCHAR(10)
                )""",
            
            "Medium":"""
                CREATE TABLE IF NOT EXISTS Medium (
                Partitions VARCHAR(5),
                Locker_Count VARCHAR(5),
                deposite VARCHAR(10),
                rent VARCHAR(10)
                )""",
            
            "Large":"""
                CREATE TABLE IF NOT EXISTS Large (
                Partitions VARCHAR(5),
                Locker_Count VARCHAR(5),
                deposite VARCHAR(10),
                rent VARCHAR(10)
                )""",
            
            "Name":""" 
                CREATE TABLE IF NOT EXISTS Name (
                Locker_No VARCHAR(5),
                Locker_Size VARCHAR(50) NOT NULL,
                Locker_Type VARCHAR(50) NOT NULL,
                First_Name VARCHAR(50) NOT NULL,
                Middle_Name VARCHAR(50),
                Last_Name VARCHAR(50) NOT NULL,
                Date DATE NOT NULL
            );
            """,
            
            "Address": """
                    CREATE TABLE IF NOT EXISTS Address (
                    Locker_No VARCHAR(5),
                    Locker_Size VARCHAR(50) NOT NULL,
                    Line1 VARCHAR(255) NOT NULL,
                    Line2 VARCHAR(255),
                    City VARCHAR(100) NOT NULL,
                    Dist VARCHAR(100) NOT NULL,
                    Tal VARCHAR(100) NOT NULL,
                    State VARCHAR(100) NOT NULL,
                    Country VARCHAR(100) NOT NULL,
                    Pin INT NOT NULL,
                    FOREIGN KEY (Locker_No) REFERENCES Name(Locker_No) ON DELETE CASCADE
                );
            """,
            
            "KYC": """
                    CREATE TABLE IF NOT EXISTS KYC (
                    Locker_No VARCHAR(5),                    
                    Locker_Size VARCHAR(50) NOT NULL,
                    Adhaar BIGINT UNIQUE NOT NULL,
                    PAN VARCHAR(10) UNIQUE NOT NULL,
                    FOREIGN KEY (Locker_No) REFERENCES Name(Locker_No) ON DELETE CASCADE
                );
            """,
            
            "Permissions": """
                    CREATE TABLE IF NOT EXISTS Permissions (
                    Locker_No VARCHAR(5),
                    Locker_Size VARCHAR(50) NOT NULL,
                    Nominee_1 VARCHAR(100) DEFAULT NULL,
                    Nominee_2 VARCHAR(100) DEFAULT NULL,
                    Nominee_3 VARCHAR(100) DEFAULT NULL,
                    Nominee_4 VARCHAR(100) DEFAULT NULL,
                    Nominee_5 VARCHAR(100) DEFAULT NULL,
                    FOREIGN KEY (Locker_No) REFERENCES Name(Locker_No) ON DELETE CASCADE
                );
            """,
            
            "Visitors": """
                    CREATE TABLE IF NOT EXISTS Visitors (
                    Visitor_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Locker_No VARCHAR(5) NOT NULL,
                    Locker_Size VARCHAR(50) NOT NULL,
                    Visitor_Name VARCHAR(255) NOT NULL,
                    Date DATE NOT NULL,
                    Entry_Time TIME NOT NULL,
                    Exit_Time TIME,
                    FOREIGN KEY (Locker_No) REFERENCES Name(Locker_No) ON DELETE CASCADE
                );""",
                
            "OldLockers":"""
                    CREATE TABLE IF NOT EXISTS OldLockers (
                        Locker_No VARCHAR(5),
                        Locker_Size VARCHAR(50) NOT NULL,
                        Locker_Type VARCHAR(50) NOT NULL,
                        Name VARCHAR(255) NOT NULL,
                        Occipied_Date DATE NOT NULL,
                        Release_Date DATE NOT NULL,
                        Address VARCHAR(255),
                        Adhaar BIGINT UNIQUE NOT NULL,
                        PAN VARCHAR(10) UNIQUE NOT NULL,
                        Nominee_1 VARCHAR(100) DEFAULT NULL,
                        Nominee_2 VARCHAR(100) DEFAULT NULL,
                        Nominee_3 VARCHAR(100) DEFAULT NULL,
                        Nominee_4 VARCHAR(100) DEFAULT NULL,
                        Nominee_5 VARCHAR(100) DEFAULT NULL);""",
        }
        
        for table_name, query in TABLES.items(): self.cursor.execute(query)
        self.connection.commit()
    
    def add_data(self, entries):
        date = datetime.date.today().strftime("%Y-%m-%d")
        queries = {"Name":
                            f"""INSERT INTO Name VALUES (
                                "{entries["Locker No"]}", 
                                '{entries["Locker Size"]}',
                                '{entries["Locker Type"]}',
                                '{entries["First Name"]}', 
                                '{entries["Middle Name"]}', 
                                '{entries["Last Name"]}',
                                '{date}');""",
                                
                        "Address":
                        f"""INSERT INTO Address VALUES (
                            "{entries["Locker No"]}", 
                            '{entries["Locker Size"]}',
                            '{entries["Address Line 1"]}', 
                            '{entries["Address Line 2"]}', 
                            '{entries["City"]}', 
                            '{entries["District"]}', 
                            '{entries["Taluka"]}', 
                            '{entries["State"]}', 
                            '{entries["Country"]}', 
                            {entries["Pincode"]});""",
                        
                        "KYC":
                        f"""INSERT INTO KYC VALUES (
                            "{entries["Locker No"]}",
                            '{entries["Locker Size"]}', 
                            {entries["Aadhaar ID"]}, 
                            '{entries["PAN ID"]}');""",
                        
                        "Permissions":
                        f"""INSERT INTO Permissions VALUES (
                            "{entries["Locker No"]}", 
                            '{entries["Locker Size"]}',
                            '{entries["Nominee 1"]}', 
                            '{entries["Nominee 2"]}', 
                            '{entries["Nominee 3"]}', 
                            '{entries["Nominee 4"]}', 
                            '{entries["Nominee 5"]}');"""}
        
        for table_name, query in queries.items():
            self.cursor.execute(query)    
            self.connection.commit()

    def update_data(self, entries):
        tables = {"Name" : {"First Name" : "First_Name", "Middle Name" : "Middle_Name", "Last Name" : "Last_Name"},
                        "Address" : {"Address Line 1" : "Line1", "Address Line 2" : "Line2", "Country" : "Country", "State" : "State", "District" : "Dist", "Taluka" : "Tal", "City" : "City", "Pincode" : "Pin"},
                        "KYC" : {"Aadhaar ID" : "Adhaar", "PAN ID" : "PAN"},
                        "Permissions" : {"Nominee 1" : "Nominee_1", "Nominee 2" : "Nominee_2", "Nominee 3" : "Nominee_3", "Nominee 4" : "Nominee_4", "Nominee 5" : "Nominee_5"}}
        
        for column, new_data in entries.items():
            if column not in ["Locker No", "Locker Size", "Locker Type"]: 
                for table_name, attributes in tables.items():
                    if column in attributes:
                        query = f"UPDATE {table_name} SET {attributes[column]} = ? WHERE Locker_No = ? AND Locker_Size = ?"
                        self.cursor.execute(query, (new_data, entries['Locker No'], entries["Locker Size"]))
        self.connection.commit()

    def get_occupied_details(self, locker_no=None, locker_size=None):
        details = {"Locker No" : [], "Locker Size":[], "Locker Type" : [], "Registration Date" : [], "Occupied By" : [], "Address" : [], "Addhaar ID": [], "PAN ID": [], "Nominee 1" : [], 
                   "Nominee 2" : [], "Nominee 3" : [], "Nominee 4" : [], "Nominee 5" : []}
        
        if locker_no and locker_size: self.cursor.execute("""SELECT * FROM Name, Address, KYC, Permissions WHERE Name.Locker_No = ? AND Name.Locker_Size = ? 
                                                          AND Address.Locker_No = ? AND Address.Locker_Size = ? AND KYC.Locker_No = ? AND KYC.Locker_Size = ? 
                                                          AND Permissions.Locker_No = ? AND Permissions.Locker_Size = ?""", (str(locker_no), locker_size, str(locker_no), locker_size, str(locker_no), locker_size, str(locker_no), locker_size))
        
        else: self.cursor.execute("""SELECT * FROM Name, Address, KYC, Permissions WHERE Name.Locker_No = Address.Locker_No AND Name.Locker_No = KYC.Locker_No AND Name.Locker_No = Permissions.Locker_No
                                  AND Name.Locker_Size = Address.Locker_Size AND Name.Locker_Size = KYC.Locker_Size AND Name.Locker_Size = Permissions.Locker_Size""")
        all_data = self.cursor.fetchall()
        self.connection.commit()
        
        for data in all_data:
            name = f'{data[3]} {data[4]} {data[5]}'
            address = f'{data[9]}, {data[10]}, {data[11]}, {data[12]}, {data[13]}, {data[14]}, {data[15]}, {data[16]}'
            
            details["Locker No"].append(data[0])
            details["Locker Size"].append(data[1])
            details["Locker Type"].append(data[2])
            details["Registration Date"].append(data[6])
            details["Occupied By"].append(name)
            details["Address"].append(address)
            details["Addhaar ID"].append(data[19])
            details["PAN ID"].append(data[20])
            details["Nominee 1"].append(data[23])
            details["Nominee 2"].append(data[24])
            details["Nominee 3"].append(data[25])
            details["Nominee 4"].append(data[26])
            details["Nominee 5"].append(data[27])
        return details        
    
    def get_occupied_lockers(self):
        query = """SELECT * from Name;"""
        self.cursor.execute(query)
        lockers = self.cursor.fetchall()
        self.connection.commit()
        return lockers
    
    def get_locker_owners(self):
        query = """SELECT * from Permissions;"""
        self.cursor.execute(query)
        temp_lockers = self.cursor.fetchall()
        self.connection.commit()
        
        lockers = []
        occupied_size = {}

        for rows in self.get_occupied_lockers():
            occupied_size[rows[0]] = rows[1]
            lockers.append(rows[0 : 6])

        for rows in temp_lockers:
            temp = ()
            locker_num = rows[0]
            locker_size = rows[1]
            
            for data in rows[2:]:
                temp += (locker_num, locker_size, "")
                if data.lower() not in ["na", ""]:
                    temp += tuple(data.split(" "), )
                    lockers.append(temp)
                temp = ()
        return lockers

    def set_lockers(self, lockers):
        try:
            [self.dropper(table) for table in ["Small", "Medium", "Large"] ].clear()
        except Exception:
            pass
        self.create_tables()
        
        for locker_size, locker in lockers.items():
            if locker[0] == "NA":
                self.cursor.execute(f"INSERT INTO {locker_size} VALUES ('{locker[0]}', '{locker[1]}', '{locker[2]}', '{locker[3]}')")
            else:
                for index in range (len(locker[0])):
                    self.cursor.execute(f"INSERT INTO {locker_size} VALUES ('{locker[0][index]}', '{locker[1][index]}', '{locker[2]}', '{locker[3]}')")
        self.connection.commit()
    
    def get_depo_rent(self, locker_size):
        self.cursor.execute(f"SELECT deposite, rent from {locker_size}")
        data = self.cursor.fetchall()
        self.connection.commit()
        return data

    def get_rent_details(self):
        self.cursor.execute("SELECT Locker_No, Locker_Size, First_Name, Middle_Name, Last_Name, Date from Name WHERE Locker_Type = 'Rent'")
        data = self.cursor.fetchall()
        self.connection.commit()
        return data
    
    def get_lockers(self):
        var = ["Small", "Medium", "Large"]
        lockers = {}
        temp = {}
        for locker_size in var:
            self.cursor.execute(f"SELECT * FROM {locker_size}")
            temp[locker_size] = self.cursor.fetchall()
        self.connection.commit()
        
        for types, locker in temp.items():
            partitions = []
            counts = []
            for (partition, count, depo, rent) in locker:
                if partition != "NA":
                    partitions.append(partition)
                counts.append(count)
            if partitions:
                lockers[types] = [partitions, counts]
            else:
                lockers[types] = counts
            
        temp.clear()
        return lockers
    
    def set_visitors(self, locker_no, locker_size=None, visitor=None, entry_time=None, exit_time=None):
        if locker_no and entry_time and not exit_time:
            query = """
                INSERT INTO Visitors (Locker_No, Locker_Size, Visitor_Name, Date, Entry_Time)
                VALUES (?, ?, ?, ?, ?)
            """
            date_today = datetime.date.today().strftime("%Y-%m-%d")
            time_entry = entry_time.strftime("%H:%M:%S") if isinstance(entry_time, datetime.datetime) else entry_time
            self.cursor.execute(query, (str(locker_no), locker_size, visitor, date_today, time_entry))
        else:
            query = """
                UPDATE Visitors
                SET Exit_Time = ?
                WHERE Locker_No = ? AND Exit_Time IS NULL
            """
            time_exit = exit_time.strftime("%H:%M:%S") if isinstance(exit_time, datetime.datetime) else exit_time
            self.cursor.execute(query, (time_exit, str(locker_no)))
        self.connection.commit()
    
    def get_visitors(self):
        date = datetime.date.today().strftime("%Y-%m-%d")
        self.cursor.execute("SELECT Locker_Size, Locker_No, VIsitor_Name, Entry_Time, Exit_Time FROM Visitors WHERE Date == ?", (date,))
        data = self.cursor.fetchall()
        self.connection.commit()
        return data

    def get_visitors_details(self):
        details = {"Sr No" : [], "Locker No" : [], "Locker Size" : [], "Visitor Name" : [], "Date" : [], "Entry Time": [], "Exit Time": []}
        self.cursor.execute("SELECT * FROM Visitors")
        all_data = self.cursor.fetchall()
        self.connection.commit()
        
        for data in all_data:
            for index, (column_title, _) in enumerate(details.items()):
                details[column_title].append(data[index])
        return details
        
    def releaseLocker(self, locker_num, locker_size):
        self.cursor.execute("SELECT * FROM Name, Address, KYC, Permissions WHERE Name.Locker_No = ? AND Name.Locker_Size = ?", (str(locker_num), locker_size))
        data = self.cursor.fetchall()[0]
        self.connection.commit()
        name = f'{data[3]} {data[4]} {data[5]}'
        address = f'{data[9]}, {data[10]}, {data[11]}, {data[12]}, {data[13]}, {data[14]}, {data[15]}, {data[16]}'
        date = datetime.date.today().strftime("%Y-%m-%d")
        
        self.cursor.execute(f"INSERT INTO OldLockers VALUES ('{str(data[0])}', '{data[1]}', '{data[2]}', '{name}', '{data[6]}', '{date}', '{address}', '{data[19]}', '{data[20]}', '{data[23]}', '{data[24]}', '{data[25]}', '{data[26]}', '{data[27]}')")
        self.connection.commit()
        
        self.cursor.execute(f"DELETE FROM Name WHERE Locker_No = {str(locker_num)} AND Locker_Size = '{locker_size}'")
        self.cursor.execute(f"DELETE FROM Address WHERE Locker_No = { str(locker_num)} AND Locker_Size = '{locker_size}'")
        self.cursor.execute(f"DELETE FROM KYC WHERE Locker_No = {str(locker_num)} AND Locker_Size = '{locker_size}'")
        self.cursor.execute(f"DELETE FROM Permissions WHERE Locker_No = {str(locker_num)} AND Locker_Size = '{locker_size}'")
        self.connection.commit()
        
    def get_old_customer_details(self):
        details = {"Locker No" : [], "Locker Size" : [],"Locker Type" : [], "Occupied By" : [], "Occupied On" : [], "Released On":[], "Address" : [], "Addhaar ID": [], "PAN ID": [], "Nominee 1" : [], 
                   "Nominee 2" : [], "Nominee 3" : [], "Nominee 4" : [], "Nominee 5" : []}
        
        self.cursor.execute("SELECT * FROM OldLockers")
        all_data = self.cursor.fetchall()
        self.connection.commit()
        
        for data in all_data:
            for index, (column_title, _) in enumerate(details.items()):
                details[column_title].append(data[index])
        return details
    
    def dropper(self, table_name):
        query = f"DROP TABLE {table_name};"
        self.cursor.execute(query)
        self.connection.commit()

#--------------------------------------- District and Tal Database --------------------------------------
class DistDatabase:
    def __init__(self):
        self.connection = sqlite3.connect(Settings.CURRENT_DIR + "/assets/" + "/citydata.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.cursor = self.connection.cursor()
    
    def getDistricts(self):
        self.cursor.execute("SELECT District FROM talukas")
        districts = set()
        for dist in self.cursor.fetchall():
            districts.add(dist[0])
        self.connection.commit()
        return list(districts)
        
    def getTalukas(self):
        self.cursor.execute("SELECT Taluka FROM talukas")
        tals = set()
        for dist in self.cursor.fetchall(): tals.add(dist[0])
        self.connection.commit()
        return list(tals)
        
    def getCities(self):
        self.cursor.execute("SELECT City FROM cities")
        cities = set()
        for dist in self.cursor.fetchall(): cities.add(dist[0])
        self.connection.commit()
        return list(cities)
    
    def getPincode(self):
        self.cursor.execute("SELECT Pincode FROM cities")
        pincode = set()
        for code in self.cursor.fetchall(): pincode.add(str(code[0]))
        self.connection.commit()
        return list(pincode)

#--------------------------------------- Recognizations classes  ---------------------------------------
class Datasets(Settings):
    def __init__(self):
        self.location = "./" + "/DATA/" + "/SAMPLES/"
        self.FACESKNOW, self.NAMESKNOW = self.Get_Images()
    
    def Get_Images(self):
        FACESKNOW, NAMESKNOW  = [], []
        if not os.path.exists(self.location): os.makedirs(self.location)
        for person in os.listdir(self.location):
            person_path = os.path.join(self.location, person)
            
            if not os.path.isdir(person_path): continue
            for image_file in os.listdir(person_path):
                image_path = os.path.join(person_path, image_file)
                try:
                    img = face_recognition.load_image_file(image_path)
                    encodings = face_recognition.face_encodings(np.array(img))
                    if encodings:  
                        FACESKNOW.append(encodings[0])  
                        NAMESKNOW.append(person)
                except Exception as _: pass
        return FACESKNOW, NAMESKNOW
        
    def Store_samples(self, person):
        person_path = os.path.join(self.location, person)
        os.makedirs(person_path, exist_ok=True) 
        return person_path
        
    def Recognize(self, image):
        image = np.array(image)
        if not self.FACESKNOW: return "No faces registered"

        locations = face_recognition.face_locations(image, model="hog")  
        encodings = face_recognition.face_encodings(image, locations)

        for face_encoding in encodings:
            distances = face_recognition.face_distance(self.FACESKNOW, face_encoding)
            best_match_index = np.argmin(distances)
            if distances[best_match_index] < self.TOLERANCE: return self.NAMESKNOW[best_match_index]  
        return "Unknown"

#------------------------------------- Detecting and storing faces --------------------------------------
class DetectionFrame(customtkinter.CTkToplevel):
    def __init__(self, person):
        super().__init__()

        self.person = person
        self.title(Settings.TITLE)
        self.iconbitmap(Settings.ICON)
        self.after(1000, self.state, "zoomed")
        self.after(250, lambda: self.iconbitmap(Settings.ICON))

        self.checking = False
        self.camera_running = False
        self.counter = 0
        self.latest_frame = None

        self.label_frame = customtkinter.CTkFrame(self, corner_radius=20)
        self.label_frame.pack(pady=40)

        self.label = customtkinter.CTkLabel(self.label_frame, text="", width=800, height=600)
        self.label.pack(pady=10)

        self.note = customtkinter.CTkLabel(self, text=f"Capturing images for {person}", font=("Arial", 28, "bold"))
        self.note.pack(pady=20)

        self.status = customtkinter.CTkLabel(self, text="", font=("Arial", 26))
        self.status.pack(pady=20)

        self.button = customtkinter.CTkButton(self, text="🎥 Start Capturing", font=("Arial", 22, "bold"),
                                              width=300, height=50, command=self.toggle_camera)
        self.button.pack(pady=10)

        self.protocol("WM_DELETE_WINDOW", self.close_window)

    def toggle_camera(self):
        if self.camera_running:
            self.stop_camera()
        else:
            self.start_camera()

    def start_camera(self):
        self.camera = cv2.VideoCapture(Settings.CAMERA)
        self.camera.set(cv2.CAP_PROP_FPS, 60)
        self.camera_running = True
        self.button.configure(text="⏹ Stop")
        self.status.configure(text="Starting camera... Wait a while")

        self.thread = threading.Thread(target=self.wait_and_enable_capture, daemon=True)
        self.thread.start()
        self.update_frame()

    def wait_and_enable_capture(self):
        threading.Event().wait(5)
        self.checking = True
        self.status.configure(text="Capturing face samples...")
        self.face_thread = threading.Thread(target=self.process_faces_in_background, daemon=True)
        self.face_thread.start()

    def stop_camera(self):
        self.camera_running = False
        self.checking = False
        self.counter = 0
        self.label.configure(image=None)
        self.status.configure(text="Camera stopped.")
        self.button.configure(text="🎥 Start Capturing")
        if hasattr(self, "camera"):
            self.camera.release()
        cv2.destroyAllWindows()

    def update_frame(self):
        if not self.camera_running: return

        ret, frame = self.camera.read()
        if not ret: return

        self.latest_frame = frame.copy()

        display_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

        # Remove black border
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        x, y, w, h = cv2.boundingRect(thresh)
        display_frame = display_frame[y:y + (h - 10), x:x + w]
        
        img = Image.fromarray(display_frame)
        img = img.resize((800, 600))

        mask = Image.new("L", (800, 600), 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, 800, 600), fill=255, radius=20)

        img.putalpha(mask)
        photo = customtkinter.CTkImage(light_image=img, size=(800, 600))
        self.label.configure(image=photo)

        if self.camera_running:
            self.after(10, self.update_frame)

    def process_faces_in_background(self):
        save_path = Datasets().Store_samples(self.person)
        while self.camera_running and self.checking and self.counter < Settings.SAMPLES:
            if self.latest_frame is None: continue

            frame = self.latest_frame
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = Settings.MODEL.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                if self.counter >= Settings.SAMPLES: break
                face = gray[y:y + h, x:x + w]
                self.counter += 1
                cv2.imwrite(f"{save_path}/{self.counter}.jpg", face)
            cv2.waitKey(50)

        self.status.configure(text="Images stored successfully.")
        self.camera_running = False
        self.checking = False
        self.counter = 0
        self.label.configure(image=None)
        self.button.configure(text="🎥 Capturing Again")
        if hasattr(self, "camera"):
            self.camera.release()
        cv2.destroyAllWindows()

    def close_window(self):
        self.stop_camera()
        self.destroy()

#-------------------------------------- Custom Combobox design -------------------------------------        
class SearchableComboBox:
    def __init__(self, main_master, master, placeholder, options, width=200):
        self.options = options
        self.flag = False

        self.frame = customtkinter.CTkFrame(master, fg_color="transparent", corner_radius=10)
        self.entry = customtkinter.CTkEntry(self.frame, placeholder_text=placeholder, width=width - 35, corner_radius=10)
        self.entry.pack(side=tkinter.LEFT, padx=(0, 5))
        self.entry.bind("<KeyRelease>", self.on_entry_key)
        self.entry.bind("<FocusIn>", self.show_dropdown)

        self.button = customtkinter.CTkButton(self.frame, text="▼", width=30, command=self.show_dropdown, corner_radius=10)
        self.button.pack(side=tkinter.LEFT)

        self.textbox = customtkinter.CTkTextbox(main_master, height=80, width=width, corner_radius=5)
        self.textbox.bind("<Button-1>", self.on_textbox_click)
        self.populate_textbox(self.options)

    def populate_textbox(self, options):
        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", tkinter.END)
        for option in options:
            self.textbox.insert(tkinter.END, option + "\n")
        self.textbox.configure(state="disabled")

    def on_entry_key(self, event):
        typed_value = self.entry.get().strip().lower()
        filtered = [opt for opt in self.options if opt.lower().startswith(typed_value)]
        self.populate_textbox(filtered)
        self.show_dropdown()

    def on_textbox_click(self, event):
        index = self.textbox.index(f"@{event.x},{event.y}")
        line = index.split('.')[0]
        selected = self.textbox.get(f"{line}.0", f"{line}.end").strip()
        if selected:
            self.entry.delete(0, tkinter.END)
            self.entry.insert(0, selected)
        self.hide_dropdown()

    def show_dropdown(self, event=None):
        self.textbox.place(in_=self.entry, x=0, rely=1, relwidth=1.0, anchor="nw")
        self.textbox.lift()
        if self.flag == True: self.hide_dropdown()
        else: self.flag = True

    def hide_dropdown(self):
        self.flag = False
        self.textbox.place_forget()

    def get(self):
        return self.entry.get()

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def place(self, **kwargs):
        self.frame.place(**kwargs)

#-------------------------------------------- Form to get data -----------------------------------------    
class MainForm:
    def updatemsg(self, msg, locker_size, locker_type):
        Deposite, Rent = DatabaseManager().get_depo_rent(locker_size)[0]
        data = {"Deposite":Deposite, "Rent":Rent}
        msg.configure(text=f"For {locker_size} Locker {locker_type} : {data[locker_type]}")
    
    def Set_data(self, locker_number, locker_size, data=None):
        self.entry_vars = {"Locker No" : f'{locker_number}', "Locker Size" : locker_size}

        # New Window
        newCTk = customtkinter.CTkToplevel()
        newCTk.title(f"{Settings.TITLE} - Saving Data for Locker {locker_number}")
        newCTk.after(250, lambda : newCTk.iconbitmap(Settings.ICON))
        newCTk.after(500, lambda: newCTk.state("zoomed"))
        
        #Open at top
        newCTk.focus()
        newCTk.grab_set()
        newCTk.lift()
        newCTk.attributes('-topmost', True)
        newCTk.after(10, lambda: newCTk.attributes('-topmost', False))

        newCTk.grid_columnconfigure((1), weight=0)
        newCTk.grid_columnconfigure((0, 2), weight=1)
        
        # Label and Entry Creator
        def create_label_entry(parent, text, row, column=0, width=750, values=[], main=None, placeholder=None):
            label = customtkinter.CTkLabel(parent, text=text, font=("Arial", 14, "bold"))
            label.grid(row=row, column=column, padx=(20, 5), pady=(0, 20), sticky="wns")

            if text in ["Country:", "State:", "District:", "Taluka:", "City:", "Pincode:"]:
                entry = SearchableComboBox(main, parent, placeholder=placeholder, options=values, width=width)
                entry.grid(row=row, column=column + 1, padx=(5, 1), pady=(0, 20), sticky="wns")
                
            elif text == "Locker Type:":
                entry = customtkinter.CTkOptionMenu(parent, values=values, width=width, corner_radius=5)
                entry.grid(row=row, column=column + 1, padx=(5, 1), pady=(0, 20), sticky="wns")
                msg = customtkinter.CTkLabel(parent, text="", font=("", 18, "bold"))
                msg.grid(row=row, column=column+2, padx=(75,1), pady=(0, 20), sticky="e")
                
                self.updatemsg(msg, locker_size, data[2][0] if data else "Deposite")
                entry.configure(command=lambda locker_type=entry.get() : self.updatemsg(msg, locker_size, locker_type))
                    
            elif text in ["Address Line 1:", "Address Line 2:"]: 
                entry = customtkinter.CTkEntry(parent, placeholder_text=placeholder, width=width, corner_radius=5)
                entry.grid(row=row, column=column + 1, columnspan=6, padx=(5, 20), pady=(0, 20), sticky="wns")
            else:
                entry = customtkinter.CTkEntry(parent, placeholder_text=placeholder, width=width, corner_radius=5)
                entry.grid(row=row, column=column + 1, padx=(5, 20), pady=(0, 20), sticky="wns")
                
            self.entry_vars[text.strip(":")] = entry

        # Section Frames
        def section_frame(title, master, row_idx):
            frame = customtkinter.CTkFrame(master, corner_radius=10)
            frame.grid(row=row_idx, column=1, pady=20, padx=10, sticky="ew")
            
            customtkinter.CTkLabel(frame, text=title, font=("Arial", 25, "bold")).grid(
                row=0, column=0, pady=(20, 40), columnspan=2, padx=(30,1), sticky="nw")
            return frame
        
        # Scrollable Frame
        scroll_frame = customtkinter.CTkScrollableFrame(master=newCTk, label_text="New Locker Form", 
                                                        fg_color="transparent", label_font=("Calibri", 30, "bold"), width=1280, height=850)
        scroll_frame.grid(row=0, column=1, padx=20, pady=20)
        scroll_frame.grid_columnconfigure((0, 2), weight=1)
        scroll_frame.grid_columnconfigure((1), weight=0)

        main_frame = customtkinter.CTkFrame(scroll_frame)
        main_frame.grid(row=0, column=1, padx=20, pady=(40))

        # Save Button Action
        def set_details():
            entries = {}
            for key, var in self.entry_vars.items():
                if key == "Locker No" or key == "Locker Size": entries[key] = var
                elif var.get() == "" and not data: entries[key] = "NA"
                elif var.get() == "" and data: continue  
                else: entries[key] = var.get()
            
            if data: DatabaseManager().update_data(entries)
            else: DatabaseManager().add_data(entries)
            messagebox.showinfo("Success", "Locker Details Updated." if data else "Locker Details Saved.")
            newCTk.destroy()
            
            if data:
                peoples = []
                for i in range (1, 6): 
                    try: peoples.append(entries[f'Nominee {i}'])
                    except: pass
                for Nominee in peoples: 
                    if Nominee not in ["NA", ""]: 
                        messagebox.showinfo("Capture Image", f"Please capture images for Facial Recognition Process of {Nominee}")
                        DetectionFrame(Nominee).wait_window()
            else:
                peoples = [f'{entries["First Name"]} {entries["Middle Name"]} {entries["Last Name"]}']
                for i in range (1, 6): peoples.append(entries[f'Nominee {i}'])
                for Nominee in peoples: 
                    if Nominee not in ["NA", ""]: 
                        messagebox.showinfo("Capture Image", f"Please capture images for Facial Recognition Process of {Nominee}")
                        DetectionFrame(Nominee).wait_window()
            self.entry_vars.clear(); entries.clear()

        customtkinter.CTkButton(newCTk, text="Save", width=150, height=50,font=("Calibri", 20, "bold"), command=set_details).grid(row=1, column=1, padx=20, pady=20)

        locker_type = section_frame("Locker Information", main_frame, 1)
        create_label_entry(locker_type, "Locker Type:", 1, 0, width=300, main=main_frame, values=data[2] if data else ["Deposite", "Rent"])
        
        basic_info = section_frame("Basic Information", main_frame, 2)
        create_label_entry(basic_info, "First Name:", 1, 0, 175, placeholder=data[4][0].split()[0] if data else "")
        create_label_entry(basic_info, "Middle Name:", 1, 2, 175, placeholder=data[4][0].split()[1] if data else "")
        create_label_entry(basic_info, "Last Name:", 1, 4, 175, placeholder=data[4][0].split()[2] if data else "")

        address = section_frame("Address", main_frame, 3)
        create_label_entry(address, "Address Line 1:", 1, placeholder=data[5][0].split(",")[0] if data else "")
        create_label_entry(address, "Address Line 2:", 2, placeholder=data[5][0].split(",")[1] if data else "")
        create_label_entry(address, "Country:", 3, 0, width=175, main=main_frame ,placeholder=data[5][0].split(",")[6] if data else "", values=["India"])
        create_label_entry(address, "State:", 3, 2, width=175, main=main_frame, placeholder=data[5][0].split(",")[5] if data else "", values=["Maharastra"])
        create_label_entry(address, "District:", 3, 4, width=175, main=main_frame, placeholder=data[5][0].split(",")[3] if data else "", values=DistDatabase().getDistricts())
        create_label_entry(address, "Taluka:", 4, 0, width=175, main=main_frame, placeholder=data[5][0].split(",")[4] if data else "", values=DistDatabase().getTalukas())
        create_label_entry(address, "City:", 4, 2, width=175, main=main_frame, placeholder=data[5][0].split(",")[2] if data else "", values=DistDatabase().getCities())
        create_label_entry(address, "Pincode:", 4, 4, width=175, main=main_frame, placeholder=data[5][0].split(",")[7] if data else "", values=DistDatabase().getPincode())

        kyc = section_frame("KYC Details", main_frame, 4)
        create_label_entry(kyc, "Aadhaar ID:", 1, column=0, width=330, placeholder=data[6][0] if data else "")
        create_label_entry(kyc, "PAN ID:", 1, column=2, width=330, placeholder=data[7][0] if data else "")

        permission = section_frame("Nominees", main_frame, 5)
        for i in range(1, 6):
            create_label_entry(permission, f"Nominee {i}:", i, placeholder=data[i+7][0] if data and data[i+7][0]!="NA" else "\t\t First Name \t\t\t Middle Name \t\t\t Last Name")

#------------------------------------ Getting Lockers Types and count ---------------------------------
class LockerManager(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        
        self.title(Settings.TITLE)
        self.geometry("550x700")
        self.resizable(False, False)
        self.after(250, lambda : self.iconbitmap(Settings.ICON))
        
        #Open at top
        self.focus()
        self.grab_set()
        self.lift()
        self.attributes('-topmost', True)
        self.after(10, lambda: self.attributes('-topmost', False))
        
        self.all_lockers = {"Small" : [], "Medium": [], "Large": []}

        self.tab_frame = customtkinter.CTkFrame(self, width=120, corner_radius=10)
        self.content_frame = customtkinter.CTkFrame(self, corner_radius=10)
        self.save_button = customtkinter.CTkButton(self, text="Save", font=("Calibri", 18, "bold"), width=125, height=40, corner_radius=10, state="disabled", command=self.add_lockers_to_db)
        
        self.tab_frame.grid(row=0, column=0, padx=10, pady=10, rowspan=2, sticky="nsew")
        self.content_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nesw")
        self.save_button.grid(row=1, column=1, pady=(40, 20))

        self.tabs = {}
        for label in ["Small", "Medium", "Large"]:
            btn = customtkinter.CTkButton(self.tab_frame, text=label, command=lambda l=label: self.show_tab(l), height=30)
            btn.pack(pady=(40, 5), padx=10, fill="x")
            self.tabs[label] = self.create_tab_frame(label)
        self.show_tab("Small")
    
    def add_lockers_to_db(self):
        lockers_buttons = {"Small": [], "Medium": [], "Large": []}
        for types, values in self.all_lockers.items():
            if self.all_lockers[types][0] != "NA":
                partition_count = int(self.all_lockers[types][0])
                partition_var = [chr(i+65) for i in range (partition_count)]
            else: partition_var = "NA"
            lockers_buttons[types] = [partition_var, values[1], values[2], values[3]]
            
        self.destroy()
        DatabaseManager().set_lockers(lockers_buttons)

    def create_tab_frame(self, label):
        frame = customtkinter.CTkFrame(self.content_frame, corner_radius=10)
        partition_values = [str(i) for i in range(2, 11)]
        partition_values.insert(0, "NA")

        partition_label = customtkinter.CTkLabel(frame, text="Add partitions : ")
        partition_dropdown = customtkinter.CTkOptionMenu(frame, values=partition_values)
        combo_frame = customtkinter.CTkFrame(frame, corner_radius=0, fg_color="transparent", bg_color="transparent", border_width=0)
        
        partition_label.grid(row=1, column=0, padx=(30, 5), pady=(20, 10), sticky="w")
        partition_dropdown.grid(row=1, column=1, padx=10, pady=(20, 10), sticky="we")
        combo_frame.grid(row=2, column=0, columnspan=2, pady=10, padx=10, sticky="w")
        
        deposite_label = customtkinter.CTkLabel(frame, text="Deposits Amount : ")
        rent_label = customtkinter.CTkLabel(frame, text="Rent Amount : ")
        deposite = customtkinter.CTkEntry(frame, placeholder_text="Deposite Amount", corner_radius=10)
        rent = customtkinter.CTkEntry(frame, placeholder_text="Rent Amount", corner_radius=10)
        
        deposite_label.grid(row=3, column=0, padx=(30, 5), pady=10, sticky="w")
        rent_label.grid(row=4, column=0, padx=(30, 5), pady=10, sticky="w")
        deposite.grid(row=3, column=1, padx=10, pady=10, sticky="we")
        rent.grid(row=4, column=1, padx=10, pady=10, sticky="we")
        
        combo_boxes = []
        def update_locker_combos(choice):
            for widget in combo_frame.winfo_children(): widget.destroy()
            combo_boxes.clear()

            if choice == "NA":
                lbl = customtkinter.CTkLabel(combo_frame, text="Total Lockers :")
                lbl.grid(row=0, column=0, padx=(20, 40), pady=10, sticky="w")
                combo = customtkinter.CTkComboBox(combo_frame, values=[str(x) for x in range(1, 101)], corner_radius=10)
                combo.grid(row=0, column=1, padx=5, pady=5)
                combo_boxes.append(combo)
            else:
                count = int(choice)
                for i in range(count):
                    part = chr(65 + i)
                    lbl = customtkinter.CTkLabel(combo_frame, text=f"Total Lockers for {part} :")
                    lbl.grid(row=i, column=0, padx=(20, 5), pady=5, sticky="e")
                    combo = customtkinter.CTkComboBox(combo_frame, values=[str(x) for x in range(1, 101)])
                    combo.grid(row=i, column=1, padx=5, pady=5)
                    combo_boxes.append(combo)

        partition_dropdown.configure(command=update_locker_combos)
        partition_dropdown.set("NA")  # Set default
        update_locker_combos("NA")  # Show 1 combo by default
        
        def add_data():
            selected_partition = partition_dropdown.get()
            values = [combo.get() for combo in combo_boxes]
            
            if selected_partition == "NA": self.all_lockers[label] = ["NA", values[0], deposite.get(), rent.get()]
            else: self.all_lockers[label] = [selected_partition, values, deposite.get(), rent.get()]
            
            complete = True
            for v in self.all_lockers.values():
                if not v or (v[0] != "NA" and (not isinstance(v[1], list) or len(v[1]) != int(v[0]))):
                    complete = False ; break
            self.save_button.configure(state="normal" if complete else "disabled")

        set_button = customtkinter.CTkButton(frame, text="SET", command=add_data, corner_radius=10)
        set_button.grid(row=5, column=0, columnspan=2, pady=20)
        return frame

    def show_tab(self, name):
        for frame in self.tabs.values(): frame.pack_forget()
        self.tabs[name].pack(expand=True, fill="both")

#----------------------------------------------- Rental Tab --------------------------------------------
class RentManager(customtkinter.CTkToplevel):
    def __init__(self):
        super().__init__()
        
        self.title(Settings.TITLE)
        self.after(250, lambda : self.iconbitmap(Settings.ICON))
        self.after(500, self.state, "zoomed")
        
        #Open at top
        self.focus()
        self.grab_set()
        self.lift()
        self.attributes('-topmost', True)
        self.after(10, lambda: self.attributes('-topmost', False))
        
        table_frame = customtkinter.CTkFrame(self)
        table_frame.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        # Table
        self.table = ttk.Treeview(table_frame, columns=('No', 'Locker', 'Name', 'Date', 'Time'), show="headings", yscrollcommand=scrollbar.set, selectmode="browse")
        columns = {"No": "Sr. No.", "Locker": "Locker Details", "Name": "Customer Name", "Date":"Registration Date", "Time": "Time to Renew"}

        for col, heading in columns.items():
            self.table.heading(col, text=heading, anchor="center")
            self.table.column(col, anchor="center")

        self.table.pack(expand=True, fill="both")
        scrollbar.config(command=self.table.yview)
        self.show_details()
    
    def remain_days(self, date):
        year, month, day = str(date).split("-")
        year = int(year)+1
        day = int(day)-1
        return f"{year}-{month}-{day}"
    
    def show_details(self):
        for index, entry in enumerate(DatabaseManager().get_rent_details()):
            data = (index+1, f"{entry[1]} - {entry[0]}", f"{entry[2]} {entry[3]} {entry[4]}", entry[5], self.remain_days(entry[5]))
            self.table.insert("", "end", values=data)
        
#-------------------------------------- Generating Locker structure ------------------------------------
class LockerLayoutBase(customtkinter.CTkToplevel):
    def __init__(self, locker_data, button_callback, filter_func, button_state_func, title):
        super().__init__()

        # Window settings
        self.title(title)
        self.after(250, self.state, "zoomed")
        self.after(250, lambda : self.iconbitmap(Settings.ICON))

        self.focus()
        self.grab_set()
        self.lift()
        self.attributes('-topmost', True)
        self.after(10, lambda: self.attributes('-topmost', False))

        # Layout grid
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure((0, 2), weight=1)

        # Tab views
        self.views = customtkinter.CTkTabview(self, width=800, corner_radius=10)
        self.views.grid(row=1, column=1, sticky="nsew", padx=10, pady=(40, 20))

        # Locker layout per type
        for locker_size, (occupied, size, column, pad, partition, total_lockers) in locker_data.items():
            self.views.add(locker_size)

            if partition:
                partitions = customtkinter.CTkTabview(self.views.tab(locker_size), width=1000, corner_radius=10)
                partitions.grid(row=1, column=1, sticky="nsew")
                for i, section in enumerate(partition):
                    tab_name = section
                    partitions.add(tab_name)
                    scrollFrame = customtkinter.CTkScrollableFrame(partitions.tab(tab_name), width=1000, height=800, corner_radius=10)
                    scrollFrame.grid(padx=10, pady=10, sticky="nsew")
                    scrollFrame.columnconfigure(tuple(range(column)), weight=1)

                    self.generate_buttons(occupied, size, column, pad, scrollFrame, button_callback, tab_name, int(total_lockers[i]), filter_func, button_state_func)
            else:
                scrollFrame = customtkinter.CTkScrollableFrame(self.views.tab(locker_size), width=1000, height=800, corner_radius=10)
                scrollFrame.grid(padx=10, pady=10, sticky="nsew")
                scrollFrame.columnconfigure(tuple(range(column)), weight=1)

                self.generate_buttons(occupied, size, column, pad, scrollFrame, button_callback, "", int(total_lockers), filter_func, button_state_func)

    def generate_buttons(self, occupied, size, column, pad, frame, callback, prefix, total, filter_func, button_state_func):
        count = 1
        row, col = 0, 0
        for _ in range(total):
            locker_id = f"{prefix}{count}"
            if not filter_func(locker_id, occupied): count += 1; continue
            state = button_state_func(locker_id, occupied)
            customtkinter.CTkButton(frame, width=size[0], height=size[1], font=("Calibri", 20), text=locker_id, corner_radius=20, state=state, 
                                             command=lambda num=locker_id: callback(num, self.views.get())).grid(row=row, column=col, padx=pad[0], pady=pad[1])
            col += 1
            if col >= column: row += 1; col = 0
            count += 1
            
#----------------------------------------- Showing All lockers ------------------------------------------
class ShowAllLockers(LockerLayoutBase):
    def __init__(self):
        locker_data = self.prepare_data()
        super().__init__(locker_data, self.select_callback, self.filter_all_lockers, self.disable_occupied_lockers, f"{Settings.TITLE} - Add new Locker")
    
    def prepare_data(self):
        occupied = {"Small": [], "Medium": [], "Large": []}
        for row in DatabaseManager().get_occupied_lockers(): occupied[row[1]].append(row[0])
        return self.structure_data(occupied, DatabaseManager().get_lockers())

    def structure_data(self, occupied, total_data):
        lockers = {
            'Small': [occupied["Small"], [150, 100], 5, [10, 10]],
            'Medium': [occupied["Medium"], [175, 125], 4, [15, 15]],
            'Large': [occupied["Large"], [200, 150], 4, [20, 20]],
            }
        try:
            for k, v in total_data.items():
                if len(v) == 1: lockers[k] += [[], v[0]]
                else: lockers[k] += [v[0], v[1]]
            return lockers
        except:
            if messagebox.showerror("Lockers Data not Found !", "Please set the lockers first !"): LockerManager(); self.destroy()

    def filter_all_lockers(self, locker_id, occupied):
        return True  # Show every locker

    def disable_occupied_lockers(self, locker_id, occupied):
        return "disabled" if locker_id in occupied else "normal"

    def select_callback(self, locker_num, locker_size):
        self.destroy()
        MainForm().Set_data(locker_num, locker_size)

#------------------------------------ Showing occupied lockers only ------------------------------------
class ReleaseLocker(LockerLayoutBase):
    def __init__(self, flag=False):
        self.flag = flag
        title = f"{Settings.TITLE} - Release Locker" if flag else f"{Settings.TITLE} - Update Locker"
        locker_data = self.prepare_data()
        if locker_data: super().__init__(locker_data, self.release_callback, self.filter_occupied_only, self.enable_all, title)

    def prepare_data(self):
        occupied = {"Small": [], "Medium": [], "Large": []}
        for row in DatabaseManager().get_occupied_lockers():
            occupied[row[1]].append(row[0])
        return self.structure_data(occupied, DatabaseManager().get_lockers())

    def structure_data(self, occupied, total_data):
        lockers = {
            'Small': [self.sorter(occupied["Small"]), [150, 100], 5, [10, 10]],
            'Medium': [self.sorter(occupied["Medium"]), [175, 125], 4, [15, 15]],
            'Large': [self.sorter(occupied["Large"]), [200, 150], 4, [20, 20]]
        }
        try:
            for k, v in total_data.items():
                if len(v) == 1:
                    lockers[k] += [[], v[0]]
                else:
                    lockers[k] += [v[0], v[1]]
            return lockers
        except:
            if messagebox.showerror("Lockers Data not Found !", "Please set the lockers first !"): LockerManager(); self.destroy()

    def sorter(self, data):
        if data and not data[0].isnumeric():
            for i in range (len(data)-1):
                for j in range (i, len(data)):
                    temp = ""
                    if len(data[i]) > 1 and data[i][0] == data[j][0]:
                        if int(data[i][1:]) > int(data[j][1:]):
                            temp = data[i]
                            data[i] = data[j]
                            data[j] = temp
        else :
            data = [int(ele) for ele in data]
            data = sorted(data)
            data = [str(ele) for ele in data]
        return data

    def filter_occupied_only(self, locker_id, occupied):
        return locker_id in occupied

    def enable_all(self, locker_id, occupied):
        return "normal"

    def release_callback(self, locker_num, locker_size):
        if self.flag == True:
            if messagebox.askyesno("Confirm Release", f"Do you want to release locker {locker_num}?"):
                messagebox.showinfo("Locker Released", f"Locker {locker_num} has been successfully released.")
                DatabaseManager().releaseLocker(locker_num, locker_size)
                self.destroy()
        elif self.flag == False:
            data = list(DatabaseManager().get_occupied_details(locker_num, locker_size).values())
            MainForm().Set_data(data[0][0], data[1][0], data)
              
#----------------------------------------- Saving to Excel file -------------------------------------------  
class GetIntoExcel:
    def getDownPath(self):
        if os.name == "nt": return Path(os.environ["USERPROFILE"]) / "Downloads"
        else: return Path.home() / "Documents"
    
    def writeData(self, filename, details):
        down_path = self.getDownPath()
        
        if not os.path.exists(str(down_path) + "/Locker System"): os.makedirs(str(down_path) + "/Locker System")
        to_store = f'{down_path}/Locker System/'
        
        dataFrame = pandas.DataFrame(details)
        writer = pandas.ExcelWriter(path=f"{to_store}{filename}.xlsx", engine="openpyxl")
        dataFrame.to_excel(writer, sheet_name="Data", index=False)
        writer.close()

    def occupied_lockers(self):
        down_path = self.getDownPath()
        details = DatabaseManager().get_occupied_details()
        self.writeData("Occupied Lockers", details)
        
        if messagebox.askyesno("Saved sucessfully", "File is saved in Download//Locker System folder \nDo you want to open the file?", icon='info'):
            os.startfile(f'{down_path}/Locker System/Occupied Lockers.xlsx')
    
    def visitors_list(self):
        down_path = self.getDownPath()
        details = DatabaseManager().get_visitors_details()
        self.writeData("Visitors", details)
        
        if messagebox.askyesno("Saved sucessfully", "File is saved in Download//Locker System folder \nDo you want to open the file?", icon='info'):
            os.startfile(f'{down_path}/Locker System/Visitors.xlsx')
    
    def old_customers(self):
        down_path = self.getDownPath()
        details = DatabaseManager().get_old_customer_details()
        self.writeData("Old customers", details)
        
        if messagebox.askyesno("Saved sucessfully", "File is saved in Download//Locker System folder \nDo you want to open the file?", icon='info'):
            os.startfile(f'{down_path}/Locker System/Old customers.xlsx')
  
#----------------------------------------- Main GUI structure -------------------------------------------                
class GUI(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        #GUI Settings
        self.title(Settings.TITLE)
        self.after(500, self.state, "zoomed")
        self.after(250, lambda : self.iconbitmap(Settings.ICON))
        
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(0, weight=1)
        sv_ttk.set_theme(customtkinter.get_appearance_mode())
        WindowSettings().changeTablestyle()
        
        #Initilizing required
        self.entries = {}
        self.counter = 1
        self.initilize()
        
        #Camera background Frame
        self.leftFrame = customtkinter.CTkFrame(self, corner_radius=5, width=480, height=600)
        self.leftFrame.pack(side=customtkinter.LEFT, fill="y", padx=10, pady=20)
        
        #Visitor Frame
        self.rightFrame = customtkinter.CTkFrame(self, corner_radius=5)
        self.rightFrame.pack(side=customtkinter.RIGHT, padx=10, pady=20, fill=customtkinter.BOTH, expand=True)
        
        #Camera Label Frame
        self.cameraFrame = customtkinter.CTkFrame(self.leftFrame, corner_radius=10, border_width=3, width=485, height=400)
        self.cameraFrame.grid(row=1, pady=40, padx=20)
        
        #Camera Frame inside Camera background Frame
        self.camera_label = customtkinter.CTkLabel(self.cameraFrame, text="",  width=480, height=400)
        self.camera_label.pack(padx=3, pady=3)
        
        #Update message
        self.status = customtkinter.CTkLabel(self.leftFrame, text="", font=("", 22, "bold"), width=480, height=20)
        self.status.grid(row=3, padx=5, pady=(50, 50))
        
        #Camera Button
        self.camera_button = customtkinter.CTkButton(self.leftFrame, text="🎥 Start Camera", font=("", 22, "bold"), width=300, height=50, command=self.toggle_camera) 
        self.camera_button.grid(row=2, padx=20, pady=(20, 50))
        
        #Calling Menu
        self.getmenu()
        self.visitors()

    def getmenu(self):
        MENU = tkinter.Menu(self, tearoff=0)
        self.config(menu=MENU)

        FILEMENU1 = tkinter.Menu(MENU, tearoff=0)
        FILEMENU2 = tkinter.Menu(MENU, tearoff=0)
        FILEMENU3 = tkinter.Menu(MENU, tearoff=0)
        FILEMENU4 = tkinter.Menu(MENU, tearoff=0)
        
        MENU.add_cascade(label="Manage Lockers", menu=FILEMENU1)
        MENU.add_cascade(label="Settings", menu=FILEMENU2)
        MENU.add_cascade(label="Window", menu=FILEMENU3)
        MENU.add_cascade(label="Export", menu=FILEMENU4)
        
        FILEMENU1.add_command(label="Add Locker", activebackground="#0A84FF", command=ShowAllLockers)
        FILEMENU1.add_command(label="Release Locker",  activebackground="#0A84FF", command=lambda : ReleaseLocker(True))
        FILEMENU1.add_command(label="Update Locker",  activebackground="#0A84FF", command=ReleaseLocker)
        FILEMENU1.add_command(label="Rent Details",  activebackground="#0A84FF", command=RentManager)
        FILEMENU1.add_separator()
        FILEMENU1.add_command(label="Exit", activebackground="#0A84FF", command=self.destroy)
        
        FILEMENU2.add_command(label="Setup total lockers", activebackground="#0A84FF", command=LockerManager)
        FILEMENU2.add_separator()
        
        SUBFILEMENU1 = tkinter.Menu(FILEMENU3, activebackground="#0A84FF", tearoff=0)
        SUBFILEMENU2 = tkinter.Menu(FILEMENU3, activebackground="#0A84FF", tearoff=0)
        
        FILEMENU3.add_cascade(label="Change Appearance", activebackground="#0A84FF", menu=SUBFILEMENU1)
        FILEMENU3.add_cascade(label="Set Camera", activebackground="#0A84FF", menu=SUBFILEMENU2)
        FILEMENU3.add_separator()
        
        SUBFILEMENU1.add_command(label="Light", activebackground="#0A84FF", command= lambda mode="light" : WindowSettings().changeAppearance(mode))
        SUBFILEMENU1.add_command(label="Dark", activebackground="#0A84FF", command= lambda mode="dark" : WindowSettings().changeAppearance(mode))
        
        for cam in range (10):
            camera = cv2.VideoCapture(cam)
            if camera.isOpened():
                if cam == 0:
                    SUBFILEMENU2.add_command(label="Default", activebackground="#0A84FF", command=lambda camera=cam : self.updateCamera(camera))
                else:
                    SUBFILEMENU2.add_command(label=f"External Camera {cam}", activebackground="#0A84FF", command=lambda camera=cam : self.updateCamera(camera))
        
        FILEMENU4.add_command(label="Get occupied locker details", activebackground="#0A84FF", command=lambda : GetIntoExcel().occupied_lockers())
        FILEMENU4.add_command(label="Get visitors details", activebackground="#0A84FF", command=lambda : GetIntoExcel().visitors_list())
        FILEMENU4.add_command(label="Get old customer details", activebackground="#0A84FF", command=lambda : GetIntoExcel().old_customers())
        FILEMENU4.add_separator()

    def updateCamera(self, camera):
        Settings.CAMERA = camera
        print(Settings.CAMERA)
    
    def visitors(self):        
        # Treeview table inside right_frame
        table_frame = customtkinter.CTkFrame(self.rightFrame)
        table_frame.pack(expand=True, fill="both", padx=5, pady=5)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        # Table
        columns = {"No": "Sr. No.", "LType":"Locker Type", "Lno": "Locker No.", "Name": "Customer Name", "Entry": "Entry Time", "Exit": "Exit Time"}
        self.table = ttk.Treeview(table_frame, columns=('No', 'LType', 'Lno', 'Name', 'Entry', 'Exit'), show="headings", yscrollcommand=scrollbar.set, selectmode="browse")

        for col, heading in columns.items():
            self.table.heading(col, text=heading, anchor="center")
            self.table.column(col, anchor="center")

        self.table.pack(expand=True, fill="both")
        scrollbar.config(command=self.table.yview)
        self.visitors_info()
    
    def visitors_info(self):
        try: self.table.delete(*self.table.get_children())
        except : pass
        for index, entries in enumerate(DatabaseManager().get_visitors()): 
            data = (index+1, )+entries
            self.table.insert("", "end", values=data)

    def initilize(self):
        self.choosenLocker = None
        self.checking = False
        self.wait_thread = None
        self.current_person = None
        self.entry_detected = False
        self.waiting_for_exit = False  
        self.camera_running = False
        self.logs = {} 

    def selectlocker(self, person, lockers):
        newCTk = customtkinter.CTkToplevel()
        newCTk.title(f'{Settings.TITLE} - Select your locker')
        newCTk.after(250, lambda : newCTk.iconbitmap(Settings.ICON))
        width_of_window = 500
        height_of_window = int(f"{len(lockers)}00")

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = (screen_width/2)-(width_of_window/2)
        y_coordinate = (screen_height/2)-(height_of_window/2)
        newCTk.geometry("%dx%d+%d+%d" %(width_of_window,height_of_window,x_coordinate,y_coordinate))
        
        newCTk.focus()
        newCTk.grab_set()
        newCTk.lift()
        newCTk.attributes('-topmost', True)
        newCTk.after(10, lambda: newCTk.attributes('-topmost', False))
        
        def selectedlocker(data):
            self.choosenLocker = data
            newCTk.destroy()

        customtkinter.CTkLabel(newCTk, text=f"Mr./Miss {person} \nWhich locker you want to access ?", font=("", 18, 'bold')).pack(padx=20, pady=20)
        
        for index, locker in enumerate(lockers):
            customtkinter.CTkRadioButton(newCTk, text=f"{locker[1]} - {locker[0]}", value=index, command=lambda data=locker: selectedlocker(data)).pack(padx=20, pady=10)
            
        self.wait_window(newCTk)
        return self.choosenLocker

    def getlockers(self, match):
        lockers = DatabaseManager().get_locker_owners()
        locker_details = []
        if lockers:
            for rows in lockers:
                if f'{rows[3]} {rows[4]} {rows[5]}' == match: locker_details.append((rows[0], rows[1]))
            if len(locker_details) > 1: return self.selectlocker(match, locker_details)
            elif locker_details: return locker_details[0]
        return False
            
    def toggle_camera(self):
        if self.camera_running:
            if self.waiting_for_exit:
                self.waiting_for_exit = False
                exit_time = datetime.datetime.now().strftime("%T")
                self.entries[self.counter].append(f"{exit_time}")
                DatabaseManager().set_visitors(self.locker_no, exit_time=exit_time)
                self.counter+=1
                self.visitors_info()
            self.initilize()
            self.status.configure(text="")
            self.camera_label.configure(image=None)
            self.camera_button.configure(text="🎥 Start Camera")
            self.camera.release()
            cv2.destroyAllWindows()
        else:
            self.camera_running = True
            self.camera = cv2.VideoCapture(Settings.CAMERA)
            self.camera.set(cv2.CAP_PROP_FPS, 60)
            self.camera_button.configure(text="⏹ Stop Camera")
            self.start_wait(init=True, onEnter=False, onExit=False)
            self.camera_window()
                
    def update_match_result(self, match):
        self.match = match
    
    def run_face_recognition(self, gray, frame):
        faces = Settings.MODEL.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
        match = "Unknown"
        for (x, y, w, h) in faces:
            face_frame = frame[y:y+h, x:x+w]  
            self.checking = False
            match = Datasets().Recognize(face_frame)
            self.checking = True
        self.after(0, lambda: self.update_match_result(match))
    
    def start_face_thread(self, gray, frame):
        if not hasattr(self, "face_thread") or not self.face_thread.is_alive():
            self.face_thread = threading.Thread(target=self.run_face_recognition, args=(gray.copy(), frame.copy()), daemon=True)
            self.face_thread.start()
    
    def camera_window(self):      
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            match = "Unknown"
            
            if self.checking: 
                self.start_face_thread(gray, frame)
                if self.match : match = self.match
            
            if match != "Unknown" and match !="No faces registered":
                if match not in self.logs and not self.entry_detected: self.record_entry(match)
                elif match == self.current_person and self.entry_detected and self.waiting_for_exit: self.record_exit(match)
            elif match == "No faces registered":
                if messagebox.showerror("Unknown Person", "Unknown Face, Please register your locker !"):
                    self.checking = False
                    self.after(250, self.toggle_camera)

            #Remove cv2 black border
            _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
            x, y, w, h = cv2.boundingRect(thresh)
            frame = frame[y:y+(h-10), x:x+w]
                    
            # Converting Frame to image
            img = Image.fromarray(frame)
            img = img.resize((480, 400))
            
            #Creating a Mask
            mask = Image.new("L", (480, 400), 0)
            draw = ImageDraw.Draw(mask)
            draw.rounded_rectangle((0, 5, 480, 400), fill=255, outline=0, radius=20)
            
            img.putalpha(mask)
            photo = customtkinter.CTkImage(light_image=img, size=(480, 400))
            self.camera_label.configure(image = photo)
        
        if self.camera_running:
            self.after(30, self.camera_window)
    
    def record_entry(self, match):
        entry_time = datetime.datetime.now().strftime("%T")
        self.logs[match] = {"Entry": entry_time, "Exit": None}
        try:
            self.locker_no, self.locker_size = self.getlockers(match) 
            self.entries[self.counter] = [self.locker_no, match, entry_time]
            DatabaseManager().set_visitors(self.locker_no, self.locker_size, match, entry_time=entry_time)
            self.visitors_info()
            self.current_person = match
            self.entry_detected = True  
            self.status.configure(text = f"{match} Inside \nWaiting for Exit...")
            
            self.start_wait(init=False, onEnter=True, onExit=False)
        except Exception:
            if messagebox.showerror("Locker closed", f"Mr/Miss {match} your locker is closed"):
                self.after(250, self.toggle_camera)

    def record_exit(self, match):
        exit_time = datetime.datetime.now().strftime("%T")
        self.logs[match]["Exit"] = exit_time
        if len(self.entries) != 5:
            self.entries[self.counter].append(exit_time)
            DatabaseManager().set_visitors(self.locker_no, exit_time=exit_time)
        self.visitors_info()
        self.start_wait(init=False, onEnter=False, onExit=True)

    def start_wait(self, init=False, onEnter=False, onExit=False):
        if self.wait_thread is None or not self.wait_thread.is_alive():
            self.wait_thread = threading.Thread(target=self.wait, args=(init, onEnter, onExit), daemon=True)
            self.wait_thread.start()

    def wait(self, init, onEnter, onExit):
        if init:
            self.status.configure(text = "Initializing...... Wait \nFor a while ... !")
            threading.Event().wait(10)
            if self.camera_running:
                self.status.configure(text = "Ready to check ......")
                self.checking = True

        elif onEnter:
            self.checking = False
            self.waiting_for_exit = True  
            threading.Event().wait(10)  
            if self.camera_running:  
                self.checking = True
                self.status.configure(text = "Checking for Exit...")

        elif onExit:
            self.checking = False
            self.waiting_for_exit = False
            self.counter+=1
            if self.camera_running:
                self.status.configure(text = "Resetting ......... Wait")
                threading.Event().wait(10)
                self.reset_system()

    def reset_system(self):
        self.logs = {}  
        self.current_person = None
        self.entry_detected = False
        self.waiting_for_exit = False  
        if self.camera_running: 
            self.status.configure(text = "Waiting for Person...")
            threading.Event().wait(2)
            self.checking = True
    
#------------------------------------------ Loading Window --------------------------------------------  
class PreLoading(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.focus()
        self.grab_set()
        self.lift()
        self.attributes('-topmost', True)
        self.after(10, lambda: self.attributes('-topmost', False))
        
        def start_anim():
            p_bar.start()
            
        width_of_window = 480
        height_of_window = 250
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = (screen_width/2)-(width_of_window/2)
        y_coordinate = (screen_height/2)-(height_of_window/2)
        self.geometry("%dx%d+%d+%d" %(width_of_window,height_of_window,x_coordinate,y_coordinate))
        self.config(relief="solid", borderwidth=2, highlightthickness=2)
        self.overrideredirect(True)

        frame = customtkinter.CTkFrame(self, corner_radius=0, fg_color="transparent")
        frame.pack(padx=0, pady=0)
        customtkinter.CTkLabel(frame, text='Banking Locker System', font=('', 28, 'bold')).pack(anchor="center", pady=(90, 10), padx=77)
        customtkinter.CTkLabel(frame, text='Loading...', font=('', 18, "bold")).pack(pady=(20, 20))

        p_bar = customtkinter.CTkProgressBar(frame, width=300, height=5, mode='indeterminate')
        p_bar.pack(pady=(17, 20))
        
        self.after(10, start_anim)
        self.after(5000, self.destroy)

if __name__ == "__main__":
    PreLoading().mainloop()
    GUI().mainloop()
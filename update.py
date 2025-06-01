from App import *

class newGUI(customtkinter.CTk):
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
        self.match = None
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
    

if __name__ == "__main__":
    app = newGUI()
    app.mainloop()
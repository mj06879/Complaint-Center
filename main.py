import csv
from logging import root
from random import seed
from random import randint
from tkinter import Tk, mainloop, LEFT, TOP
from tkinter.ttk import *
import tkinter as tk
from tkinter import *
from tkinter import ttk
from typing import Any
from PIL import Image, ImageTk
import time
from datetime import date
from datetime import datetime, time
from datetime import datetime, timedelta
import datetime as dt
from functools import partial
import os
import random
from regex import R

class Node():
    def __init__(self, val, index):
        self.val = val        #priority of query in this case
        self.children = []    #each node contains pointers to children
        self.index = index    #loaction of query in the list where they are stored

class Heap():
    def __init__(self):
        self.root = None

    def find_max_val(self)->int:
        if self.root == None:
            return ("Heap is empty!")
        else:
            return self.root.val

    def find_max_index(self)->int:
        if self.root == None:
            return False
        else:
            return self.root.index

    def _merge(self, root1, root2):
        if root1 == None:
            return root2
        elif root2 == None:
            return root1
        elif root1.val > root2.val:
            root1.children.append(root2)
            return root1
        else:
            root2.children.append(root1)
            return root2

    def insert(self, val, index):
        self.root = self._merge(self.root, Node(val, index))

    def delete_max(self):
        if self.root == None:
            return False
        else:
            self.root = self._merge_pairs(self.root.children)
            return True

    def _merge_pairs(self, l):
        if len(l) == 0:
            return None
        elif len(l) == 1:
            return l[0]
        else:
            return self._merge(self._merge(l[0], l[1]), self._merge_pairs(l[2:]))

#extracting data from excel files assigning priority and inserting into pairing heap
class Query():
    def __init__(self) -> None:

        self.Data = {}
        self.Queries=[]
        self.h1 = Heap()
        self.deleted_index = []     # To store indexes of Queries being resolved & getting deleted from Heap. 

        self.lowest_Frequency = float('inf')    # initially setting up at +ve infinity. 
        self.lowest_spent = float('inf')
        self.priority_dict = {}  # (keys: priority, vlaue: Index)    # The recorde of priorities and the index of queries... For checking that not getting the same priority agian. 
        
        self.type_severity = {"Personnel": 0.5, "Communication":0.75, "Delivery": 1, "Product/Service": 2,
        "Website": 5}         # {Type: Severity factor.}
        
        # Key words in complaints ... [0, 1, ... , n]  --> index number tells the severity.
        self.key_words_lst =  ["save", "cheap", "cheaply", "noisy", "noise", "sick", "suck", "throw", "threw",
        "disappoinent", "disappointing","disappointed", "irritating", "quality", "equipment","durable", "poor",
        "poorly", "risk", "missing", "fragile", "drastically", "problem", "problems", "waste", "wasted", "regret", "frustrating",
        "uncomfortable", "junk", "trash", "trashed", "garbage", "cracked", "break", "broke", "damage", "destroyed", "avoid", "bad",
        "nasty", "crap", "crapy", "worthless", "unbearable", "hate", "hated", "painful", "unusable", "failed", "useless",
        "damned", "worst", "disaster", "terrible"]

        with open("Data_user.csv", 'r') as file:
            reader = csv.reader(file)
            count = 0
            for row in reader:
                if count >=1:
                    self.Data[row[1]] = row[0:1] + row[2:]   
                    # self.Data = {User_name: [Client_ID, City, Region, Total_Amount_Spent, Frequency, Password]}
                
                count+=1
            
        with open("Complaints.csv", 'r') as file:
            reader=csv.reader(file)
            count  = 0
            for row in reader:
                self.Queries.append(row)
                    # row = [Complaint_ID, User_name, Amnt_of_last_order, Complaint, Last_purchased_time, Type, Product_ID, Initial_time]

                if count >=1:
                    if row[7] == str(None):                     # if Initial_Time  == None, then setting it today's date. 
                        now = datetime.now()
                        now = now.strftime("%d/%m/%Y, %H:%M:%S")
                        row[7] = now
                    
                    # We are taking lowest frequency and lowest spent out of those Users that are in complaits. 
                    if int((self.Data[row[1]])[3]) < self.lowest_spent:   # Data[row[1]] = [Client_ID, City, Region, Total_Amount_Spent, Frequency, Password] 
                        self.lowest_spent = int((self.Data[row[1]])[3])   # 
                    if int((self.Data[row[1]])[4]) < self.lowest_Frequency:
                        self.lowest_Frequency = int((self.Data[row[1]])[4])    
                count +=1 

        self.Heading= self.Queries.pop(0)        


        # print(self.Heading)
        # print()
        # print(self.Queries)
        # print("lowest_frequency: ", self.lowest_Frequency)
        # print("lowest_spent: ", self.lowest_spent)

        self.ranking()

    def ranking(self)->None:                              # Ranking all Complaints 
        count=0

        for query in self.Queries:
            priority = self.Ranking_helper(query, count)  # need to figure out way to determine this -->helper function (ranking_helper)
            self.h1.insert(priority,count)  
            count+=1
        
    def Ranking_helper(self, query, index)->float:       # Returns the priority of every query 

        spent_P = self.Spent_priority(int((self.Data[query[1]])[3]))
        freq_P = self.Freq_priority(int((self.Data[query[1]])[4]))
        crit_P = self.Critical_keys(query[3], query[5])
        factor_P = self.factor(query[7])
        no_of_days_P = self.No_of_days(query[4], query[7])
        
        Priority = (spent_P * freq_P * crit_P * factor_P)/no_of_days_P          # all Relative prioties in Main priority formula.

        while Priority in self.priority_dict.keys():
            Priority += 1                                  # when get same priority ... +1 by inspiration of linear probing 
        
        self.priority_dict[Priority] = index               # Adding the new priority in priority dictionary. 
        return Priority

    def Freq_priority(self, freq) ->float:                 # Taking out the ratio with Lowest frequency.
        return (freq/self.lowest_Frequency)
    
    def Spent_priority(self, spent) -> float:
        return (spent/self.lowest_spent)                   #  # Taking out the ratio with Lowest Spent.

    def No_of_days(self, last_purchased, Initial_time) ->float:     
        time = (self.Time_format(last_purchased, Initial_time))//60 + 1       # +1 for not getting zero ... bcz in main function it's in division ..and on NO difference --> /1 , No effect on Main priority function.            
        return time

    def factor(self, Initial_time) ->float:             # When a Complaint has been Registered. priority relatively increases with increase in Registerd Time and Current Time 
        now = datetime.now()                  
        now = now.strftime("%d/%m/%Y, %H:%M:%S")
        time = (self.Time_format(Initial_time, now) + 1) 
        time = time*100                                 # Just to show relative differnce at a sudden ... we multiplied by 100

        return time

    def Critical_keys(self, review, Type):              # Return the relative priority according to Severity of type of keywords. 
        priority = 0
        count = 1
        review = review.split(" ")
        for i in review:
            if i in self.key_words_lst:
                priority += self.key_words_lst.index(i) + 1   # +1 bcz of starting from 1
                count += 1                               # no.of key_words used in review

        priority = (priority/count) * self.type_severity[Type]
        return priority
                 
    def Time_format(self, T_1, T_2) ->float:            # A helping function for calculating time differnce in minutes

        Time_1 = T_1.split(", ")
        Time_1_date = Time_1[0].split("/")
        Time_1_time = Time_1[1].split(":")
        Time_2 = T_2.split(", ")
        Time_2_date = Time_2[0].split("/")
        Time_2_time = Time_2[1].split(":")
    
        # datetime(year, month, day, hour, minute, second)    # b-a ... T_2 - T_1
        a = datetime(int(Time_1_date[2]), int(Time_1_date[1]), int(Time_1_date[0]), int(Time_1_time[0]), int(Time_1_time[1]), int(Time_1_time[2]))
        b = datetime(int(Time_2_date[2]), int(Time_2_date[1]), int(Time_2_date[0]), int(Time_2_time[0]), int(Time_2_time[1]), int(Time_2_time[2]))
        c = b - a
        total_mins = c.total_seconds()/60
        return((total_mins))

    def Get_Max_Value(self):                # return the highest prioity number. 
        return self.h1.find_max_val()

    def Get_Max_Index(self):                # returns the index of query on highest priority. 
        a = self.h1.find_max_index()
        return (a)

    def Top_Query(self):                    # returns the Compliant on top of Heap, means the complaint of highest priority. 
        ind = self.Get_Max_Index()
        query  = self.Queries[ind]
        user_name = query[1]
        Complaint = query[3]
        Result  = str(user_name) + ": " + str(Complaint)
        return Result

    def Deletion(self):                     # Deletes the Top Complaint from heap. 
        ind = self.Get_Max_Index()
        self.deleted_index.append(ind)
        self.h1.delete_max()

    def Button_for_Deletion(self):
        self.Deletion()

    def Validate_User(self, username, password):
        for key in self.Data:
            if key == username:
                if (self.Data[key])[5] == password:
                    return True 
        return False

    def Retreive_most_imp_query(self)->str:
        if self.h1.find_max_index!=False:
            original_entry= self.Queries[self.h1.find_max_index()]
            return (original_entry[1]+": " +original_entry[8])

    def Recreate_heap(self):                    # Recreate the heap ...
        self.deleted_index.sort()
        for i in reversed(self.deleted_index):
            self.Queries.pop(i)

        self.deleted_index = []

        is_empty = False
        while is_empty == False:      # making the Heap Empty
            check = self.h1.delete_max()
            if check == False:
                is_empty = True
                
        priority_list = list(self.priority_dict.keys())
        priority_list.sort()

        lowest_priority = priority_list[0]
        highest_priority = priority_list[len(priority_list)-1]
        average_priority = (highest_priority+lowest_priority)//2           # Taking out the average priority in the Heap so on Recreation ... priority will releative change.
        count=0
        priority_list = list(self.priority_dict.keys())
        indexes_list = list(self.priority_dict.values())

        self.priority_dict = {}                                     # Heap is empyt so priority_dict is empty ..and new generated priorities will now be inserted. 
        for query in self.Queries:
            priority = self.New_Priority_generator(query, count, priority_list, indexes_list, average_priority) 
            while priority in self.priority_dict:
                priority += 1
            self.priority_dict[priority] = count
            self.h1.insert(priority,count)  
            count+=1

    #Inserting new Query given by User  
    def New_Priority_generator(self, query, count, priority_list, indexes_list, average_priority):   # Generates the new relative priority. 
        i = indexes_list.index(count)
        old_priority = priority_list[i]
        if old_priority > average_priority:
            new_priority = old_priority/(self.factor(query[7]))
        elif old_priority <= average_priority:
            new_priority = old_priority*(self.factor(query[7]))
        return new_priority
         

    def Insertion(self, Amount, ProductID, Review, choice_of_complaint, Username, Purchase_Date):    # Insertion in Queries by User
        #appending Queries
        ComplaintID=random.randint(10000, 100000)
        now = datetime.now()
        initial_time = now.strftime("%d/%m/%Y, %H:%M:%S")
        Time_1 = initial_time.split(", ")

        FinalPurchaseDate=Purchase_Date+", " + Time_1[1]
        self.Queries.append([ComplaintID, Username, Amount, Review, FinalPurchaseDate, choice_of_complaint, ProductID, initial_time])

        #updating Data of Users
        # for user_data in self.Data:
        for key,value in self.Data.items():
            if Username==key:
                self.Data[key]=[self.Data[key][0],self.Data[key][1], self.Data[key][2], int(self.Data[key][3])+Amount, int(self.Data[key][4])+1, self.Data[key][5]]
    
    def Button_for_Recreation(self):
        self.Recreate_heap()

    def Update_CSV(self, clicked):    
        Nested_Data_User = [["Client_ID", "Username", "City", "Region", "Total Amount Spent", "Frequency of Purchase", "Password"]]
        for key, value in self.Data.items():
            temp = [value[0], key, value[1], value[2], value[3], value[4], value[5]]
            Nested_Data_User.append(temp)

        self.Queries.insert(0, self.Heading)

        with open("Data_user.csv", mode="w",newline="") as csvfile:
            fav=csv.writer(csvfile)
            fav.writerows(Nested_Data_User)
        
        with open("Complaints.csv", mode="w",newline="") as csvfile:
            fav=csv.writer(csvfile)
            fav.writerows(self.Queries)


class Interface():
    def __init__(self) -> None:
        self.root = Tk()
        self.root.geometry('700x500')
        self.root.title("Call center")
        self.q1= Query()
        self.background('new_image.png')
        self.box = Text(Any,width=51,height=5)
  
    
    def background(self, filename):
        image = Image.open(filename)
        copy_of_image = image.copy()
        image = copy_of_image.resize((700, 500))
        photo = ImageTk.PhotoImage(image)
        label = ttk.Label(self.root, image = photo)
        label.bind('<Configure>')
        label.pack(fill=BOTH, expand = YES)
        self.Labels()
    
    #returns the Data and Time today
    def Time_Date(self, today=0):
        today=date.today()
        Date = today.strftime("%B %d, %Y")
        now = datetime.now()
        current_time=now.strftime("%H:%M")
        Time=(current_time)
        return (Date,Time)
    #Differentiaties between User and Admin and opens seperate screen
    def validateLogin(self, username, password):
        user_name=username.get()
        pass_word = password.get()

        print(user_name, pass_word)

        if self.q1.Validate_User(user_name, pass_word):
            print("Authorized access user")
            self.User(user_name)
        elif (user_name == "admin" and pass_word=="12"):
            print("Authorized access admin")
            self.admin()
        else:
            print("Access Denied")
            self.box_home.insert("end", "Invalid Username or Password, Please Try Again!")

    #Desiging Homepage
    def Labels(self):
        Date,Time=(self.Time_Date(today=0))
        Day=datetime.today().strftime('%A').upper()
        label_frame = tk.Label(self.root, text=Time,font=("Arial",35),fg="brown4").place(x=300,y=10)
        label_frame = tk.Label(self.root, text=Date,font=("Arial",12),fg="brown4").place(x=315,y=65)
        label_frame = tk.Label(self.root, text=Day,font=("Arial",10),fg="brown4").place(x=330,y=85)

        gret="WELCOME TO COMPLAINT \n CENTER"
        greeting = tk.Label(text=gret,font=("Arial Bold",18),fg="brown")
        greeting.place(x=190,y=120)
        self.Inputs()
    #Inputs on Homescreen
    def Inputs(self):

        username = StringVar()
        usernameLabel = Label(self.root, text="User Name").place(x=200, y=250)
        usernameEntry = Entry(self.root, textvariable=username).place(x=300, y=250)  
        
        passwordLabel = Label(self.root,text="Password").place(x=200, y=300)  
        password = StringVar()
        passwordEntry = Entry(self.root, textvariable=password, show='*').place(x=300,y=300)  

        #box
        self.box_home=Listbox(self.root,width=42,height=1)
        self.box_home.place(x=178,y=432)

        self.validateLogin = partial(self.validateLogin, username, password)
        loginButton = tk.Button(self.root, text="Login", command=self.validateLogin).place(x=340, y=350)
    
        self.root.mainloop()
   
    #User interface
    def User(self, user_name):
        self.Username=user_name
        userWindow= Toplevel(self.root)
        userWindow.title("User complaint")
        userWindow.geometry("700x500")
        Label(userWindow,text ="This is the User's view").pack()
        #insert backgorund here
        # image = Image.open("user_interface.png")
        # copy_of_image = image.copy()
        # image = copy_of_image.resize((800, 500))
        # photo = ImageTk.PhotoImage(image)
        # label = ttk.Label(userWindow, image = photo)
        # label.bind('<Configure>')
        # label.pack(fill=BOTH, expand = YES)

        image = Image.open("user_interface.png")
        copy_of_image = image.copy()
        image = copy_of_image.resize((700, 500))
        photo = ImageTk.PhotoImage(image)
        label = ttk.Label(userWindow, image = photo)
        label.bind('<Configure>')
        label.pack(fill=BOTH, expand = YES)

    


        gret="Welcome back, "+user_name  
        Greeting= Label(userWindow, text=gret, font = ("Times New Roman",18),fg="darkblue").place(x=250, y=50)

        Amount =IntVar()
        Amountlabel = Label(userWindow, text="Amount of Last \n Purchase").place(x=100, y=150)
        AmountEntry = tk.Entry(userWindow, textvariable=Amount).place(x=200, y=150) 

        ProductID = StringVar()
        ProductIDLabel = Label(userWindow,text="Product ID").place(x=100, y=200)  
        ProductIDEntry= tk.Entry(userWindow, textvariable=ProductID).place(x=200,y=200)  
 
        Purchase_Date = StringVar()
        Purchase_DateLabel = Label(userWindow,text="Purchase Date").place(x=100, y=250)  
        PurchaseEntry = tk.Entry(userWindow, textvariable=Purchase_Date).place(x=200,y=250)

        Review = StringVar()
        ReviewLabel = Label(userWindow,text="Complaint").place(x=100, y=300)  
        ReviewEntry = tk.Entry(userWindow, textvariable=Review).place(x=200,y=300, width= 200, height=60)


        Save=tk.Button (userWindow, text="Save", font=('Arial semibold', 12),fg="green",  compound=LEFT,relief=RAISED)
        Save.place(x=100,y=450)
        Save.bind('<Button-1>',self.q1.Update_CSV)

        #dropdown
        categories_of_complaints=["Personnel", "Product/Service", "Website", "Delivery", "Communication"]
        self.clicked = StringVar()
        self.clicked.set( "Type of Complaint" )
        drop = OptionMenu( userWindow , self.clicked , *categories_of_complaints)
        drop.place(x=430, y=150)
        drop.config(fg="darkblue",font=("Arial",10,"bold"))
        drop["menu"].config(bg="peach puff",fg="blue4",font=("Arial",10))
        self.clicked.trace('w',self.User_Drop_Down)

        #boxes
        self.box_user=Listbox(userWindow,width=33,height=1)
        self.box_user.place(x=200,y=400)
       

        #buttons
        self.Validate_User_Entry = partial(self.Validate_User_Entry, Amount, ProductID, Review, Purchase_Date)
        Submit=tk.Button (userWindow, text="Submit", font=('Arial semibold', 12),fg="darkblue",  compound=LEFT,relief=RAISED, command=self.Validate_User_Entry).place(x=100,y=400) 

        userWindow.mainloop()
    #Validating User Entries for Complaint Registration
    def Validate_User_Entry(self, Amount, ProductID, Review, PurchaseDate):

        Amount_=Amount.get()
        ProductID_= ProductID.get()
        Review_=Review.get()
        Purchase_Date=PurchaseDate.get()
        print(Amount_)
        if Amount_ <=0 :
            self.box_user.insert("end","Invalid Entry, Please Try Again")
            return

        self.box_user.delete(0,"end")
        self.box_user.insert("end","Your complaint has been registered")
        choice_of_complaint=self.User_Drop_Down()
        self.q1.Insertion(Amount_, ProductID_, Review_,choice_of_complaint, self.Username, Purchase_Date)

    def User_Drop_Down(self, *args)->str:
        categories_of_complaints=["Personnel", "Product/Service", "Website", "Delivery", "Communication"]
        Index_of_complaint=categories_of_complaints.index(self.clicked.get())
        if Index_of_complaint == 0:
            Choice_of_complaint="Personnel"
        elif Index_of_complaint == 1:
            Choice_of_complaint="Product/Service"
        elif Index_of_complaint == 2:
            Choice_of_complaint="Website"
        elif Index_of_complaint == 3:
            Choice_of_complaint="Delivery"
        elif Index_of_complaint == 4:
            Choice_of_complaint="Communication"
        
        return Choice_of_complaint

    #Admin Interface
    def admin(self):
        adminWindow= Toplevel(self.root)
        adminWindow.title("Admin View")
        adminWindow.geometry("700x500")
        
        #have to insert backgorund here
        image = Image.open("admin_interface.png")
        copy_of_image = image.copy()
        image = copy_of_image.resize((700, 500))
        photo = ImageTk.PhotoImage(image)
        label = ttk.Label(adminWindow, image = photo)
        label.bind('<Configure>')
        label.pack(fill=BOTH, expand = YES)
        
        #complaint box
        
        Heading= Label(adminWindow, text="Top Complaint", font = ("Times New Roman",18),fg="red").place(x=300, y=50)
        self.box=Text(adminWindow,width=80,height=15)
        self.box.place(x=20,y=100)

        self.box.insert("end", self.q1.Top_Query())

        #buttons
        Recreate=tk.Button (adminWindow, text="Recreate", font=('Arial semibold', 12),fg="green",  compound=LEFT,relief=RAISED)
        Recreate.place(x=320,y=400)
        Recreate.bind('<Button-1>',self.For_Recreation_show)
        
        Resolve=tk.Button (adminWindow, text="Resolve", font=('Arial semibold', 12),fg="green",  compound=LEFT,relief=RAISED)
        Resolve.place(x=320,y=360)
        Resolve.bind('<Button-1>',self.Repeat_For_Top_Query)

        Save=tk.Button (adminWindow, text="Save", font=('Arial semibold', 12),fg="green",  compound=LEFT,relief=RAISED)
        Save.place(x=320,y=440)
        Save.bind('<Button-1>',self.q1.Update_CSV)

        adminWindow.mainloop()
    

    def For_Recreation_show(self, clicked):      # Recreate heap ... and then show up the new Top new Complaint.
        self.q1.Button_for_Recreation()
        self.box.delete("1.0", "end")
        self.box.insert("end", self.q1.Top_Query())

    def Repeat_For_Top_Query(self, clicked):     # Delete the Top Query and show the new Top Complaint.
        self.q1.Button_for_Deletion()
        self.box.delete("1.0", "end")
        self.box.insert("end", self.q1.Top_Query())


I1=Interface()

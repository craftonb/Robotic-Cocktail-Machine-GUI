from Tkinter import *
from decimal import *
import Queue, time, thread
#import RPi.GPIO as GPIO

#naming conventions so I dont get confused later:
#a cocktail is a drink that has shots, a name, and an owner
#a drink is an alcoholic beverage (like vodka, rum, etc)
a = 7
b = 11
c = 12
d = 13
e = 15
f = 16
g = 18
h = 22
coil_A_1_pin = 7
coil_A_2_pin = 11
coil_B_1_pin = 16
coil_B_2_pin = 18
    
class User:
    totalDrinks = 0
    userLimit = 0
    nameOfUser = ""
    # the only constructor we need as of right now
    def __init__ (self, userLimit, nameOfUser):
        self.userLimit = userLimit
        self.nameOfUser = nameOfUser

#Brian = User(10, "Brian")    
class Cocktail:
    amtOfShots = [0, 0, 0, 0, 0, 0, 0, 0]
    nameOfCocktail = ""
    nameOfOwner = ""
    #these are the different constructors for the class objects
    # the amtOfShots and nameOfOwner in the () are just the parameters passed
    #to the constructor and then assigned to members of class object
    def __init__ (self, amtOfShots, nameOfOwner):
        self.amtOfShots = amtOfShots
        self.nameOfOwner = nameOfOwner
    def __init__ (self, amtOfShots, nameOfOwner, nameOfCocktail):
        self.amtOfShots = amtOfShots
        self.nameOfOwner = nameOfOwner
        self.nameOfCocktail = nameOfCocktail

class Application(Frame):

    #define all types of premade Cocktails here
    longIslandIcedTea = Cocktail([1, 1, 1, 1, 0, 0, 0, 0], "", "Long Island Iced Tea") # look we do NOT include self. we used the '4' parameter constructor and entered 4 because self is not one
    graveyard = Cocktail([1, 1, 1, 1, 1, 1, 1, 1], "", "The Graveyard")
    customDrink = Cocktail([0, 0, 0, 0, 0, 0, 0, 0], "", "Custom Drink")
    #Derp = Cocktail([0, 0, 0, 0, 0, 0, 0, 1], "", "Derp")

    #declare user, although going to want to have these inputed later
    Brian = User(10, "Brian")

    #add all the cocktails into the known cocktail list
    knownCocktailList = []
    knownCocktailList.append(longIslandIcedTea)
    knownCocktailList.append(graveyard)
    knownCocktailList.append(customDrink)
    #knownCocktailList.append(Derp)
    
    #Queue of cocktails that users are requesting
    cocktailQueue = Queue.Queue(16)

    # the list of users
    userList = []

    #keep track of things in the GUI, like the current drink selected
    currentDrinkSelected = 1
    shotAmountEntryFields = []

    #keep track of the list of drinks
    drinkList = ['Vodka', 'Gin', 'Tequila', 'Rum', 'Drink 5', 'Drink 6', 'Drink 7', 'Drink 8']

    #wait for drink to be taken
    isDrinkTaken = False

    #RPi constants
    

    def __init__(self, master):
        #set up gui
        Frame.__init__(self, master)
        self.grid()        
        self.leftSide = Frame(self)
        self.leftSide.grid(row=1, column=0, rowspan=20)         
        self.createWidgets()
        #set up RPi

        #GPIO.setmode(GPIO.BOARD)
        #GPIO.setup(a, GPIO.OUT)
        #GPIO.setup(b, GPIO.OUT)
        #GPIO.setup(self.c, GPIO.OUT)
        #GPIO.setup(self.d, GPIO.OUT)
        #GPIO.setup(self.e, GPIO.OUT)
        #GPIO.setup(f, GPIO.OUT)
        #GPIO.setup(g, GPIO.OUT)
        #GPIO.setup(self.h, GPIO.OUT)
        #GPIO.setup(self.coil_A_1_pin, GPIO.OUT)
        #GPIO.setup(self.coil_A_2_pin, GPIO.OUT)
        #GPIO.setup(self.coil_B_1_pin, GPIO.OUT)
        #GPIO.setup(self.coil_B_2_pin, GPIO.OUT)

    def createColumnHeadings(self):
        #creating headings
        i = 0
        for text in ['Drink Queue', 'Known Drinks', 'Shots Each']:
            Label(self, text=text, font=("Helvetica", 30)).grid(row=0, column=i, sticky=W, padx=100, pady=30)
            i = i + 1

    def createDrinkQueueBox(self):
        self.queue=Text(self.leftSide, height=15, width=30,font=("Helvetica", 15), wrap=NONE)
        self.queue.insert("0.1", "Drinks will be queued up here")
        self.queue.config(state=DISABLED)
        self.queue.grid(row=3, column=0)

    def createRadioButtons(self):
        self.currentDrinkSelected = IntVar()
        i = 1
        for cocktail in self.knownCocktailList:
            Radiobutton(self, text=cocktail.nameOfCocktail, variable=self.currentDrinkSelected, value=i, command=self.determineDrinks).grid(row=i, column=1)
            i = i + 1

    def resetTextBox(self):
        for i in range(8):
            self.shotAmountEntryFields[i].config(state=NORMAL)
            self.shotAmountEntryFields[i].delete(0, END)
            self.shotAmountEntryFields[i].config(state=DISABLED)

    def determineDrinks(self):
        self.resetTextBox()
        currentCocktail = self.knownCocktailList[self.currentDrinkSelected.get() - 1]
        for i in range(8):
            self.shotAmountEntryFields[i].config(state=NORMAL)
            self.shotAmountEntryFields[i].insert(0, currentCocktail.amtOfShots[i])
            self.shotAmountEntryFields[i].config(state=DISABLED)
            if currentCocktail.nameOfCocktail == "Custom Drink":
                self.shotAmountEntryFields[i].config(state=NORMAL)

    def createEntryFields(self):
        i=0
        for drink in self.drinkList:
            Label(self, text=drink).grid(row=i+1,column=2,sticky=W)
            self.shotAmountEntryFields.append(Entry(self))
            self.shotAmountEntryFields[i].grid(row=i+1, column=2)
            self.shotAmountEntryFields[i].insert(0, 0)
            self.shotAmountEntryFields[i].config(state=DISABLED)
            i = i + 1


    def addToQueue(self):
        if not self.cocktailQueue.full():
            currentCocktail = self.knownCocktailList[self.currentDrinkSelected.get() - 1]
            tempShotList = []
            totalShots = 0
            for i in range(8):
                tempShotList.append(self.shotAmountEntryFields[i].get()) # temp shot list is an 8 element array. same constructor as the listed drinks like long island ice tea from above.
                totalShots = totalShots + int(self.shotAmountEntryFields[i].get())
            
            for i in range(0, len(self.userList)):
                if self.userList[i].nameOfUser == self.currentUserName.get():
                    userID = i
                    
                    if self.userList[userID].totalDrinks + totalShots <= self.userList[userID].userLimit:
                        self.userList[userID].totalDrinks = self.userList[userID].totalDrinks + totalShots
                        newDrink = Cocktail(tempShotList, self.currentUserName.get(), currentCocktail.nameOfCocktail)
                        self.cocktailQueue.put(newDrink)
                        self.printQueue()
                        break
                    else:
                        self.messageBox.delete(0,len(self.messageBox.get()))
                        self.messageBox.insert(0,"Too much alcohol")
                        break
                    
                
                    
            

    def addUser(self):
        validName = True
        for i in range(0, len(self.userList)):
            if self.userList[i].nameOfUser == self.enterUserName.get():
                validName = False
                self.messageBox.delete(0,len(self.messageBox.get()))
                self.messageBox.insert(0,"The name is taken")
                break
            
        if validName == True and self.currentLimit.get() != "": # if name is valid and number limit != ""
            newUser = User(int(self.currentLimit.get()), self.enterUserName.get())
            self.userList.append(newUser)

        self.enterUserName.delete(0,len(self.enterUserName.get()))
        self.currentLimit.delete(0,len(self.currentLimit.get()))
        

    def removeFromQueue(self):
        if self.cocktailQueue.qsize() > 0:
            self.cocktailQueue.get()
            self.printQueue()

    def startMaking(self):
        thread.start_new_thread(self.makeDrink, ())

    def isNextDrink(self, currentDrink, currentCocktail):
        if currentDrink > 7:
            return False
        else:
            return (currentCocktail.amtOfShots[currentDrink] > 0 or self.isNextDrink(currentDrink + 1, currentCocktail))

    def forward(self, delay, steps):  
        for i in range(0, steps):
            self.setStep(1, 0, 1, 0)
            time.sleep(delay)
            self.setStep(0, 1, 1, 0)
            time.sleep(delay)
            self.setStep(0, 1, 0, 1)
            time.sleep(delay)
            self.setStep(1, 0, 0, 1)
            time.sleep(delay)

    def backwards(self, delay, steps):  
        for i in range(0, steps):
            self.setStep(1, 0, 0, 1)
            time.sleep(delay)
            self.setStep(0, 1, 0, 1)
            time.sleep(delay)
            self.setStep(0, 1, 1, 0)
            time.sleep(delay)
            self.setStep(1, 0, 1, 0)
            time.sleep(delay)
      
    def setStep(self, w1, w2, w3, w4):
        GPIO.output(self.coil_A_1_pin, w1)
        GPIO.output(self.coil_A_2_pin, w2)
        GPIO.output(self.coil_B_1_pin, w3)
        GPIO.output(self.coil_B_2_pin, w4)

    def makeDrink(self):
        while not self.cocktailQueue.empty():
            #c,d,e,h
            currentCocktail = self.cocktailQueue.get()
            for i in range(8):
                if self.isNextDrink(i, currentCocktail):
                    #self.forward(.005, 7)
                    if currentCocktail.amtOfShots[i] > 0:
                        #GPIO.output(self.c, True)
                        time.sleep(int(1 * currentCocktail.amtOfShots[i]))
                        #GPIO.output(self.c, False)
                else:
                    #self.backwards(.005, 7 * i)
                    break
            self.waitForDrinkTaken()

    def waitForDrinkTaken(self):
        self.currentlyMaking.config(state=NORMAL)
        self.currentlyMaking.delete(0, END)
        self.currentlyMaking.insert(0, "Drink Ready. Press Take Drink")
        self.currentlyMaking.config(state=DISABLED)
        while not self.isDrinkTaken:
            time.sleep(1)
        self.isDrinkTaken = False
        self.printQueue()

    def takeDrink(self):
        self.isDrinkTaken = True

    def printQueue(self):
        self.queue.config(state=NORMAL)
        self.currentlyMaking.config(state=NORMAL)
        self.currentlyMaking.delete(0, END)
        self.queue.delete("0.1", END)
        if not self.cocktailQueue.empty():
            self.currentlyMaking.insert(0, self.cocktailQueue.queue[0].nameOfCocktail + " - " + self.cocktailQueue.queue[0].nameOfOwner)
        self.currentlyMaking.config(state=DISABLED)
        for i in range(1, self.cocktailQueue.qsize()):
            self.queue.insert("0.1", self.cocktailQueue.queue[self.cocktailQueue.qsize() - i].nameOfCocktail + " - " + self.cocktailQueue.queue[self.cocktailQueue.qsize() - i].nameOfOwner + "\n")
        self.queue.config(state=DISABLED)

    
    def createWidgets(self):
        #creating headings
        self.createColumnHeadings()

        #create giant "Drink Queue" text box
        self.createDrinkQueueBox()

        #create radio buttons
        self.createRadioButtons()

        #create entry fields
        self.createEntryFields()

        #make the "Currently Making" box
        self.currentlyMaking = Entry(self.leftSide, font=("Helvetica", 15), width=30)
        self.currentlyMaking.config(state=DISABLED)
        self.currentlyMaking.grid(row=1, column=0, pady=10)
        Label(self.leftSide, text="Currently Making:").grid(row=0, column=0)

        #make the "Name" box
        Label(self, text="Enter your name for the drink:").grid(row=38, column=1, sticky=W)
        self.currentUserName = Entry(self)
        self.currentUserName.grid(row=39, column=1, sticky=W)

        #this is textbox where user name is taken from
        Label(self, text="Enter New User Name").grid(row=36, column=2)
        self.enterUserName = Entry(self)
        self.enterUserName.grid(row=37, column=2)

        #this is textbox where drink limit is taken from
        Label(self, text="Enter drink limit:").grid(row=38, column=2)
        self.currentLimit = Entry(self)
        self.currentLimit.grid(row=39, column=2)

        #this is textbox where drink limit is taken from
        Label(self, text="Error Message Box").grid(row=39, column=0)
        self.messageBox = Entry(self)
        self.messageBox.grid(row=40, column=0)
    
        
        #bottom row of buttons
        Button(self, text="Add drink to queue", command=self.addToQueue).grid(column=1, row=40, sticky=W)
        Button(self, text="Take drink", command=self.takeDrink).grid(column=1, row=40, sticky=E)
        Button(self, text="Begin making", command=self.startMaking).grid(column=1, row=40)
        
        Button(self, text="Add User", command=self.addUser).grid(row=35, column=2)


#necessary crap to actually start program
root = Tk()
root.title("Drink Menu")
root.geometry("1368x766")

app = Application(root)

app.mainloop()

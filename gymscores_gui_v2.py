# from tkinter import *
import sqlite3 as sq
import datetime
import tkinter
import tkinter.ttk

window = tkinter.Tk()
window.title('gymscores')

# Create Autocomplete Class
class AutocompleteCombobox(tkinter.ttk.Combobox):

        def set_completion_list(self, completion_list):
                """Use our completion list as our drop down selection menu, arrows move through menu."""
                self._completion_list = sorted(completion_list, key=str.lower) # Work with a sorted list
                self._hits = []
                self._hit_index = 0
                self.position = 0
                self.bind('<KeyRelease>', self.handle_keyrelease)
                self['values'] = self._completion_list  # Setup our popup menu

        def autocomplete(self, delta=0):
                """autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
                if delta: # need to delete selection otherwise we would fix the current position
                        self.delete(self.position, tkinter.END)
                else: # set position to end so selection starts where textentry ended
                        self.position = len(self.get())
                # collect hits
                _hits = []
                for element in self._completion_list:
                        if element.lower().startswith(self.get().lower()): # Match case insensitively
                                _hits.append(element)
                # if we have a new hit list, keep this in mind
                if _hits != self._hits:
                        self._hit_index = 0
                        self._hits=_hits
                # only allow cycling if we are in a known hit list
                if _hits == self._hits and self._hits:
                        self._hit_index = (self._hit_index + delta) % len(self._hits)
                # now finally perform the auto completion
                if self._hits:
                        self.delete(0,tkinter.END)
                        self.insert(0,self._hits[self._hit_index])
                        self.select_range(self.position,tkinter.END)

        def handle_keyrelease(self, event):
                """event handler for the keyrelease event on this widget"""
                if event.keysym == "BackSpace":
                        self.delete(self.index(tkinter.INSERT), tkinter.END)
                        self.position = self.index(tkinter.END)
                if event.keysym == "Left":
                        if self.position < self.index(tkinter.END): # delete the selection
                                self.delete(self.position, tkinter.END)
                        else:
                                self.position = self.position-1 # delete one character
                                self.delete(self.position, tkinter.END)
                if event.keysym == "Right":
                        self.position = self.index(tkinter.END) # go to end (no selection)
                if len(event.keysym) == 1:
                        self.autocomplete()
                # No need for up/down, we'll jump to the popup
                # list at the position of the autocompletion

# Connect to DB
conn = sq.connect('gymscorestest - working copy test.db')
# create cursor
c = conn.cursor()
# select all athletes FX scores and format
fxScores = c.execute("""
        SELECT athletes.first_name AS [First Name],
           athletes.last_name AS [Last Name],
           competitions.name AS Competition,
           fx_d AS [FX D-Score],
           fx_e AS [FX E-Score],
           fx_pen AS [FX Penalty],
           fx_final AS [FX Score]
         FROM scores
           INNER JOIN
           athletes ON athletes.athletes_id = scores.athletes_id
           INNER JOIN
           competitions ON competitions.competitions_id = scores.competitions_id
        """)


def submit():
	# Clear text boxes
	fxD.delete(0, END)
	fxE.delete(0, END)
	fxPen.delete(0, END)
	fxFinal.delete(0, END)
	phD.delete(0, END)
	phE.delete(0, END)
	phPen.delete(0, END)
	phFinal.delete(0, END)
	srD.delete(0, END)
	srE.delete(0, END)
	srPen.delete(0, END)
	srFinal.delete(0, END)

	# Insert into db
	# Connect to DB
	conn = sq.connect('gymscorestest - working copy test.db')
	# create cursor
	c = conn.cursor()

	# insert into table scores
	c.execute("INSERT INTO scores VALUES(:athlete,:competition,:fxD,:fxE,:fxPen,:fxFinal)",
		{
			'athlete':athletes.get(),
			'competition':competitions.get(),
			'fxD':fxD.get(),
			'fxE':fxE.get(),
			'fxPen':fxPen.get(),
			'fxFinal':fxFinal.get()
		})

	# commit changes
	conn.commit()
	# close connection to db
	conn.close()

# Create query function
def query():
	# Connect to DB
	conn = sq.connect('gymscorestest - working copy test.db')
	# create cursor
	c = conn.cursor()

	# c.execute("SELECT * FROM scores")
	c.execute("""
		SELECT athletes.first_name AS [First Name],
           athletes.last_name AS [Last Name],
           competitions.name AS Competition,
           fx_d AS [FX D-Score],
           fx_e AS [FX E-Score],
           fx_pen AS [FX Penalty],
           fx_final AS [FX Score]
      FROM scores
           INNER JOIN
           athletes ON athletes.athletes_id = scores.athletes_id
           INNER JOIN
           competitions ON competitions.competitions_id = scores.competitions_id
		""")
	records = c.fetchall()

	# Loop through results and print them
	print_records = ''
	for record in records:
		print_records += str(record) + "\n"

	query_label = tkinter.Label(window, text=print_records)
	query_label.pack()

	# commit changes
	conn.commit()
	# close connection to db
	conn.close()
def openNewWindow():
    queryWindow = tkinter.Tk()
    records = fxScores.fetchall()
    # Loop through results and print them
    print_records = ''
    for record in records:
        print_records += str(record) + "\n"

    query_label = tkinter.Label(queryWindow, text=print_records)
    query_label.pack()


# Header
header = tkinter.Label(window, text='GymScores Form', font=('arial',24,'bold'))
header.pack()

# Competitions & Athletes Frame
competitionsFrame = tkinter.LabelFrame(window,text="Competitions and Athletes", font=('arial',12,'bold'))
competitionsFrame.pack()

L1 = tkinter.Label(competitionsFrame, text = 'Competition')
L2 = tkinter.Label(competitionsFrame, text = 'Athlete')

L1.grid(row=1,column=0)
L2.grid(row=2,column=0)

# Get Competitions from DB
competitions = []
conn = sq.connect('gymscorestest - working copy test.db')
c = conn.cursor()	
c.execute("SELECT substr(DATESTART,7,4)||' '||TITLE||' '||CITY||' '||COUNTRY FROM fig_comps ORDER BY substr(DATESTART,7,4),TITLE ASC")
compRecords = c.fetchall()
for compRecord in compRecords:
	data = "%s" % compRecord[0]
	competitions.append(data)
	# print(data)

compOption = tkinter.StringVar(competitionsFrame)
compOption.set(competitions[0])
comps = tkinter.OptionMenu(competitionsFrame, compOption, *competitions)
comps.config(width=75)
comps.grid(row=1,column=1,columnspan=3)
# commit changes
conn.commit()
# close connection to db
conn.close()

# Get Athletesfrom DB
athletes =[]
conn = sq.connect('gymscorestest - working copy test.db')
c = conn.cursor()	
c.execute("SELECT GIVENNAME,SURNAME FROM fig_athletes WHERE STATUS='active' ORDER BY SURNAME ASC")
athleteRecords = c.fetchall()
for athleteRecord in athleteRecords:
	data = "%s %s" % (athleteRecord[0],athleteRecord[1])
	athletes.append(data)
	# print(data)

athlOption = tkinter.StringVar(competitionsFrame)
athlOption.set(athletes[0])
# athls = OptionMenu(competitionsFrame, athlOption, *athletes)
# athls.grid(row=2,column=1,columnspan=3)

athlEntry = AutocompleteCombobox(competitionsFrame,width=55)
athlEntry.set_completion_list(athletes)
athlEntry.grid(row=2,column=1,columnspan=3)
athlEntry.focus_set()
# commit changes
conn.commit()
# close connection to db
conn.close()

# Scores Frame
scoresFrame = tkinter.LabelFrame(window,text="Scores", font=('arial',12, 'bold'), padx=10, pady=10)
scoresFrame.pack()

# FX
# tkinter.Labels
Lfx = tkinter.Label(scoresFrame, text = 'FX', font=('arial',18))
LfxD = tkinter.Label(scoresFrame, text='FX D-Score')
LfxE = tkinter.Label(scoresFrame, text='FX E-Score')
LfxPen = tkinter.Label(scoresFrame, text='FX Penalty')
LfxFinal = tkinter.Label(scoresFrame, text='FX Score')
# Entries
fxD = tkinter.Entry(scoresFrame, width=8, borderwidth=2)
fxE = tkinter.Entry(scoresFrame, width=8, borderwidth=2)
fxPen = tkinter.Entry(scoresFrame, width=8, borderwidth=2)
fxFinal = tkinter.Entry(scoresFrame, width=8, borderwidth=2)
# Place on grid
Lfx.grid(row=4,column=0,rowspan=2)
LfxD.grid(row=4,column=1)
LfxE.grid(row=4,column=2)
LfxPen.grid(row=4,column=3)
LfxFinal.grid(row=4,column=4)
fxD.grid(row=5,column=1)
fxE.grid(row=5,column=2)
fxPen.grid(row=5,column=3)
fxFinal.grid(row=5,column=4)


# PH
Lph = tkinter.Label(scoresFrame, text = 'PH', font=('arial',16))
LphD = tkinter.Label(scoresFrame, text='PH D-Score')
LphE = tkinter.Label(scoresFrame, text='PH E-Score')
LphPen = tkinter.Label(scoresFrame, text='PH Penalty')
LphFinal = tkinter.Label(scoresFrame, text='PH Score')
phD = tkinter.Entry(scoresFrame, width=8, borderwidth=2)
phE = tkinter.Entry(scoresFrame, width=8, borderwidth=2)
phPen = tkinter.Entry(scoresFrame, width=8, borderwidth=2)
phFinal = tkinter.Entry(scoresFrame, width=8, borderwidth=2)
# Place on grid
Lph.grid(row=6,column=0,rowspan=2)
LphD.grid(row=6,column=1)
LphE.grid(row=6,column=2)
LphPen.grid(row=6,column=3)
LphFinal.grid(row=6,column=4)
phD.grid(row=7,column=1)
phE.grid(row=7,column=2)
phPen.grid(row=7,column=3)
phFinal.grid(row=7,column=4)

# SR
Lsr = tkinter.Label(scoresFrame, text = 'SR', font=('arial',16))
LsrD = tkinter.Label(scoresFrame, text='SR D-Score')
LsrE = tkinter.Label(scoresFrame, text='SR E-Score')
LsrPen = tkinter.Label(scoresFrame, text='SR Penalty')
LsrFinal = tkinter.Label(scoresFrame, text='SR Score')
srD = tkinter.Entry(scoresFrame, width=8, borderwidth=2)
srE = tkinter.Entry(scoresFrame, width=8, borderwidth=2)
srPen = tkinter.Entry(scoresFrame, width=8, borderwidth=2)
srFinal = tkinter.Entry(scoresFrame, width=8, borderwidth=2)
# Place on grid
Lsr.grid(row=8,column=0,rowspan=2)
LsrD.grid(row=8,column=1)
LsrE.grid(row=8,column=2)
LsrPen.grid(row=8,column=3)
LsrFinal.grid(row=8,column=4)
srD.grid(row=9,column=1)
srE.grid(row=9,column=2)
srPen .grid(row=9,column=3)
srFinal.grid(row=9,column=4)

# VT
L7 = tkinter.Label(scoresFrame, text = 'VT', font=('arial',16)).grid(row=10,column=0,rowspan=4)
L7vtD = tkinter.Label(scoresFrame, text='VT D-Score').grid(row=10,column=1)
L7vtE = tkinter.Label(scoresFrame, text='VT E-Score').grid(row=10,column=2)
L7vtPen = tkinter.Label(scoresFrame, text='VT Penalty').grid(row=10,column=3)
L7vtFinal = tkinter.Label(scoresFrame, text='VT Score').grid(row=10,column=4)
# next row
vtD = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=11,column=1)
vtE = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=11,column=2)
vtPen = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=11,column=3)
vtFinal = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=11,column=4)
# next row
vtxD = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=12,column=1)
vtxE = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=12,column=2)
vtxPen = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=12,column=3)
vtxFinal = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=12,column=4)
# Cumulative Final Score if doing 2 vaults
vtfFinal = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=13,column=4)

# PB
L8 = tkinter.Label(scoresFrame, text = 'PB', font=('arial',16)).grid(row=14,column=0,rowspan=2)
L8pbD = tkinter.Label(scoresFrame, text='PB D-Score').grid(row=14,column=1)
L8pbE = tkinter.Label(scoresFrame, text='PB E-Score').grid(row=14,column=2)
L8pbPen = tkinter.Label(scoresFrame, text='PB Penalty').grid(row=14,column=3)
L8pbFinal = tkinter.Label(scoresFrame, text='PB Score').grid(row=14,column=4)
# next row
pbD = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=15,column=1)
pbE = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=15,column=2)
pbPen = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=15,column=3)
pbFinal = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=15,column=4)

# HB
L9 = tkinter.Label(scoresFrame, text = 'HB', font=('arial',16)).grid(row=16,column=0,rowspan=2)
L9hbD = tkinter.Label(scoresFrame, text='HB D-Score').grid(row=16,column=1)
L9hbE = tkinter.Label(scoresFrame, text='HB E-Score').grid(row=16,column=2)
L9hbPen = tkinter.Label(scoresFrame, text='HB Penalty').grid(row=16,column=3)
L9hbFinal = tkinter.Label(scoresFrame, text='HB Score').grid(row=16,column=4)
# next row
hbD = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=17,column=1)
hbE = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=17,column=2)
hbPen = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=17,column=3)
hbFinal = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=17,column=4)

# AA
L10 = tkinter.Label(scoresFrame, text = 'AA', font=('arial',16)).grid(row=18,column=0,rowspan=2)
L10aaD =  tkinter.Label(scoresFrame, text='AA D-Score').grid(row=18,column=1)
L10aaFinal =  tkinter.Label(scoresFrame, text='AA Score').grid(row=18,column=2)
# next row
aaD = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=19,column=1)
aaFinal = tkinter.Entry(scoresFrame, width=8, borderwidth=2).grid(row=19,column=2)

submitButton = tkinter.Button(window, text='Submit', command=submit).pack()

# Create a query
query_btn = tkinter.Button(window, text="Show DB", command=query)
query_btn.pack()

# Open new window button
newWindow_btn = tkinter.Button(window, text="Open New Window", command=openNewWindow)
newWindow_btn.pack()

# # yearT = tkinter.Entry(window, textvariable=year)
# # yearT.place(x=220,y=255)
# # weightT = tkinter.Entry(window, textvariable=weight)
# # weightT.place(x=220,y=305)
# # repT = tkinter.Entry(window, textvariable=reps)
# # repT.place(x=220,y=355)

window.mainloop()

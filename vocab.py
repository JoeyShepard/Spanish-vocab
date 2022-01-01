from os import system
from msvcrt import getch
from sys import exit
from random import random,seed
from time import time

#Constants
#=========
SCORE_RESET=1       #If user gets wrong, set to this
SCORE_MAX=5         #Highest possible score
SCORE_REVIEW=3      #Reset to this if randomly selected for review on load
SCORE_MIN_SIZE=20   #Minimum number seen 1-3 times to keep in rotation

DEBUG=False

#Setup
#=====
seed()
word_limit=0
time_limit=0
spaceman_lvl=0
spaceman_exp=0

#Console colors
#==============
colors={"black":    "\u001b[30m",
        "red":      "\u001b[31m",
        "green":    "\u001b[32m",
        "yellow":   "\u001b[33m",
        "blue":     "\u001b[34m",
        "magenta":  "\u001b[35m",
        "cyan":     "\u001b[36m",
        "white":    "\u001b[37m"
        }

temp_dict={}
for name,color in colors.items():
    temp_dict["bright "+name]=color[:-1]+";1m"
colors|=temp_dict
colors["reset"]="\u001b[0m"

system("color")

def printc(msg,color):
    print(colors[color]+msg+colors["reset"],end="")

#Read in words
#=============
replacements_1={"\\\\u":    "\u00fc",
                "\\\\U":    "\u00dc"
                }
replacements_2={"\\a":      "\u00e1",
                "\\e":      "\u00e9",
                "\\i":      "\u00ed",
                "\\n":      "\u00f1",
                "\\o":      "\u00f3",
                "\\u":      "\u00fa",
                "\\A":      "\u00c1",
                "\\E":      "\u00c9",
                "\\I":      "\u00cd",
                "\\N":      "\u00d1",
                "\\O":      "\u00d3",
                "\\U":      "\u00da",
                "\\!":      "\u00a1",
                "\\?":      "\u00bf"
                }
                
words={}
with open("vocab.txt") as f:
    for line in f.readlines():
        new_line=line.strip()
        
        #Skip empty lines
        if new_line=="":
            continue
        
        #Replace slashed characters
        for d in [replacements_1,replacements_2]:
            for k,v in d.items():
                new_line=new_line.replace(k,v)
        
        #Separate Spanish from English
        index=new_line.find(" - ")
        if index!=-1:
            spanish=new_line[:index]
            english=new_line[index+3:]
        else:
            spanish=new_line
            english=""
        
        #Add to list of words
        if spanish in words:
            words[spanish]["english"]+="\n"+english
        else:
            words[spanish]={}
            words[spanish]["english"]=english
            words[spanish]["score_spanish"]=0
            words[spanish]["score_english"]=0
    print(str(len(words))+" words loaded")
    
#Read in scores
#==============
def rand_int(max_int):
    return int(random()*(max_int))
    
STATE_WORD=0
STATE_SCORE_SPANISH=1
STATE_SCORE_ENGLISH=2
score_state=STATE_WORD
score_matched=0
score_unmatched=0
#Try to open scores file and create it if it doesn't exist
try:
    f=open("scores.txt")
except:
    f=open("scores.txt","wt")
    f.close()
    f=open("scores.txt")
for line in f.readlines():
    line=line.strip()
    if score_state==STATE_WORD:
        temp_word=line
        if temp_word in words:
            score_matched+=1
        else:
            score_unmatched+=1
        score_state=STATE_SCORE_SPANISH
    elif score_state==STATE_SCORE_SPANISH:
        if temp_word in words:
            temp_score=int(line)
            words[temp_word]["score_spanish"]=temp_score
        score_state=STATE_SCORE_ENGLISH
    elif score_state==STATE_SCORE_ENGLISH:
        if temp_word in words:
            temp_score=int(line)
            words[temp_word]["score_english"]=temp_score
        score_state=STATE_WORD
        
print(str(score_matched)+" scores loaded")
if score_unmatched>0:
    printc(str(score_unmatched)+" scores without matching word!\n","yellow")
f.close()

#Select random word
#==================
def rand_score(which):
    #First, make sure there are enough words seen 1-3 times
    if len([k for k,v in words.items() if v[which] in [1,2,3]])<SCORE_MIN_SIZE:
        #Use unseen words if there are any
        if len([k for k,v in words.items() if v[which]==0])!=0:
            return 0
        #Return 4 or 5 if not enough seen 1-3 times and no unseen left
        else:
            return rand_int(2)+4
    
    temp_rand=rand_int(20)
    #5% chance to introduce new word
    if temp_rand==0:
        return 0
    #80% chance to practise word seen 1-3 times
    elif temp_rand<17:
        return rand_int(3)+1
    #10% chance to practice word seen 4 times
    elif temp_rand<19:
        return 4
    #5% chance to practice word seen 5 times
    else:
        return 5
        
#Input loop
#==========
STATE_MENU=0
STATE_SPANISH=1
STATE_ENGLISH=2
input_state=STATE_MENU

def GetKey():
    key=getch()
    if key==b'\x03':
        print("^C",end="")
        exit()
    return key.decode("utf-8").lower()

def DrawMenu():
    menu=[  "Review Spanish words",
            "Review English words",
            "Set word limit",
            "Set time limit"
            ]
    print()
    for i,item in enumerate(menu):
        print(str(i+1)+". "+item)
        if item=="Review Spanish words": 
            print("   ",end="")
            PrintCounts("score_spanish")
        elif item=="Review English words": 
            print("   ",end="")
            PrintCounts("score_english")
    print()
    print("Select a number or press q to quit")

def Spaceman(amount):
    #print(amount)
    return

def PrintCounts(which_score):
    global words
    counts=""
    for i in range(6):
        counts+=str(i)+":"+str(len([k for k,v in words.items() if v[which_score]==i]))
        if i!=5:
            counts+=", "
    print("Counts: "+counts)

def HandleKeys(which_score,input_state):
    global words_left, words
    global end_time, time_left
    global score_correct, score_total   
    
    PrintCounts(which_score)
    print("Mark as known [y/n]? q to quit")
    
    limit_expired=False
    if end_time!=0:
        time_left=end_time-time()
        if time_left<=0:
            print("Time expired! "+str(time_limit)+" minutes")
            limit_expired=True
        else:
            print("Time left: "+str(int(time_left/60))+":"+("0"+str(int(time_left%60)))[-2:])
    if words_left!=0:
        words_left-=1
        if words_left==0:
            print("Words finished!")
            limit_expired=True
        else:
            print("Words left: "+str(words_left))
    
    exit_loop=False
    while exit_loop==False:
        key=GetKey()
        if key=='y' or key=='\r':
            score_correct+=1
            score_total+=1
            words[rand_spanish][which_score]+=1
            if words[rand_spanish][which_score]>SCORE_MAX:
                words[rand_spanish][which_score]=SCORE_MAX
            Spaceman(3)
            exit_loop=True
        elif key=='n':
            score_total+=1
            words[rand_spanish][which_score]=SCORE_RESET
            Spaceman(-1)
            exit_loop=True
        
        if key=='q' or (limit_expired and exit_loop):
            if score_total!=0:
                print()
                print("Results: ",end="")
                printc(str(score_correct)+" correct ","bright green")
                print("out of "+str(score_total)+". ("+str(round(100*score_correct/score_total,2))+"%)")
            
            #Write scores out to file
            with open("scores.txt","wt") as f:
                for k,v in words.items():
                    f.write(k+"\n")
                    f.write(str(v["score_spanish"])+"\n")
                    f.write(str(v["score_english"])+"\n")
            input_state=STATE_MENU
            DrawMenu()
            exit_loop=True
    return input_state
    
DrawMenu()

while True:
    if input_state==STATE_MENU:
        key=GetKey()
        if key=='q':
            exit()
        elif key=='1':
            score_total=0
            score_correct=0
            rand_spanish=""
            last_word=""
            words_left=word_limit
            spaceman_lvl=1
            spaceman_exp=0
            #5% chance to put word seen max times back into rotation
            for k,v in words.items():
                if v["score_spanish"]==SCORE_MAX: 
                    if rand_int(20)==0:
                        words[k]["score_spanish"]=1
            if time_limit!=0:
                end_time=time()+time_limit*60
            else:
                end_time=0
            input_state=STATE_SPANISH
        elif key=='2':
            score_total=0
            score_correct=0
            rand_spanish=""
            last_word=""
            words_left=word_limit
            spaceman_lvl=1
            spaceman_exp=0
            #5% chance to put word seen max times back into rotation
            for k,v in words.items():
                if v["score_english"]==SCORE_MAX: 
                    if rand_int(20)==0:
                        words[k]["score_english"]=1
            if time_limit!=0:
                end_time=time()+time_limit*60
            else:
                end_time=0
            input_state=STATE_ENGLISH
        elif key=='3':
            word_limit=int(input("Word limit: "))
            DrawMenu()
        elif key=='4':
            time_limit=int(input("Time limit (minutes): "))
            DrawMenu()
    
    if input_state==STATE_SPANISH:
        print()
        rand_words=[]
        #Don't show same word twice in a row
        while last_word==rand_spanish:
            while rand_words==[]:
                temp_score=rand_score("score_spanish")
                rand_words=[k for k,v in words.items() if v["score_spanish"]==temp_score]
            rand_index=rand_int(len(rand_words))
            rand_spanish=rand_words[rand_index]
            rand_words=[]
        last_word=rand_spanish
        printc(rand_spanish+"\n","bright blue")
        
        rand_english=words[rand_spanish]["english"]
        if rand_english!="":
            while GetKey()!='\r':
                continue
            printc(rand_english+"\n","green")
        input_state=HandleKeys("score_spanish",input_state)
                
    elif input_state==STATE_ENGLISH:
        print()
        rand_words=[]
        #Don't show same word twice in a row
        while last_word==rand_spanish:
            while rand_words==[]:
                temp_score=rand_score("score_english")
                rand_words=[k for k,v in words.items() if v["score_english"]==temp_score]
            rand_index=rand_int(len(rand_words))
            rand_spanish=rand_words[rand_index]
            rand_words=[]
        last_word=rand_spanish
        
        rand_english=words[rand_spanish]["english"]
        english_words=[]
        for k,v in words.items():
            if v["english"]==rand_english:
                english_words+=[k]
        if rand_english!="":
            printc(rand_english,"green")
            if len(english_words)>1:
                print(" (x"+str(len(english_words))+")")
            else:
                print()
            while GetKey()!='\r':
                continue
        #printc(rand_spanish+"\n","bright blue")
        for word in english_words:
            printc(word+"\n","bright blue")
        input_state=HandleKeys("score_english",input_state)
        

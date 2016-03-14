from __future__ import division

from collections import namedtuple
from Tkinter import *
from ttk import *

import sys

if TkVersion < 8.0 :
    print "Needs at least TkVersion 8.0"
    sys.exit(0)

import string
import random
import time
import pprint
import time
import itertools

#ninja'ed and modified StopWatch from code.activestate.com under PSL
class StopWatch():  
    """ Implements a stop watch frame widget. """                                                                
    def __init__(self, parent):        
        self.root = parent
        self._start = 0.0        
        self._elapsedtime = 0.0
        self.running = 0
        self.root.timestr = StringVar()     
    def _update(self): 
        """ Update the label with elapsed time. """
        self._elapsedtime = time.time() - self._start
        self._setTime(self._elapsedtime)
        self._timer = self.root.after(50, self._update)
    
    def _setTime(self, elap):
        """ Set the time string to Minutes:Seconds:Hundreths """
        minutes = int(elap/60)
        seconds = int(elap - minutes*60.0)
        hseconds = int((elap - minutes*60.0 - seconds)*100)                
        self.root.timestr.set('%02d:%02d:%02d' % (minutes, seconds, hseconds))
        
    def Start(self):                                                     
        """ Start the stopwatch, ignore if running. """
        if not self.running:            
            self._start = time.time() - self._elapsedtime
            self._update()
            self.running = 1        
    
    def Stop(self):                                    
        """ Stop the stopwatch, ignore if stopped. """
        if self.running:
            self.root.after_cancel(self._timer)            
            self._elapsedtime = time.time() - self._start    
            self._setTime(self._elapsedtime)
            self.running = 0
    
    def Cycle(self, event):    
        if self.running:
            self.Stop()
        else:
            self.Start()

    def Reset(self):                                  
        """ Reset the stopwatch. """
        self._start = time.time()         
        self._elapsedtime = 0.0    
        self._setTime(self._elapsedtime)

class Game:
    def __init__(self, parent):
        self.level = StringVar()
        self.answered = StringVar()
        self.answered.set('0')
        self.level.set('1')
	self.stopwatch = StopWatch(parent)
	self.pause = ''
        self.row_types = []
        self.gen_row_type_list()

    def gen_row_type_list(self):
        #list of all available options to generate a row
        self.row_types = []
        row_type_tuple = namedtuple('row_type_tuple','given_type target_type')
        #configure via options later
        tt = 'bhd'
        for i in tt:
            for a in tt:
                if not a == i:
                    self.row_types.append(row_type_tuple(i,a))
        for i in tt: 
            for f in itertools.permutations(tt,2):
                #don't worry about duplicates in list
                if not i in f:
                    self.row_types.append(row_type_tuple(i,f))


    def calc_tick(self):
        return int((10000.0/(int(self.level.get()))) - float(self.answered.get()))

    def check_advance_level(self):
        if (int(self.level.get()) * 25) < int(self.answered.get()):
            self.level.set(str(int(self.level.get())+1))
            return True
        return False
            
    def dump_stats(self):
        print "Level Achieved: ", self.level.get()
        print "Elapsed Time: ", self.stopwatch.root.timestr.get()
        print "Total Answered: ", self.answered.get()
        
class Layout:
    def __init__(self, parent):
        self.root = parent
        #row_tuple will hold the list of all widgets to clear in each row
        #bin hex and dec are reserved so initials
        self.row_tuple = namedtuple('row_tuple','b h d answer')
        self.rows = []

    def setup_window(self, parent):
        self.myParent = parent
        self.myParent.style = Style()
        self.myParent.style.theme_use("clam")
        self.myParent.title("Bin/Hex/Dec Game")
        self.myParent.resizable(width=FALSE, height=FALSE)
        #window dimensions
        #padding will slowly this proportional sizing method 
        self.wwidth = int(self.myParent.winfo_screenwidth() * .66)
        self.wheight = int(self.myParent.winfo_screenheight() * .66)

        #ui split up as { game | score }
        self.hframe_width_game = int(self.wwidth * .8)
        self.hframe_width_score = int(self.wwidth * .2)

        # game { legend / bin_main / legend }
        self.vframe_height_bin_legend = int(self.wheight * .05)
        self.vframe_height_numbers = int(self.wheight * .8) 
        # main { bin | hex | dec }
        self.hframe_width_bin = self.hframe_width_bin_legend = int(self.hframe_width_game * .8)
        self.hframe_width_hex = int(self.hframe_width_game * .05)
        self.hframe_width_dec = int(self.hframe_width_game * .15)

        self.hframe_padding_bin_legend = int(self.hframe_width_game * .2)

        self.myParent.geometry('%sx%s' % (self.wwidth, self.wheight))

        self.myContainer1 = Frame(parent) 
        self.myContainer1.pack(expand=1, fill=BOTH)

        self.frame_game = self.gen_hframe(self.myContainer1, self.hframe_width_game)
        self.frame_score = self.gen_hframe(self.myContainer1, self.hframe_width_score)
    
        self.gen_frame_game(self.frame_game)
        self.gen_frame_score(self.frame_score)

    def gen_frame_game(self,p):
        self.frame_bin_legend_top_container = self.gen_vframe(p, self.vframe_height_bin_legend)
        self.frame_numbers = self.gen_vframe(p, self.vframe_height_numbers)
        self.frame_bin_legend_bot_container = self.gen_vframe(p, self.vframe_height_bin_legend)

        self.frame_bin_legend_top = self.gen_hframe(self.frame_bin_legend_top_container, self.hframe_width_bin_legend)
        self.frame_bin_legend_top_right_padding = self.gen_hframe(self.frame_bin_legend_top_container, self.hframe_padding_bin_legend)
        self.frame_bin_legend_bot = self.gen_hframe(self.frame_bin_legend_bot_container, self.hframe_width_bin_legend)
        self.frame_bin_legend_bot_right_padding = self.gen_hframe(self.frame_bin_legend_bot_container, self.hframe_padding_bin_legend)

        self.gen_bin_legend(self.frame_bin_legend_top)
        self.gen_bin_legend(self.frame_bin_legend_bot)

        self.frame_bin = self.gen_hframe(self.frame_numbers, self.hframe_width_bin)
        self.frame_hex = self.gen_hframe(self.frame_numbers, self.hframe_width_hex)
        self.frame_dec = self.gen_hframe(self.frame_numbers, self.hframe_width_dec)

    def gen_frame_score(self,p):
        score_tuple = namedtuple( 'score_tuple','name text value')
        score_labels = [ score_tuple('game.level','Level','1'),
                        score_tuple('game.answered','Total Answered','0'),
                        score_tuple('game.time','Time Elapsed','')]
        score_buttons = [ score_tuple('game.pause','Pause',''),
                        score_tuple('game.sound','Sound','On')]
        for t in score_labels:
            if t.name == 'game.time':
                self.gen_frame_score_item(p,t,isButton=False,isTimer=True)
            else:
                self.gen_frame_score_item(p,t)
        #spacers- adjust top range to shrink scores button size
        #don't use pack ever again
        for i in range(0,10):
            Frame(p).pack(side=TOP, fill=BOTH, anchor=N, expand=1)
        for t in score_buttons:
            self.gen_frame_score_item(p,t,isButton=True)
        self.game.score_labels = score_labels
        self.game.score_buttons = score_buttons 

    def gen_frame_score_item(self,p,t,isButton=False,isTimer=False):
        if isButton:
            fr = Button(p, compound=CENTER)
            if t.name == 'game.pause':
               fr.bind(sequence='<Button-1>', func=self.game.stopwatch.Cycle) 
        else:
            fr = Frame(p)
        Label(fr, compound=CENTER, text=t.text).pack(side=LEFT, fill=BOTH, expand=1, padx=5, pady=5, ipadx=5, ipady=5)
        l = None
        if isTimer:
            l = Label(fr, textvariable=self.game.stopwatch.root.timestr, justify=RIGHT)
        elif t.name == 'game.level':
            l = Label(fr, textvariable=self.game.level, justify=RIGHT)
        elif t.name == 'game.answered':
            l = Label(fr, textvariable=self.game.answered, justify=RIGHT)
        else:
            l = Label(fr, text=t.value, justify=RIGHT)
            setattr(self,t.name,l)
        l.pack(side=RIGHT, anchor=E, fill=Y, expand=1, padx=5, pady=5, ipadx=5, ipady=5)
        fr.pack(side=TOP, fill=BOTH, expand=1)

    def gen_bin_legend(self,p):
        i = 128
        for c in range(0,8):
            f = Frame(p, relief=RIDGE)
            Label(f, text=(str(i) if self.game.level < (c+1)*3 else 0),justify=CENTER, width=5).pack(anchor=CENTER, expand=1)
            f.pack(side=LEFT, expand=1, fill=BOTH, padx=2, pady=2, ipadx=2, ipady=2)    
            i = int(i/2)

    def gen_hframe(self,p,w):
        f = Frame(p,relief=RIDGE, width=w)
        f.pack_propagate(0)
        f.pack(side=LEFT, expand=1, fill=BOTH, padx=2, pady=2, ipadx=2, ipady=2)    
        return f

    def gen_vframe(self,p,h):
        f = Frame(p,relief=RIDGE, height=h)
        f.pack_propagate(0)
        f.pack(side=TOP, expand=1, fill=BOTH, padx=2, pady=2, ipadx=2, ipady=2)    
        return f

    def bn_clicked(self, event):
        event.widget.bin_list[event.widget.i]='1' if event.widget['text']=='0' else '0'
        event.widget.config(text=event.widget.bin_list[event.widget.i])
        self.check_bin_answer(event)

    def regen_rows(self):
        pass

    def gen_row(self):
        pos = len(self.rows)+1
        #row_type_tuple = namedtuple('row_type_tuple','given_type target_type')
        row_type = self.game.row_types[random.randrange(0,len(self.game.row_types))]
        r = [random.choice(['1','0']) for i in xrange(0,8)]
        b = h = d = None
        if row_type.given_type=='b':
                b = self.add_bin_row(self.frame_bin, r, pos)
        elif row_type.given_type=='h':
                h = self.add_hex_row(self.frame_hex, r, pos)
        elif row_type.given_type=='d':
                d = self.add_dec_row(self.frame_dec, r, pos)
                
        for a in row_type.target_type:
            if a == 'b':
                #scramble target
                scr = [random.choice(['1','0']) for i in xrange(0,8)]
                b = self.add_bin_row(self.frame_bin, scr, pos, is_target=True,bin_val=r)
            elif a == 'h':
                h = self.add_hex_row(self.frame_hex, r, pos, is_target=True)
            elif a == 'd':
                d = self.add_dec_row(self.frame_dec, r, pos, is_target=True)
        self.rows.append(self.row_tuple(b,h,d,r))

    def add_hex_row(self,p,h,rel_y, is_target=False):
        e = Entry(p, width=4, text=h)
        e.place(relx=0.1, rely=1.0 - rel_y*0.1)
        e.val = int(''.join(h),2)
        e.rowidx=len(self.rows)
        if is_target:
            #function to check answer
            e.bind(sequence='<Key>',func=self.check_hex_answer)
        else:
            e.insert(0,hex(e.val))
            e.config(state=DISABLED)
        return e

    def add_dec_row(self,p,d,rel_y, is_target=False):
        e = Entry(p, width=10)
        e.place(relx=0.1, rely=1.0 - rel_y*0.1)
        e.rowidx=len(self.rows)
        e.val = int(''.join(d),2)
        if is_target:
            #function to check answer
            e.bind(sequence='<Key>',func=self.check_dec_answer)
        else:
            e.insert(0,e.val)
            e.config(state=DISABLED)
        return e

    def add_bin_row(self,p,bin_list, rel_y, is_target=False, bin_val=None):
        button_list = []
        for i in xrange(0,8):
            b = Button(master=p, width=8, text=bin_list[i])
            button_list.append(b)
            b.i = i
            b.bin_list = bin_list
            b.button_list = button_list
            if is_target:
                b.bind(sequence='<Button-1>', func=self.bn_clicked)
            b.place(relx=(1/8)*i, rely=1.0 - rel_y*0.1)
        button_list[0].rowidx=len(self.rows)
        button_list[0].val = bin_val
        return button_list

    def remove_row(self,idx):
        if not self.rows[idx].b==None:
            for b in self.rows[idx].b:
                 b.destroy()
        if not self.rows[idx].h==None:
                self.rows[idx].h.destroy()
        if not self.rows[idx].d==None:
            self.rows[idx].d.destroy()
        #everything above idx needs to be adjusted
        #fix indexes and adjust screen placement
        if len(self.rows) > idx:
            for r in range(idx+1,len(self.rows)):
                if not self.rows[r].b==None:
                    self.rows[r].b[0].rowidx = self.rows[r].b[0].rowidx - 1
                    i=0
                    for b in self.rows[r].b:
                        b.place(relx=(1/8)*i, rely=1.0 - r*0.1)
                        i = i + 1
                if not self.rows[r].h==None:
                    self.rows[r].h.rowidx = self.rows[r].h.rowidx - 1
                    self.rows[r].h.place(relx=0.1, rely=1.0 - r*0.1)
                if not self.rows[r].d==None:
                    self.rows[r].d.rowidx = self.rows[r].d.rowidx - 1
                    self.rows[r].d.place(relx=0.1, rely=1.0 - r*0.1)
        del self.rows[idx]

    def check_bin_answer(self, event):
        if event.widget.button_list[0].val == event.widget.button_list[0].bin_list:
            self.remove_row(event.widget.button_list[0].rowidx)
            self.game.answered.set( str(int(self.game.answered.get()) + 1))
            self.game.check_advance_level()

    def check_dec_answer(self, event):
        if str(event.widget.val) == event.widget.get():
            self.remove_row(event.widget.rowidx)
            self.game.answered.set( str(int(self.game.answered.get()) + 1))
            self.game.check_advance_level()

    def check_hex_answer(self, event):
        try:
            if hex(event.widget.val) == hex(int(event.widget.get(),16)):
                print "correct"
                self.remove_row(event.widget.rowidx)
                self.game.answered.set( str(int(self.game.answered.get()) + 1))
                self.game.check_advance_level()
        except TypeError:
            pass
        except ValueError:
            pass

class MyApp:
    def __init__(self, parent):
        self.root = parent
        self.layout = Layout(parent)
        self.game = Game(parent)
        self.layout.game = self.game
        self.game.layout = self.layout

    def timer(self):
        #determine next tick speed based on level, amount completed, and alg
        if self.game.stopwatch.running:
            self.layout.gen_row()
            if len(self.layout.rows) > 10:
                print "GAME OVER!"
                self.game.dump_stats()
                exit(1)
        #technically can 'cheat' here
        self.root.after(self.game.calc_tick(),self.timer)
        
if __name__ == '__main__':
    root = Tk()
    myapp = MyApp(root)
    myapp.timer()
    myapp.game.stopwatch.Start() 
    myapp.layout.setup_window(root)
    myapp.layout.gen_row()
    myapp.root.mainloop()

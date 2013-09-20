#!/usr/bin/python
"""
Hugo Rivera
Fall 2013
Suspensful random number picker.
Resizable, py2/3 compatible, cross platform.
"""
from sys import version_info
from random import choice
from math import log

#Try to maintain py3 compatibility
if version_info[0] <= 2:
    import Tkinter as tk
else:
    import tkinter as tk
    
class Roulette_UI(tk.Tk):
    def __init__(self, title, suspensefulness=5, master=None):
        """
        Create a tkinter window. 
        title - displayed on the top of the tkinter window
        suspensefulness - speed of shuffling
            , a lower value means numbers are unveiled faster
        """
        #Initiate tkinter
        tk.Tk.__init__(self, master)
        self.title(title)
        
        self.tk_setPalette(background='white', foreground='black', \
               activeBackground='white', activeForeground='gray')
        #Initial values.
        self.suspensefulness = suspensefulness
        self.num, self.max_num, self.min_num, self.step_num = 777, 1000, -1000, 1
        self.range = list(range(self.min_num, self.max_num, self.step_num))
        self.init_range = self.range
        
        self.f = tk.Frame(self, bg='white')
        self.f.pack(fill=tk.BOTH, expand=1)
        self._define_elements(self.f)
        
        self.protocol("WM_DELETE_WINDOW", self.tk_quit)
        self.bind("<Escape>", self.tk_quit)
        
        #Used to calculate a nice color scheme.
        self.button_fg = "#FF1717"
        self.button_bg = "#FFFFFF"
        
        
        #First run
        self.run()
        return
        
    def run(self):
        """
        First run. Start with the default range, ask for another range.
        """
        self.range_ask()
        self.num_ask()
        self.roll_nums()
        self.mainloop()
        return
        
    def _define_elements(self, frame):
        #Make a menu on the top bar with a single button that makes a dropdown menu
        self.top_menu = tk.Menu(frame)

        self.drop_menu = tk.Menu(frame, tearoff=0)
        self.drop_menu.add_command(label="Change Range", command=self.range_ask)
        self.drop_menu.add_command(label="Picking speed", command=self.num_ask)
        self.drop_menu.add_command(label="About", command=self.show_about)
        self.drop_menu.add_separator()
        self.drop_menu.add_command(label="Quit", command=self.tk_quit)
        
        self.top_menu.add_cascade(label="Menu", menu=self.drop_menu)
        #Hope 'self' extends 'tkinter.Tk()'
        self.config(menu=self.top_menu)
        
        #Create canvas frame for drawing numbers and a wrapper frame for it.
        self.num_frame = tk.Frame(frame)
        self.num_frame.pack(side = tk.TOP, fill=tk.BOTH, expand=True)
        
        self.num_canvas = tk.Canvas(self.num_frame)
        self.num_canvas.pack(fill=tk.BOTH, expand=True)
        self.num_canvas.bind("<Configure>", self.roll_nums)
        
        self.num_canvas_width = int(self.num_canvas.cget("width"))
        self.num_canvas_height = int(self.num_canvas.cget("height"))
        
        self.canvas_rects = []
        self.canvas_digits = []
        self.canvas_queue = []
        
        #Create button to start shuffling
        self.but_image = tk.PhotoImage(file="red_button.ppm")
        self.but_go = tk.Button(frame, text='GET', image=self.but_image, \
            command=self.show_random)
        self.but_go.pack()
        
        return

    def tk_quit(self):
        """
        Close the entire window
        """
        self.quit()
        self.destroy()  
        self.quit = True #Broadcast status
        return
    
    def show_about(self):
        Message(self, "About", \
        "A suspenseful random number picker.\nHugo Rivera 2013")
        return
    
    def num_ask(self):
        question = \
        "Please enter the desired coefficient for number selection\nA lower value means numbers are unveiled faster\nInteger >= 1"
        n = Ask_Num_Dialog(self, question, self.suspensefulness)
        self.suspensefulness = n.result
        return
    
    def range_ask(self, question=None):
        """
        Ask for the desired range for random numbers
        """
        if question == None:
            question = \
            "Please enter the desired range \nand the step size for incrementing"
        d = Range_Dialog(self, question, (self.max_num, self.min_num, self.step_num))
        if hasattr(d.result, '__getitem__') and len(d.result) == 3:
            res = d.result
            
            self.step_num = res[2]
            self.max_num = max(res[0], res[1])
            self.min_num = min(res[0], res[1])
            
            self.range = list(range(self.min_num, self.max_num, self.step_num))
        else:
            self.range = self.init_range
        
        return
    
    def show_random(self):
        """
        Pick a new random number and start the picking animation.
        """
        self.num = choice(self.range)
        self.callback_roll_nums()
        return

    def roll_nums(self, event=None, time_per_place=5):
        """
        Unveil the numbers using the canvas at a pace of 'time_per_place'
        which must be >0 and an integer
        """
        if time_per_place <= 0:
            time_per_place = 1
        time_per_place = int(time_per_place)
        
        #Clear the after() queue and the lists of element IDs
        for e in self.canvas_rects + self.canvas_digits:
            self.num_canvas.delete(e)
        for t in self.canvas_queue:
            self.after_cancel(t)
        self.canvas_rects = []
        self.canvas_digits = []

        #Draw a rectangle for each decimal place
        if not event == None:
            self.num_canvas_width = event.width
            self.num_canvas_height = event.height

        #How many places? Make it an integer and give log a >0 value
        mnum = max(abs(self.max_num), abs(self.min_num))
        num_rects = int(log(mnum, 10)) + 1
        
        #Make space for the dash
        if self.min_num < 0 and int(log(abs(self.min_num), 10)) + 1 >= num_rects:
            num_rects += 1
        num_range = list(range(num_rects))
        
        #Figure out the element dimensions, colors and position
        rect_outline = 10
        rect_w = self.num_canvas_width / num_rects - 5
        rect_h = self.num_canvas_height - 2 * rect_outline
        rect_ox = self.num_canvas_width / 2
        rect_ox -= (num_rects * rect_w) / 2
        rect_oy = 10
        
        outline = self.complementary_color(self.button_fg)
        bg = self.button_fg
        
        #Draw background rects
        for i in num_range:
            #Center the rectangles and give them space between each other
            x1, y1, x2, y2 = i*rect_w + rect_ox, rect_h + rect_oy, \
                (i * rect_w) + rect_w + rect_ox, rect_oy
            rect = self.num_canvas.create_rectangle(x1, y1, x2, y2, \
                fill=bg, outline=outline, width=rect_outline)
            self.canvas_rects.append(rect)
        
        #Draw text. Pad smaller numbers with zeroes. 
        #E.g., if max_num = 999, num = 99, ns = "099"
        ns = self._pad_string(str(abs(self.num)), '0', num_rects)
        #Add the dash if it had one
        if self.num < 0:
            ns = '-' + ns[1:]
        
        #Pick a font size
        fontsize = - self.num_canvas_width / 2.5
        font = ('Helvetica', int(fontsize))
        
        #Draw a character on the ith rectangle
        def draw_char(i, char='7', delete_after=-1):
            #center the number
            x1, y1 = i*rect_w + rect_ox, rect_h + rect_oy
            
            x, y = x1 + rect_w / 2, y1 / 2
            
            txt = self.num_canvas.create_text(x, y, \
                text=char, font=font, fill='white')
            
            #Ask tkinter to delete this character from the canvas after X ms
            if delete_after > 0:
                timed = self.num_canvas.after(delete_after, self.num_canvas.delete, txt)
                self.canvas_queue.append(timed)
            self.canvas_digits.append(txt)
        
        #Start with the most significant place first
        num_range.reverse()
        
        #The time interval
        #Use tkinter's after() queue to make the numbers whiz by cool.
        del_time = time_per_place * 5
        for i in num_range:
            #Loop from 0 to 9 'count' times
            count = (i + 1) * 3 + int(time_per_place / 2)
            cc = ns[i]
            
            if cc == '-':
                picked_int = 0
            else:
                picked_int = int(cc)
                
            for j in list(range(0,9)) * count + list(range(0, picked_int)):
                #Add a new character after some time
                #Callback = draw the countdown number
                
                #Delete this char after X seconds
                del_after = int(del_time * 2)
                
                timed = self.num_canvas.after(del_time * count, \
                    draw_char, i, str(j), del_time)
                self.canvas_queue.append(timed)
                count += 1
            
            #Draw the picked number
            timed = self.num_canvas.after(count * del_time, draw_char, i, cc)
            self.canvas_queue.append(timed)
        return
    
    def callback_roll_nums(self):
        """
        #Callback functions take no args. 
        #This runs roll_nums and asks it to take some time in displaying each decimal place
        #time in milliseconds
        """
        self.num_canvas.delete(tk.ALL)
        self.roll_nums(None, time_per_place=self.suspensefulness)
        return
    
    def complementary_color(self, hex_string, max_places=6, prefix='#'):
        """
        Find the complementary color of a hex color string. 
        Handles prefixes and places.
        """
        #max color - color = complementary color
        max_color = self._pad_string('', 'F', max_places)
        comp = (hex(int(max_color, 16) - int(hex_string[len(prefix):], 16)))
        #apply the given prefix based format and remove python's hex formatting
        return prefix + self._pad_string(comp[2:], '0', max_places)

    def _pad_string(self, string, prefix, max_length):
        #pads a string with some substring as a prefix
        if len(string) < max_length:
            string = prefix + string
            string = self._pad_string(string, prefix, max_length)
        return string


#Class for dialog windows from the tkinter docs
#apply and body changed to make it a range picking dialog
#http://effbot.org/tkinterbook/tkinter-dialog-windows.htm
class Dialog(tk.Toplevel):
    def __init__(self, parent, title = None):
        tk.Toplevel.__init__(self, parent)
        self.transient(parent)
        if title:
            self.title(title)
        self.parent = parent

        self.result = None
        
        body = tk.Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5, pady=5)

        self.buttonbox()
        self.grab_set()

        if not self.initial_focus:
            self.initial_focus = self

        self.protocol("WM_DELETE_WINDOW", self.cancel)
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
                                parent.winfo_rooty()+50))

        self.initial_focus.focus_set()
        self.wait_window(self)

    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.
        pass

    def buttonbox(self):
        # add standard button box. OK, cancel, and a question
        box = tk.Frame(self)

        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.LEFT, padx=5, pady=5)
        w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side=tk.LEFT, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()
        return

    def ok(self, event=None):
        self.withdraw()
        self.update_idletasks()

        self.apply()
        self.cancel()

    def cancel(self, event=None):
        # put focus back to the parent window
        self.parent.focus_set()
        self.destroy()
        return

    def apply(self):
        pass

class Message(Dialog):
    def __init__(self, parent, title=None, message=None):
        self.message = message
        Dialog.__init__(self, parent, title)

    def buttonbox(self):
        box = tk.Frame(self)
        
        l = tk.Label(box, text=self.message)
        l.pack(padx=16, pady=16)
        
        w = tk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side=tk.BOTTOM, padx=5, pady=5)
        
        self.bind("<Return>", self.cancel)
        self.bind("<Escape>", self.cancel)
        
        box.pack()

class Range_Dialog(Dialog):
    def __init__(self, parent, question=None, prev_range=(0,5,1), title = None):
        self.question = question
        self.prev_range = prev_range
        Dialog.__init__(self, parent, title)
        
    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.
        if self.question:
            q = tk.Label(master, text=self.question)
            q.grid(row=0, columnspan=2)
        
        tk.Label(master, text="Start:").grid(row=1)
        self.e_start = tk.Entry(master)
        self.e_start.insert(0, self.prev_range[0])
        self.e_start.grid(row=1, column=1)
        
        tk.Label(master, text="End:").grid(row=2)
        self.e_end = tk.Entry(master)
        self.e_end.insert(0, self.prev_range[1])
        self.e_end.grid(row=2, column=1)
        
        #tkinter variable
        self.user_wants_step = tk.IntVar()
        
        #want step?
        self.cb = tk.Checkbutton(master, text="Step?", variable=self.user_wants_step)
        self.cb.grid(row=3, sticky=tk.W)
        if self.prev_range[2] != 1:
            self.user_wants_step.set(1)
        
        #get step!
        self.e_step = tk.Entry(master)
        self.e_step.insert(0, self.prev_range[2])
        self.e_step.grid(row=3, column=3)
        
        return self.e_start #initial focus.
    
    def apply(self):
        try:
            start = int(self.e_start.get())
            end = int(self.e_end.get())

            if self.user_wants_step.get() == 1:
                step = int(self.e_step.get())
            else:
                step = 1
            self.result = start, end, step
        except:
            self.result = None
        return
    
class Ask_Num_Dialog(Dialog):
    def __init__(self, parent, question=None, prev_num=0, title = None):
        self.question = question
        self.prev_num = prev_num
        Dialog.__init__(self, parent, title)
        
    def body(self, master):
        # create dialog body.  return widget that should have
        # initial focus.
        if self.question:
            q = tk.Label(master, text=self.question)
            q.grid(row=0, columnspan=2)
        
        tk.Label(master, text="Start:").grid(row=1)
        self.e_num = tk.Entry(master)
        self.e_num.insert(0, self.prev_num)
        self.e_num.grid(row=1, column=1)
        
        return self.e_num 
    
    def apply(self):
        try:
            num = int(self.e_num.get())
            self.result = num
        except:
            self.result = None
        return

if __name__ == '__main__':
    r = Roulette_UI("SC Roulette", 3)
import tkinter as tk
from tkinter.ttk import Progressbar

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.hi_there = tk.Button(self)
        self.hi_there["text"] = "Hello World\n(click me)"
        self.hi_there["command"] = self.say_hi
        self.hi_there.pack(side="top")

        self.quit = tk.Button(self, text="QUIT", fg="red",
                              command=self.master.destroy)
        self.quit.pack(side="bottom")
        self.progress = Progressbar(self, orient=tk.HORIZONTAL,length=100,  mode='indeterminate')
        self.progress = tk.ttk.Progressbar(self);
        self.progress.pack();

    def say_hi(self):
        self.progress.start()
        print("hi there, everyone!")

root = tk.Tk()
app = Application(master=root)
app.mainloop()


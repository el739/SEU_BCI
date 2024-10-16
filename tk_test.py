import tkinter as tk  

class MyApp:  
    def __init__(self, root):  
        self.root = root  
        self.root.title('Tkinter Example')  
        self.root.geometry('300x200')  

        self.label = tk.Label(root, text='Hello, Tkinter!', font=('Arial', 20))  
        self.label.pack(pady=20)  

        self.button = tk.Button(root, text='Click Me', command=self.on_button_click)  
        self.button.pack(pady=20)  

    def on_button_click(self):  
        self.label.config(text='Button Clicked!')  

if __name__ == '__main__':  
    root = tk.Tk()  
    app = MyApp(root)  
    root.mainloop()
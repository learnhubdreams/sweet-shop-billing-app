# main.py

import tkinter as tk
from ui.main_window import MainWindow

def main():
    root = tk.Tk()
    root.title("Sweet Shop Billing System")
    root.geometry("1000x600")
    root.resizable(False, False)

    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()

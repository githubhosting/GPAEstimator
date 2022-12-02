import tkinter as tk


def show_img(img64):
    root = tk.Tk()
    w, h = 300, 150
    x, y = (root.winfo_screenwidth() - w) // 2, (root.winfo_screenheight() - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")
    dat = [""]

    img = tk.PhotoImage(data=img64)
    cv = tk.Canvas(root, width=300, height=80, bg='white')
    cv.pack(side='top', fill='both', expand=1)
    cv.create_image(150, 40, image=img)

    inp = tk.Entry(root)
    inp.pack(pady=5)
    but = tk.Button(root, text="enter", command=lambda: dat.append(inp.get()) or root.destroy())
    but.pack(pady=5)

    root.mainloop()
    return dat.pop()

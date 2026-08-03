# EXAMPLE READ USAGE

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import time
import threading
import subprocess
import platform

REQUEST_FILE = "read_request.txt"
RESPONSE_FILE = "read_response.txt"


def read_response():
    data = {}
    with open(RESPONSE_FILE) as f:
        for line in f:
            if "=" in line:
                key, value = line.strip().split(
                    "=",
                    1
                )

                data[key] = value

    os.remove(RESPONSE_FILE)

    return data


class MediaUI:

    def __init__(self, root_seed):
        self.root = root_seed
        self.root.title("Media Read Service UI")
        self.root.geometry("900x700")
        self.current_file = ""
        self.current_image = None

        ##################################################
        # Search Area
        ##################################################

        top = ttk.Frame(root_seed, padding=10)
        top.pack(fill="x")

        ttk.Label(
            top,
            text="Filename:"
        ).pack(side="left")

        self.filename = ttk.Entry(
            top,
            width=50
        )

        self.filename.pack(
            side="left",
            padx=10
        )

        ttk.Button(
            top,
            text="Open",
            command=self.request_file
        ).pack(side="left")

        ##################################################
        # Status
        ##################################################

        self.status = ttk.Label(
            root_seed,
            text="Ready"
        )

        self.status.pack()

        ##################################################
        # Metadata
        ##################################################

        info = ttk.LabelFrame(
            root_seed,
            text="File Information",
            padding=10
        )

        info.pack(
            fill="x",
            padx=10,
            pady=10
        )

        self.metadata = tk.Text(
            info,
            height=8
        )

        self.metadata.pack(
            fill="x"
        )

        ##################################################
        # Display Area
        ##################################################

        display = ttk.LabelFrame(
            root_seed,
            text="Preview",
            padding=10
        )

        display.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        self.preview = tk.Label(
            display
        )

        self.preview.pack(
            expand=True
        )

        self.text_view = tk.Text(
            display,
            wrap="word"
        )

    ##################################################
    # Send READ request
    ##################################################

    def request_file(self):

        filename = self.filename.get().strip()

        if filename == "":
            return

        threading.Thread(
            target=self.send_request,
            args=(filename,),
            daemon=True
        ).start()

    def send_request(self, filename):

        self.status.config(
            text="Requesting..."
        )

        if os.path.exists(RESPONSE_FILE):
            os.remove(RESPONSE_FILE)

        with open(REQUEST_FILE, "w") as f:
            f.write("command=READ\n")
            f.write(f"file_name={filename}\n")

        start = time.time()
        while time.time() - start < 15:
            if os.path.exists(RESPONSE_FILE):
                response = read_response()
                self.display_response(response)
                return

            time.sleep(.25)

        messagebox.showerror(
            "Timeout",
            "Read Service did not respond."
        )

    ##################################################
    # Display result
    ##################################################

    def display_response(self, data):

        self.clear_display()

        if data.get("status") != "success":
            self.status.config(text="File not found")
            return

        self.status.config(text="Loaded")
        self.current_file = data["file_path"]
        self.metadata.insert(
            "end", "\n".join(
                [f"{k}: {v}"for k, v in data.items()]
            )
        )

        media = data.get(
            "media_type",
            "other"
        )

        ##################################################
        # Text
        ##################################################

        if media == "text":

            self.show_text(self.current_file)

        ##################################################
        # Image
        ##################################################

        elif media == "image":

            self.show_image(self.current_file)

        ##################################################
        # Other
        ##################################################

        else:

            self.preview.config(
                text=f"{media.upper()} FILE\n\n"
                "Use Open button below."
            )

            ttk.Button(
                self.preview.master,
                text="Open File",
                command=self.open_external
            ).pack()

    ##################################################
    # Display text
    ##################################################

    def show_text(self, filename):

        self.text_view.pack(
            fill="both",
            expand=True
        )

        with open(filename, "r", errors="ignore") as f:
            contents = f.read()

        self.text_view.insert(
            "end",
            contents
        )

    ##################################################
    # Display image
    ##################################################

    def show_image(self, filename):

        image = Image.open(
            filename
        )

        image.thumbnail(
            (600, 400)
        )

        self.current_image = ImageTk.PhotoImage(
            image
        )

        self.preview.config(
            image=self.current_image
        )

    ##################################################
    # Open external application
    ##################################################

    def open_external(self):

        if not self.current_file:
            return

        if platform.system() == "Windows":

            os.startfile(self.current_file)

        elif platform.system() == "Darwin":
            subprocess.Popen(
                ["open", self.current_file]
            )

        else:
            subprocess.Popen(
                ["xdg-open", self.current_file]
            )

    ##################################################
    # Clear UI
    ##################################################

    def clear_display(self):

        self.metadata.delete(
            "1.0",
            "end"
        )

        self.text_view.pack_forget()

        self.preview.config(
            image=""
        )


##########################################################

if __name__ == "__main__":
    root = tk.Tk()

    app = MediaUI(root)

    root.mainloop()

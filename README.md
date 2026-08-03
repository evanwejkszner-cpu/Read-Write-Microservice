# Read-Microservice
A microservice that reads and returns saved application data so programs can access stored information. Program is compatible with several media types, however it only returns metadata; data must be encoded by client program. It also has a built in search feature.

SEND REQUEST:
        with open(REQUEST_FILE, "w") as f:        # Opens request file
            f.write("command=READ\n")             # Writes READ command into request
            f.write(f"file_name={filename}\n")    # Writes file name into request

EXAMPLE REQUEST:
        command=READ
        file_name=photo.jpg                       # This is what's sent to read.py

READ.PY RESPONSE:
        status=success
        file_name=photo.jpg
        file_path=C:\Media\photo.jpg
        file_type=.jpg
        media_type=image
        file_size=2458731
        modified=2026-08-02 21:15:32

CLIENT INTERPRETATION:
        data = {
            "status": "success",
            "file_name": "photo.jpg",
            "file_path": "C:\\Media\\photo.jpg",
            "file_type": ".jpg",
            "media_type": "image",
            "file_size": "2458731",
            "modified": "2026-08-02 21:15:32"
        }                                        # Client receives dictionary

CLIENT-SIDE PROCESSING:
        def display_response(self, data):        # Display function
            if data.get("status") != "success":
                self.status.config(text="File not found")
                return                           # Handles request failure
            self.status.config(text="Loaded")    # For request success
            self.current_file = data["file_path"]# Saves file path for future reference
            media = data.get(
                "media_type",
                "other"
            )                                    # Finds file type for continued processing

CLIENT-SIDE PROCESSING BY FILE TYPE:
  TEXT:
        if media == "text":
            self.show_text{self.current_file)
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
  IMAGE:
        elif media == "image":
            self.show_image(self.current_file)
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


UML:
┌────────┐        ┌──────────┐        ┌────────────────┐        ┌───────────────┐
│ User   │        │   UI     │        │  Read Service  │        │ Media Library │
└───┬────┘        └────┬─────┘        └───────┬────────┘        └───────┬───────┘
    │                  │                      │                         │
    │ Enter filename   │                      │                         │
    │─────────────────>│                      │                         │
    │                  │                      │                         │
    │                  │ Create read_request.txt                       │
    │                  │─────────────────────>│                         │
    │                  │                      │                         │
    │                  │                      │ Detect request file     │
    │                  │                      │                         │
    │                  │                      │ Parse request           │
    │                  │                      │                         │
    │                  │                      │ command=READ            │
    │                  │                      │ file_name=image.jpg     │
    │                  │                      │                         │
    │                  │                      │ Request file metadata   │
    │                  │                      │────────────────────────>│
    │                  │                      │                         │
    │                  │                      │ Return file information  │
    │                  │                      │<────────────────────────│
    │                  │                      │                         │
    │                  │                      │ Create read_response.txt │
    │                  │<─────────────────────│                         │
    │                  │                      │                         │
    │                  │ Read response file  │                         │
    │                  │─────────────────────>│                         │
    │                  │                      │                         │
    │                  │ Receive metadata    │                         │
    │                  │<─────────────────────│                         │
    │                  │                      │                         │
    │                  │ Determine media type│                         │
    │                  │                      │                         │
    │                  │                      │                         │
    │                  │ Display file        │                         │
    │<─────────────────│                      │                         │
    │                  │                      │                         │

    

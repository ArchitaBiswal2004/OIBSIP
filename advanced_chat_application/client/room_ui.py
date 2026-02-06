# client/room_ui.py
import tkinter as tk
from tkinter import messagebox
from client.chat_ui import ChatWindow


class RoomSelector:
    """Enhanced room selection window"""

    def __init__(self, client):
        self.client = client

        self.root = tk.Tk()
        self.root.title("Select Chat Room")
        self.root.geometry("450x550")
        self.root.resizable(False, False)
        self.root.configure(bg="#075e54")

        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        """Create UI elements"""

        # Header
        header_frame = tk.Frame(self.root, bg="#075e54")
        header_frame.pack(fill="x", pady=20)

        tk.Label(
            header_frame,
            text=f"Welcome, {self.client.username}!",
            font=("Segoe UI", 18, "bold"),
            bg="#075e54",
            fg="white"
        ).pack()

        tk.Label(
            header_frame,
            text="Choose or create a chat room",
            font=("Segoe UI", 10),
            bg="#075e54",
            fg="#dcf8c6"
        ).pack(pady=(5, 0))

        # Main content
        content_frame = tk.Frame(self.root, bg="white")
        content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        # Room name entry
        tk.Label(
            content_frame,
            text="Room Name",
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor="w", pady=(30, 8))

        self.room_entry = tk.Entry(
            content_frame,
            font=("Segoe UI", 13),
            relief="solid",
            bd=1
        )
        self.room_entry.pack(fill="x", ipady=10)
        self.room_entry.insert(0, "general")
        self.room_entry.focus_set()
        self.room_entry.select_range(0, tk.END)

        # Join button
        self.join_btn = tk.Button(
            content_frame,
            text="Join Room",
            font=("Segoe UI", 12, "bold"),
            bg="#25d366",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.join_room,
            padx=20,
            pady=12
        )
        self.join_btn.pack(fill="x", pady=(20, 10))

        # Divider
        tk.Label(
            content_frame,
            text="── or choose from popular rooms ──",
            font=("Segoe UI", 9),
            bg="white",
            fg="gray"
        ).pack(pady=15)

        # Popular rooms
        popular_rooms = [
            ("💬 General", "general"),
            ("💼 Work", "work"),
            ("🎮 Gaming", "gaming"),
            ("📚 Study", "study"),
            ("🎵 Music", "music"),
            ("🍕 Food", "food")
        ]

        rooms_grid = tk.Frame(content_frame, bg="white")
        rooms_grid.pack(fill="x", pady=10)

        for i, (label, room) in enumerate(popular_rooms):
            row = i // 2
            col = i % 2

            btn = tk.Button(
                rooms_grid,
                text=label,
                font=("Segoe UI", 10),
                bg="#f0f0f0",
                fg="#333",
                relief="flat",
                cursor="hand2",
                command=lambda r=room: self.quick_join(r),
                padx=15,
                pady=8
            )
            btn.grid(row=row, column=col, padx=5, pady=5, sticky="ew")

        rooms_grid.columnconfigure(0, weight=1)
        rooms_grid.columnconfigure(1, weight=1)

        # Bind Enter key
        self.root.bind("<Return>", lambda e: self.join_room())

        # Info
        tk.Label(
            content_frame,
            text="🔒 All messages are encrypted end-to-end",
            font=("Segoe UI", 8),
            bg="white",
            fg="gray"
        ).pack(side="bottom", pady=(20, 10))

    def quick_join(self, room):
        """Quick join a room from popular list"""
        self.room_entry.delete(0, tk.END)
        self.room_entry.insert(0, room)
        self.join_room()

    def join_room(self):
        """Join selected room"""
        room = self.room_entry.get().strip()

        if not room:
            messagebox.showerror("Error", "Please enter a room name")
            return

        if len(room) < 2:
            messagebox.showerror("Error", "Room name must be at least 2 characters")
            return

        # Validate room name (alphanumeric + underscore/dash)
        if not room.replace("_", "").replace("-", "").isalnum():
            messagebox.showerror("Error", "Room name can only contain letters, numbers, _ and -")
            return

        self.join_btn.config(state="disabled", text="Joining...")
        self.root.update()

        try:
            # Send join request
            success = self.client.join_room(room)

            if success:
                self.root.destroy()
                ChatWindow(self.client, room)
            else:
                messagebox.showerror("Error", "Failed to join room")
                self.join_btn.config(state="normal", text="Join Room")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to join room:\n{e}")
            self.join_btn.config(state="normal", text="Join Room")
# client/chat_ui.py
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import threading
import uuid
import base64
import os
from datetime import datetime


class ChatWindow:
    """Advanced WhatsApp-like chat interface with all features"""

    def __init__(self, client, room):
        self.client = client
        self.room = room
        self.messages = {}  # message_id -> message info
        self.typing_users = []
        self.selected_message = None  # For reply/edit/delete
        self.last_typing_time = 0

        self.root = tk.Tk()
        self.root.title(f"Chat Room – {room}")
        self.root.geometry("800x650")
        self.root.minsize(600, 400)

        self.create_widgets()
        self.start_receive_thread()

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def create_widgets(self):
        """Create all UI elements"""

        # ===== HEADER =====
        header_frame = tk.Frame(self.root, bg="#075e54", height=70)
        header_frame.pack(fill="x")
        header_frame.pack_propagate(False)

        # Room info
        info_frame = tk.Frame(header_frame, bg="#075e54")
        info_frame.pack(side="left", padx=15, pady=10)

        tk.Label(
            info_frame,
            text=f"# {self.room}",
            bg="#075e54",
            fg="white",
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w")

        self.status_label = tk.Label(
            info_frame,
            text=f"🟢 Connected as {self.client.username}",
            bg="#075e54",
            fg="#dcf8c6",
            font=("Segoe UI", 9)
        )
        self.status_label.pack(anchor="w")

        # Header buttons
        btn_frame = tk.Frame(header_frame, bg="#075e54")
        btn_frame.pack(side="right", padx=15)

        tk.Button(
            btn_frame,
            text="📎",
            font=("Segoe UI", 16),
            bg="#075e54",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.attach_file,
            bd=0
        ).pack(side="left", padx=5)

        # ===== CHAT AREA =====
        chat_container = tk.Frame(self.root, bg="#ece5dd")
        chat_container.pack(fill="both", expand=True)

        # Scrollbar
        scrollbar = tk.Scrollbar(chat_container)
        scrollbar.pack(side="right", fill="y")

        # Chat text widget
        self.chat = tk.Text(
            chat_container,
            state="disabled",
            wrap="word",
            yscrollcommand=scrollbar.set,
            bg="#ece5dd",
            font=("Segoe UI", 10),
            cursor="arrow",
            padx=10,
            pady=10
        )
        self.chat.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.chat.yview)

        # Configure text tags for message bubbles
        self.chat.tag_config(
            "bubble_me",
            background="#dcf8c6",
            justify="right",
            lmargin1=150,
            lmargin2=150,
            rmargin=15,
            spacing1=5,
            spacing3=8,
            relief="solid",
            borderwidth=1
        )

        self.chat.tag_config(
            "bubble_other",
            background="white",
            justify="left",
            lmargin1=15,
            lmargin2=15,
            rmargin=150,
            spacing1=5,
            spacing3=8,
            relief="solid",
            borderwidth=1
        )

        self.chat.tag_config(
            "sender_me",
            foreground="#075e54",
            font=("Segoe UI", 9, "bold"),
            justify="right"
        )

        self.chat.tag_config(
            "sender_other",
            foreground="#075e54",
            font=("Segoe UI", 9, "bold"),
            justify="left"
        )

        self.chat.tag_config(
            "timestamp",
            foreground="gray",
            font=("Segoe UI", 8),
            justify="right"
        )

        self.chat.tag_config(
            "system",
            foreground="#666",
            font=("Segoe UI", 9, "italic"),
            justify="center"
        )

        self.chat.tag_config(
            "edited",
            foreground="gray",
            font=("Segoe UI", 8, "italic")
        )

        # Typing indicator
        self.typing_label = tk.Label(
            self.root,
            text="",
            bg="#ece5dd",
            fg="gray",
            font=("Segoe UI", 9, "italic"),
            anchor="w",
            padx=15,
            height=1
        )
        self.typing_label.pack(fill="x")

        # ===== REPLY BAR (hidden by default) =====
        self.reply_frame = tk.Frame(self.root, bg="#d1f4cc", height=40)
        self.reply_label = tk.Label(
            self.reply_frame,
            text="",
            bg="#d1f4cc",
            fg="#333",
            font=("Segoe UI", 9),
            anchor="w"
        )
        self.reply_label.pack(side="left", padx=10, fill="both", expand=True)

        tk.Button(
            self.reply_frame,
            text="✕",
            bg="#d1f4cc",
            fg="red",
            relief="flat",
            cursor="hand2",
            command=self.cancel_reply
        ).pack(side="right", padx=10)

        # ===== INPUT AREA =====
        input_frame = tk.Frame(self.root, bg="white", padx=10, pady=10)
        input_frame.pack(fill="x")

        # Message entry
        self.entry = tk.Text(
            input_frame,
            height=3,
            wrap="word",
            font=("Segoe UI", 11),
            relief="solid",
            bd=1
        )
        self.entry.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.entry.bind("<KeyRelease>", self.on_typing)
        self.entry.bind("<Control-Return>", lambda e: self.send_message())
        self.entry.focus_set()

        # Send button
        self.send_btn = tk.Button(
            input_frame,
            text="Send",
            font=("Segoe UI", 11, "bold"),
            bg="#25d366",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.send_message,
            state="disabled",
            padx=20,
            pady=10
        )
        self.send_btn.pack(side="right")

        # Right-click menu for messages
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Reply", command=self.reply_to_message)
        self.context_menu.add_command(label="Edit", command=self.edit_message)
        self.context_menu.add_command(label="Delete", command=self.delete_message)
        self.context_menu.add_command(label="Copy", command=self.copy_message)

        self.chat.bind("<Button-3>", self.show_context_menu)

    def show_context_menu(self, event):
        """Show right-click context menu"""
        # Get clicked position
        index = self.chat.index(f"@{event.x},{event.y}")
        
        # Find message at this position (simplified)
        self.context_menu.post(event.x_root, event.y_root)

    def reply_to_message(self):
        """Set up reply to selected message"""
        if self.selected_message:
            msg_info = self.messages.get(self.selected_message)
            if msg_info:
                self.reply_frame.pack(fill="x", before=self.typing_label)
                self.reply_label.config(
                    text=f"↩ Replying to {msg_info['sender']}: {msg_info['text'][:50]}..."
                )
                self.entry.focus_set()

    def cancel_reply(self):
        """Cancel reply"""
        self.reply_frame.pack_forget()
        self.selected_message = None

    def edit_message(self):
        """Edit own message"""
        if self.selected_message:
            msg_info = self.messages.get(self.selected_message)
            if msg_info and msg_info['sender'] == self.client.username:
                new_text = self.entry.get("1.0", "end-1c").strip()
                if new_text:
                    self.client.edit_message(self.selected_message, new_text)

    def delete_message(self):
        """Delete own message"""
        if self.selected_message:
            msg_info = self.messages.get(self.selected_message)
            if msg_info and msg_info['sender'] == self.client.username:
                if messagebox.askyesno("Delete Message", "Delete this message?"):
                    self.client.delete_message(self.selected_message)

    def copy_message(self):
        """Copy message text to clipboard"""
        if self.selected_message:
            msg_info = self.messages.get(self.selected_message)
            if msg_info:
                self.root.clipboard_clear()
                self.root.clipboard_append(msg_info['text'])

    def on_typing(self, event=None):
        """Handle typing events"""
        import time

        # Enable/disable send button
        text = self.entry.get("1.0", "end-1c").strip()
        self.send_btn.config(state="normal" if text else "disabled")

        # Send typing indicator (throttled)
        current_time = time.time()
        if current_time - self.last_typing_time > 2:
            self.last_typing_time = current_time
            try:
                self.client.send_typing_indicator(True)
            except:
                pass

    def send_message(self):
        """Send a chat message"""
        text = self.entry.get("1.0", "end-1c").strip()
        if not text:
            return

        message_id = str(uuid.uuid4())
        reply_to = self.selected_message if self.reply_frame.winfo_ismapped() else None

        try:
            self.client.send_message(text, message_id, reply_to)
            self.entry.delete("1.0", "end")
            self.send_btn.config(state="disabled")
            self.cancel_reply()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send message:\n{e}")

    def attach_file(self):
        """Attach and send a file"""
        file_path = filedialog.askopenfilename(
            title="Select file to send",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.gif"),
                ("Documents", "*.pdf *.txt *.doc *.docx"),
                ("All files", "*.*")
            ]
        )

        if not file_path:
            return

        # Check file size (limit to 5MB)
        file_size = os.path.getsize(file_path)
        if file_size > 5 * 1024 * 1024:
            messagebox.showerror("Error", "File too large (max 5MB)")
            return

        try:
            with open(file_path, "rb") as f:
                file_data = f.read()

            filename = os.path.basename(file_path)
            file_type = os.path.splitext(filename)[1]
            file_data_b64 = base64.b64encode(file_data).decode()

            message_id = str(uuid.uuid4())
            self.client.upload_file(message_id, filename, file_type, file_data_b64)

            # Send a message about the file
            self.client.send_message(f"📎 {filename}", message_id)

        except Exception as e:
            messagebox.showerror("Error", f"Failed to send file:\n{e}")

    def display_message(self, sender, text, message_id, timestamp, is_me, reply_to=None, edited=False):
        """Display a message in the chat"""
        self.chat.config(state="normal")

        # Store message info
        self.messages[message_id] = {
            "sender": sender,
            "text": text,
            "timestamp": timestamp,
            "is_me": is_me
        }

        # Display sender name
        tag = "sender_me" if is_me else "sender_other"
        self.chat.insert("end", f"{sender}\n", (tag,))

        # Display message text
        bubble_tag = "bubble_me" if is_me else "bubble_other"
        self.chat.insert("end", f"{text}\n", (bubble_tag,))

        # Display timestamp and edited indicator
        timestamp_text = timestamp
        if edited:
            timestamp_text += " (edited)"
        self.chat.insert("end", f"{timestamp_text}\n\n", ("timestamp",))

        self.chat.config(state="disabled")
        self.chat.see("end")

        # Mark as read
        if not is_me:
            try:
                self.client.mark_as_read(message_id)
            except:
                pass

    def update_typing_indicator(self, users):
        """Update typing indicator"""
        if not users:
            self.typing_label.config(text="")
        elif len(users) == 1:
            self.typing_label.config(text=f"{users[0]} is typing...")
        elif len(users) == 2:
            self.typing_label.config(text=f"{users[0]} and {users[1]} are typing...")
        else:
            self.typing_label.config(text=f"{len(users)} people are typing...")

    def start_receive_thread(self):
        """Start background thread to receive messages"""
        threading.Thread(target=self.receive_loop, daemon=True).start()

    def receive_loop(self):
        """Receive and handle incoming messages"""
        while True:
            try:
                data = self.client.recv()
                if not data:
                    self.root.after(0, self.on_disconnected)
                    break

                msg_type = data.get("type")

                if msg_type == "chat":
                    sender = data["sender"]
                    message = data["message"]
                    message_id = data["message_id"]
                    timestamp = data["timestamp"]
                    edited = data.get("edited", False)
                    is_me = sender == self.client.username

                    self.root.after(
                        0,
                        lambda: self.display_message(
                            sender, message, message_id, timestamp, is_me, edited=edited
                        )
                    )

                elif msg_type == "typing":
                    users = data.get("users", [])
                    self.root.after(0, lambda: self.update_typing_indicator(users))

                elif msg_type == "user_joined":
                    username = data["username"]
                    users = data["users"]
                    self.root.after(
                        0,
                        lambda: self.status_label.config(text=f"🟢 {len(users)} online")
                    )
                    if username != self.client.username:
                        self.root.after(
                            0,
                            lambda: self.show_system_message(f"{username} joined")
                        )

                elif msg_type == "user_left":
                    username = data["username"]
                    users = data["users"]
                    self.root.after(
                        0,
                        lambda: self.status_label.config(text=f"🟢 {len(users)} online")
                    )
                    self.root.after(
                        0,
                        lambda: self.show_system_message(f"{username} left")
                    )

                elif msg_type == "message_edited":
                    # Handle message edit
                    pass

                elif msg_type == "message_deleted":
                    # Handle message deletion
                    pass

            except Exception as e:
                print(f"Receive error: {e}")
                break

    def show_system_message(self, text):
        """Show system message (user joined/left, etc.)"""
        self.chat.config(state="normal")
        self.chat.insert("end", f"── {text} ──\n\n", ("system",))
        self.chat.config(state="disabled")
        self.chat.see("end")

    def on_disconnected(self):
        """Handle dis***"""
        messagebox.showerror("Disconnected", "Lost *** to server")
        self.root.destroy()

    def on_closing(self):
        """Handle window closing"""
        if messagebox.askokcancel("Quit", "Do you want to leave the chat room?"):
            try:
                self.client.close()
            except:
                pass
            self.root.destroy()
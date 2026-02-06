# client/login_ui.py
import tkinter as tk
from tkinter import messagebox
from client.socket_client import ChatClient
from client.room_ui import RoomSelector


class LoginWindow:
    """Enhanced login window with modern UI"""

    def __init__(self, host="127.0.0.1", port=5555):
        self.host = host
        self.port = port
        self.client = None

        self.root = tk.Tk()
        self.root.title("WhatsApp-like Chat - Login")
        self.root.geometry("400x500")
        self.root.resizable(False, False)
        self.root.configure(bg="#075e54")

        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        """Create UI elements"""

        # Header
        header_frame = tk.Frame(self.root, bg="#075e54")
        header_frame.pack(fill="x", pady=(20, 10))

        tk.Label(
            header_frame,
            text="💬",
            font=("Segoe UI", 48),
            bg="#075e54",
            fg="white"
        ).pack()

        tk.Label(
            header_frame,
            text="Advanced Chat",
            font=("Segoe UI", 20, "bold"),
            bg="#075e54",
            fg="white"
        ).pack()

        tk.Label(
            header_frame,
            text="Connect with friends securely",
            font=("Segoe UI", 10),
            bg="#075e54",
            fg="#dcf8c6"
        ).pack()

        # Main form
        form_frame = tk.Frame(self.root, bg="white")
        form_frame.pack(fill="both", expand=True, padx=30, pady=20)

        # Username
        tk.Label(
            form_frame,
            text="Username",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor="w", pady=(20, 5))

        self.username_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 12),
            relief="solid",
            bd=1
        )
        self.username_entry.pack(fill="x", ipady=8)
        self.username_entry.focus_set()

        # Password
        tk.Label(
            form_frame,
            text="Password",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg="#333"
        ).pack(anchor="w", pady=(15, 5))

        self.password_entry = tk.Entry(
            form_frame,
            font=("Segoe UI", 12),
            relief="solid",
            bd=1,
            show="●"
        )
        self.password_entry.pack(fill="x", ipady=8)

        # Show password checkbox
        self.show_password_var = tk.BooleanVar()
        tk.Checkbutton(
            form_frame,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_password,
            bg="white",
            font=("Segoe UI", 9)
        ).pack(anchor="w", pady=(5, 0))

        # Buttons frame
        buttons_frame = tk.Frame(form_frame, bg="white")
        buttons_frame.pack(fill="x", pady=(30, 10))

        # LOGIN BUTTON
        self.login_btn = tk.Button(
            buttons_frame,
            text="Login",
            font=("Segoe UI", 11, "bold"),
            bg="#25d366",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.login,
            padx=20,
            pady=10
        )
        self.login_btn.pack(fill="x", pady=(0, 5))

        # REGISTER BUTTON
        self.register_btn = tk.Button(
            buttons_frame,
            text="Register New Account",
            font=("Segoe UI", 11),
            bg="#34b7f1",
            fg="white",
            relief="flat",
            cursor="hand2",
            command=self.register,
            padx=20,
            pady=10
        )
        self.register_btn.pack(fill="x", pady=(5, 5))

        # Bind Enter key
        self.root.bind("<Return>", lambda e: self.login())

        # Server info
        tk.Label(
            form_frame,
            text=f"Server: {self.host}:{self.port}",
            font=("Segoe UI", 8),
            bg="white",
            fg="gray"
        ).pack(side="bottom", pady=(20, 10))

    def toggle_password(self):
        """Toggle password visibility"""
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="●")

    def validate_inputs(self):
        """Validate username and password"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not username:
            messagebox.showerror("Error", "Please enter a username")
            return None, None

        if len(username) < 3:
            messagebox.showerror("Error", "Username must be at least 3 characters")
            return None, None

        if not password:
            messagebox.showerror("Error", "Please enter a password")
            return None, None

        if len(password) < 6:
            messagebox.showerror("Error", "Password must be at least 6 characters")
            return None, None

        return username, password

    def login(self):
        """Handle login"""
        username, password = self.validate_inputs()
        if not username:
            return

        self.login_btn.config(state="disabled", text="Connecting...")
        self.register_btn.config(state="disabled")
        self.root.update()

        try:
            self.client = ChatClient(self.host, self.port)
            success, message = self.client.authenticate(username, password, action="login")

            if success:
                messagebox.showinfo("Success", f"Welcome back, {username}!")
                self.root.destroy()
                RoomSelector(self.client)
            else:
                messagebox.showerror("Login Failed", message)
                self.login_btn.config(state="normal", text="Login")
                self.register_btn.config(state="normal")

        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server:\n{e}")
            self.login_btn.config(state="normal", text="Login")
            self.register_btn.config(state="normal")

    def register(self):
        """Handle registration"""
        username, password = self.validate_inputs()
        if not username:
            return

        self.login_btn.config(state="disabled")
        self.register_btn.config(state="disabled", text="Creating account...")
        self.root.update()

        try:
            self.client = ChatClient(self.host, self.port)
            success, message = self.client.authenticate(username, password, action="register")

            if success:
                messagebox.showinfo("Success", f"Account created! Welcome, {username}!")
                self.root.destroy()
                RoomSelector(self.client)
            else:
                messagebox.showerror("Registration Failed", message)
                self.login_btn.config(state="normal")
                self.register_btn.config(state="normal", text="Register")

        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot connect to server:\n{e}")
            self.login_btn.config(state="normal")
            self.register_btn.config(state="normal", text="Register")


if __name__ == "__main__":
    LoginWindow()
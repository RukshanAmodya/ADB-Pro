import os
import json
import threading
import subprocess
import time
import paramiko
import customtkinter as ctk
from tkinter import filedialog, messagebox

# --- Settings Management ---
SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {
    "ip": "18.141.179.160",
    "user": "ubuntu",
    "key_path": "AWSRR2.pem",
    "alive_interval": 30,
    "alive_count_max": 3
}

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except:
            return DEFAULT_SETTINGS
    return DEFAULT_SETTINGS

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

# --- Modern UI Setup ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ADBTunnelApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("ADB Pro | Remote Tunneling")
        self.geometry("1000x700")
        self.configure(fg_color="#0f0f0f") # Deep dark background
        
        # Grid layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.settings = load_settings()
        self.running = False
        self.workflow_thread = None
        self.workflow_lock = threading.Lock()
        self.adb_server_process = None
        self.ssh_tunnel_process = None
        self.stop_event = threading.Event()

        self.setup_ui()

    def setup_ui(self):
        # Sidebar for Settings
        self.sidebar = ctk.CTkFrame(self, width=300, corner_radius=0, fg_color="#161616", border_width=1, border_color="#333333")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="ADB PRO", font=ctk.CTkFont(size=28, weight="bold"))
        self.logo_label.pack(pady=(40, 5))
        self.sub_logo = ctk.CTkLabel(self.sidebar, text="REMOTE TUNNEL ENGINE", font=ctk.CTkFont(size=10, weight="bold"), text_color="#3498db")
        self.sub_logo.pack(pady=(0, 30))

        # Settings Section
        self.settings_container = ctk.CTkScrollableFrame(self.sidebar, fg_color="transparent", label_text="CONFIGURATION", label_font=ctk.CTkFont(size=12, weight="bold"))
        self.settings_container.pack(fill="both", expand=True, padx=15, pady=10)

        self.ip_entry = self.create_setting_input(self.settings_container, "Server IP Address", self.settings["ip"])
        self.user_entry = self.create_setting_input(self.settings_container, "SSH Username", self.settings["user"])
        
        self.alive_interval_entry = self.create_setting_input(self.settings_container, "Server Alive Interval (s)", self.settings.get("alive_interval", 30))
        self.alive_count_entry = self.create_setting_input(self.settings_container, "Server Alive Count Max", self.settings.get("alive_count_max", 3))
        
        # Key Path with Browser
        lbl = ctk.CTkLabel(self.settings_container, text="SSH Private Key (.pem)", font=ctk.CTkFont(size=12))
        lbl.pack(pady=(15, 0), padx=5, anchor="w")
        
        self.key_frame = ctk.CTkFrame(self.settings_container, fg_color="transparent")
        self.key_frame.pack(fill="x", padx=5)
        
        self.key_path_var = ctk.StringVar(value=self.settings["key_path"])
        self.key_entry = ctk.CTkEntry(self.key_frame, textvariable=self.key_path_var, font=ctk.CTkFont(size=12), border_color="#444444")
        self.key_entry.pack(side="left", fill="x", expand=True, pady=5)
        
        self.browse_btn = ctk.CTkButton(self.key_frame, text="📁", width=35, command=self.browse_key, fg_color="#333333", hover_color="#444444")
        self.browse_btn.pack(side="right", padx=(5, 0))

        self.save_btn = ctk.CTkButton(self.sidebar, text="APPLY SETTINGS", command=self.update_settings, 
                                      fg_color="#1abc9c", hover_color="#16a085", height=40, font=ctk.CTkFont(weight="bold"))
        self.save_btn.pack(pady=20, padx=25, fill="x")

        # Copyright Section
        self.copyright_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.copyright_frame.pack(side="bottom", pady=20, padx=15, fill="x")
        
        self.cp_label = ctk.CTkLabel(self.copyright_frame, text="© 2026 QuestraX\nAll Rights Reserved", 
                                     font=ctk.CTkFont(size=10), text_color="#555555")
        self.cp_label.pack()
        
        self.yt_link = ctk.CTkLabel(self.copyright_frame, text="youtube.com/@QuestraX", 
                                    font=ctk.CTkFont(size=10, underline=True), text_color="#3498db", cursor="hand2")
        self.yt_link.pack(pady=(5, 0))
        self.yt_link.bind("<Button-1>", lambda e: self.open_yt())

    def open_yt(self):
        import webbrowser
        webbrowser.open("https://www.youtube.com/@QuestraX")

        # Main Content Area
        self.main_content = ctk.CTkFrame(self, corner_radius=20, fg_color="#1a1a1a", border_width=1, border_color="#2a2a2a")
        self.main_content.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)
        
        # Header / Status Card
        self.status_frame = ctk.CTkFrame(self.main_content, height=120, corner_radius=15, fg_color="#222222", border_width=1, border_color="#333333")
        self.status_frame.pack(fill="x", padx=25, pady=25)
        
        # Connection Status Visuals
        self.status_indicator = ctk.CTkFrame(self.status_frame, width=12, height=12, corner_radius=6, fg_color="#e74c3c")
        self.status_indicator.place(x=30, rely=0.5, anchor="center")
        
        self.status_text = ctk.CTkLabel(self.status_frame, text="SYSTEM OFFLINE", font=ctk.CTkFont(size=20, weight="bold"))
        self.status_text.place(x=55, rely=0.42, anchor="w")
        
        self.status_subtext = ctk.CTkLabel(self.status_frame, text="Tunnel is not active", font=ctk.CTkFont(size=12), text_color="gray")
        self.status_subtext.place(x=55, rely=0.62, anchor="w")
        
        self.action_btn = ctk.CTkButton(self.status_frame, text="START ENGINE", font=ctk.CTkFont(size=15, weight="bold"), 
                                         height=50, width=180, corner_radius=10, command=self.toggle_connection,
                                         fg_color="#3498db", hover_color="#2980b9")
        self.action_btn.place(relx=0.95, rely=0.5, anchor="e")

        # Log Terminal Section
        self.term_frame = ctk.CTkFrame(self.main_content, corner_radius=15, fg_color="#000000", border_width=1, border_color="#333333")
        self.term_frame.pack(fill="both", expand=True, padx=25, pady=(0, 25))
        
        self.term_header = ctk.CTkFrame(self.term_frame, height=35, corner_radius=0, fg_color="#111111")
        self.term_header.pack(fill="x")
        
        self.term_title = ctk.CTkLabel(self.term_header, text="COMMAND TERMINAL", font=ctk.CTkFont(size=11, weight="bold"), text_color="#666666")
        self.term_title.pack(side="left", padx=15)

        self.terminal = ctk.CTkTextbox(self.term_frame, font=ctk.CTkFont(family="Consolas", size=13), 
                                        text_color="#00ff00", fg_color="transparent", border_width=0)
        self.terminal.pack(fill="both", expand=True, padx=10, pady=10)
        self.terminal.insert("0.0", ">>> Initialize System...\n")
        self.terminal.configure(state="disabled")

    def create_setting_input(self, parent, label, default_val):
        lbl = ctk.CTkLabel(parent, text=label, font=ctk.CTkFont(size=12))
        lbl.pack(pady=(15, 0), padx=5, anchor="w")
        entry = ctk.CTkEntry(parent, font=ctk.CTkFont(size=13), border_color="#444444")
        entry.insert(0, default_val)
        entry.pack(pady=5, padx=5, fill="x")
        return entry

    def browse_key(self):
        filename = filedialog.askopenfilename(filetypes=[("PEM files", "*.pem"), ("All files", "*.*")])
        if filename:
            self.key_path_var.set(filename)

    def update_settings(self):
        self.settings["ip"] = self.ip_entry.get()
        self.settings["user"] = self.user_entry.get()
        self.settings["key_path"] = self.key_path_var.get()
        self.settings["alive_interval"] = int(self.alive_interval_entry.get())
        self.settings["alive_count_max"] = int(self.alive_count_entry.get())
        save_settings(self.settings)
        messagebox.showinfo("Settings", "Settings saved successfully!")

    def log(self, message):
        self.terminal.configure(state="normal")
        timestamp = time.strftime("[%H:%M:%S] ")
        self.terminal.insert("end", f"{timestamp}{message}\n")
        self.terminal.see("end")
        self.terminal.configure(state="disabled")

    def set_status(self, connected, text="CONNECTED", subtext="Tunnel is active"):
        if connected:
            self.status_indicator.configure(fg_color="#2ecc71")
            self.status_text.configure(text=text)
            self.status_subtext.configure(text=subtext)
            self.action_btn.configure(text="STOP ENGINE", fg_color="#e74c3c", hover_color="#c0392b")
        else:
            self.status_indicator.configure(fg_color="#e74c3c")
            self.status_text.configure(text="SYSTEM OFFLINE")
            self.status_subtext.configure(text="Tunnel is not active")
            self.action_btn.configure(text="START ENGINE", fg_color="#3498db", hover_color="#2980b9")

    def toggle_connection(self):
        if not self.running:
            self.start_process()
        else:
            self.stop_process()

    def start_process(self):
        if self.running:
            return
        self.running = True
        self.stop_event.clear()
        self.set_status(True, "INITIALIZING...")
        self.action_btn.configure(state="disabled")
        self.workflow_thread = threading.Thread(target=self.run_workflow, daemon=True)
        self.workflow_thread.start()

    def stop_process(self):
        self.running = False
        self.stop_event.set()
        self.log("Stopping all processes...")
        
        # Terminate processes immediately
        if self.adb_server_process:
            try:
                self.adb_server_process.terminate()
            except:
                pass
        
        if self.ssh_tunnel_process:
            try:
                self.ssh_tunnel_process.terminate()
            except:
                pass
            
        self.set_status(False)
        self.action_btn.configure(state="normal")
        self.log("Disconnected.")


    def run_workflow(self):
        # Use a lock to ensure only one thread runs the workflow logic at a time
        if not self.workflow_lock.acquire(blocking=False):
            return
            
        try:
            while self.running:
                try:
                    # Cleanup previous processes if any
                    if self.adb_server_process: 
                        try: self.adb_server_process.terminate()
                        except: pass
                    if self.ssh_tunnel_process: 
                        try: self.ssh_tunnel_process.terminate()
                        except: pass
                    
                    if not self.running: break

                    # Step 1: Kill local ADB
                    self.log("Step 1: Killing local ADB server (Port 5038)...")
                    env = os.environ.copy()
                    env["ANDROID_ADB_SERVER_PORT"] = "5038"
                    subprocess.run(["adb", "kill-server"], capture_output=True, shell=True, env=env)
                    
                    if not self.running: break

                    # Step 2: Start local ADB server
                    self.log("Step 2: Starting local ADB server on Port 5038...")
                    self.adb_server_process = subprocess.Popen(
                        ["adb", "-a", "nodaemon", "server"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        shell=True,
                        env=env
                    )
                    
                    if not self.running: break

                    # Step 3: Remote SSH - Clean Port
                    self.log(f"Step 3: Cleaning port 5037 on {self.settings['ip']}...")
                    self.ssh_exec_command(f"sudo fuser -k 5037/tcp") # Ignore failures here as it might not be in use

                    if not self.running: break

                    # Step 4: Establish Tunnel
                    self.log("Step 4: Establishing SSH Reverse Tunnel...")
                    ssh_cmd = [
                        "ssh", "-o", "StrictHostKeyChecking=no", "-o", "ExitOnForwardFailure=yes",
                        "-o", f"ServerAliveInterval={self.settings.get('alive_interval', 30)}",
                        "-o", f"ServerAliveCountMax={self.settings.get('alive_count_max', 3)}",
                        "-i", self.settings["key_path"],
                        "-R", "5037:127.0.0.1:5038",
                        f"{self.settings['user']}@{self.settings['ip']}",
                        "while true; do sleep 10; done"
                    ]
                    
                    self.ssh_tunnel_process = subprocess.Popen(
                        ssh_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True
                    )
                    
                    # Give it time to establish
                    for _ in range(6): # Wait up to 3 seconds
                        if not self.running: break
                        if self.ssh_tunnel_process.poll() is not None:
                            break
                        time.sleep(0.5)
                    
                    if not self.running: break

                    if self.ssh_tunnel_process.poll() is not None:
                        _, stderr = self.ssh_tunnel_process.communicate()
                        if "remote port forwarding failed" in stderr.lower():
                            self.log("Error: Remote port forwarding failed. Retrying Step 3...")
                            continue
                        raise Exception(f"SSH Tunnel failed: {stderr.strip()}")

                    # Step 5: Check Connection
                    self.log("Step 5: Verifying connection on server...")
                    # We check if 'adb devices' works on the remote side
                    # It should return 0 if it can connect to the daemon
                    check_cmd = "export ADB_SERVER_SOCKET=tcp:127.0.0.1:5037 && adb devices"
                    success, output, error = self.ssh_exec_command(check_cmd)
                    
                    if success:
                        self.log("Success! Tunnel established and ADB responsive.")
                        self.set_status(True, "CONNECTED")
                        self.action_btn.configure(state="normal")
                    else:
                        self.log(f"Verification failed: {error or output}")
                        # If verification fails, we might need to retry or stop
                        if self.running:
                            self.log("Retrying in 5 seconds...")
                            time.sleep(5)
                            continue
                        else:
                            break

                    # Monitor the tunnel
                    while self.running:
                        if self.ssh_tunnel_process.poll() is not None:
                            self.log("SSH Tunnel connection lost. Reconnecting...")
                            break
                        time.sleep(2)
                    
                    if not self.running: break
                    
                except Exception as e:
                    if self.running:
                        self.log(f"Workflow Error: {str(e)}")
                        self.log("Retrying in 5 seconds...")
                        time.sleep(5)
                    else:
                        break
        finally:
            self.workflow_lock.release()

    def ssh_exec_command(self, command):
        """Executes a command via SSH and returns (success, stdout, stderr)"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(
                hostname=self.settings["ip"],
                username=self.settings["user"],
                key_filename=self.settings["key_path"],
                timeout=10
            )
            stdin, stdout, stderr = ssh.exec_command(command)
            
            # Wait for command to complete
            exit_status = stdout.channel.recv_exit_status()
            
            output = stdout.read().decode().strip()
            error = stderr.read().decode().strip()
            ssh.close()
            
            if error and "sudo" not in error.lower() and "list of devices" not in error.lower():
                self.log(f"Remote info: {error}")
                
            return (exit_status == 0), output, error
        except Exception as e:
            self.log(f"SSH Exec Error: {str(e)}")
            return False, "", str(e)

if __name__ == "__main__":
    app = ADBTunnelApp()
    app.mainloop()


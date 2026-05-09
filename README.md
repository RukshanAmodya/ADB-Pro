# 🚀 ADB Pro | Remote Tunneling Engine

![ADB Pro Banner](https://img.shields.io/badge/ADB--Pro-Remote--Tunneling-blue?style=for-the-badge&logo=android)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-black?style=for-the-badge)
![License](https://img.shields.io/badge/License-All--Rights--Reserved-red?style=for-the-badge)

**ADB Pro** is a high-performance, modern desktop application designed to bridge the gap between local development environments and remote Android devices. It automates the complex process of SSH reverse tunneling, allowing you to debug remote Android devices as if they were plugged directly into your local machine.

---

## ✨ Key Features

-   **💎 Modern UI**: Sleek, Dark-themed interface built with `CustomTkinter` for a premium user experience.
-   **🔄 Auto-Reconnect**: Intelligent monitoring system that detects connection drops and automatically restores the tunnel.
-   **🛠️ Automated Workflow**:
    -   Kills conflicting local ADB instances.
    -   Starts a dedicated local ADB server on port `5038`.
    -   Cleans remote ports (`5037`) using `fuser` via SSH.
    -   Establishes a secure SSH Reverse Tunnel (`-R 5037:127.0.0.1:5038`).
-   **🔒 Secure**: Uses SSH key-based authentication (`.pem` files) for all remote connections.
-   **📊 Real-time Logs**: Integrated command terminal to monitor every step of the tunneling process.

---

## 📸 Interface Preview

*(The app features a premium glassmorphism-inspired design with real-time status indicators and a dedicated log terminal.)*

---

## 🚀 Getting Started

### Prerequisites
-   Local machine: **ADB** (Android Debug Bridge) installed.
-   Remote server: **ADB** installed and SSH access enabled.
-   Python 3.10+ (if running from source).

### Installation (Source)
1.  Clone the repository:
    ```bash
    git clone https://github.com/RukshanAmodya/ADB-Pro.git
    cd ADB-Pro
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    *(Dependencies: `customtkinter`, `paramiko`)*

3.  Run the app:
    ```bash
    python main.py
    ```

---

## 🛠️ Usage Instructions

1.  **Configure Settings**: Enter your Server IP, SSH Username, and select your `.pem` private key.
2.  **Start Engine**: Click the **"START ENGINE"** button.
3.  **Monitor**: Watch the terminal logs as the system initializes the local server and establishes the tunnel.
4.  **Debug**: Once you see **"Success! Tunnel established"**, you can run `adb devices` on your **remote server**, and it will show your local devices!

---

## 📦 Building Standalone EXE

If you want to build the `.exe` file yourself:
```bash
pyinstaller --clean ADB_Pro.spec
```
The output will be in the `dist/` directory.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/RukshanAmodya/ADB-Pro/issues).

## 📄 License & Copyright

**Copyright © 2026 QuestraX. All Rights Reserved.**

This software is proprietary. Unauthorized copying, modification, distribution, or reverse engineering of this software, via any medium, is strictly prohibited. 

For copyright inquiries and updates, please visit our official channel:
[📺 QuestraX YouTube Channel](https://www.youtube.com/@QuestraX)

---

<p align="center">
  Developed with ❤️ by <b>QuestraX</b>
</p>

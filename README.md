# Subscription & Bill Reminder - Setup Guide

## 📋 Overview
This is a Python Flask web application that runs as a service on your computer. You can access it from any device on your network using a URL.

## ✅ Prerequisites
- Python 3.8 or higher installed
- Windows operating system
- Your computer should be on the same WiFi as your mobile device (or accessible via IP)

## 🚀 Installation Steps

### Step 1: Install Python Dependencies
1. Open Command Prompt or PowerShell
2. Navigate to the project folder:
```bash
cd "H:\claude-code\subscription-reminder-app"
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

### Step 2: Run the Application

**Option A: Quick Start (Manual)**
```bash
python app.py
```
The app will start on `http://localhost:5000`

**Option B: Always Running (Recommended)**
Use the provided batch script to keep the app running even if you close the window:
- Double-click `run_server.bat`
- Or run from PowerShell: `.\run_server.bat`

The app will run in the background and restart automatically if it crashes.

### Step 3: Access from Your Mobile

1. **Find Your Computer's IP Address:**
   - Open Command Prompt
   - Type: `ipconfig`
   - Look for "IPv4 Address" (usually something like `192.168.x.x`)

2. **On Your Mobile Phone:**
   - Open a web browser
   - Enter: `http://YOUR_COMPUTER_IP:5000`
   - Example: `http://192.168.1.100:5000`

3. **Save as Bookmark** for easy access

## 📱 Features

✅ Add/Edit/Delete subscriptions  
✅ Track OTT platforms (Netflix, Prime Video, Disney+, etc.)  
✅ Track utility bills (Electricity, Water, Internet)  
✅ Track AI subscriptions (Claude Pro, ChatGPT Plus)  
✅ See days remaining and status  
✅ Monthly cost calculation  
✅ Export/Import data  
✅ Works on all devices (mobile, tablet, desktop)  
✅ Responsive design  

## 🛠️ Troubleshooting

### App won't start
- Make sure Python is installed: `python --version`
- Check if port 5000 is not in use
- Try: `python app.py --port 5001`

### Can't access from mobile
- Ensure both devices are on the same WiFi
- Check firewall settings (Windows Firewall may block port 5000)
- Verify the correct IP address
- Try pinging your computer from mobile: `ping 192.168.x.x`

### Allow Windows Firewall
1. Search for "Firewall" in Windows
2. Click "Allow an app through firewall"
3. Find Python in the list and allow it
4. Or run Command Prompt as admin:
```bash
netsh advfirewall firewall add rule name="Flask App" dir=in action=allow program="C:\Path\To\Python\python.exe" enable=yes
```

## 🔄 Keep App Running 24/7

### Using Windows Task Scheduler
1. Open Task Scheduler
2. Create Basic Task → "Subscription Reminder App"
3. Trigger: "At startup"
4. Action: Start program → `C:\Users\ARPIT JAIN\subscription-reminder-app\run_server.bat`
5. Check "Run whether user is logged in or not"

### Using batch file (Easier)
The `run_server.bat` file automatically restarts the app if it crashes.

## 📊 Database
- Data stored in SQLite database: `subscriptions.db`
- Automatically created on first run
- Located in the project folder
- Backup: Copy `subscriptions.db` to keep a backup

## 🔐 Security Notes
- ✅ App runs locally on your network
- ✅ No data sent to external servers
- ✅ Only accessible from your home/office network
- 🔒 For internet access, use VPN or set up port forwarding (advanced)

## 📝 Usage Examples

### Add a subscription
1. Click "+ Add New"
2. Fill in: Name, Category, Renewal Date, Cost
3. Click "Add Subscription"

### Check status
- Dashboard shows total subscriptions
- "Due This Week" alerts
- "Monthly Spend" total
- "Overdue" count

### Export data
- Click "Export" button
- Download as JSON file
- Keep as backup

## 🆘 Still having issues?

1. Check Python version: `python --version`
2. Verify all requirements installed: `pip list`
3. Check if Flask is working: `python -c "import flask; print(flask.__version__)"`
4. Run with debug mode: `python app.py --debug`

## 📞 Support
For Flask issues: https://flask.palletsprojects.com/
For SQLAlchemy issues: https://docs.sqlalchemy.org/

---

**Happy tracking! 💰**
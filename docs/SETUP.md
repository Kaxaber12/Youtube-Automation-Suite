# 🚀 Setup Guide

<div align="center">

**Complete Installation & Configuration Walkthrough**

Get your YouTube Automation Suite up and running in minutes!

[💻 Installation](#installation) • [🔑 Google API](#google-api-configuration) • [✅ Verification](#verification) • [🔧 Troubleshooting](#troubleshooting)

</div>

---

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Google API Configuration](#google-api-configuration)
- [First Run](#first-run)
- [Verification](#verification)
- [Troubleshooting](#troubleshooting)

---

## 💻 System Requirements

### ✅ What You'll Need

<table>
<thead>
<tr>
<th align="center">Component</th>
<th align="center">Minimum</th>
<th align="center">Recommended</th>
<th align="center">Notes</th>
</tr>
</thead>
<tbody>
<tr>
<td align="center">🖥️ <b>OS</b></td>
<td>Windows 10 / macOS 10.15 / Ubuntu 18.04</td>
<td>Latest versions</td>
<td>Cross-platform support</td>
</tr>
<tr>
<td align="center">🐍 <b>Python</b></td>
<td>3.8</td>
<td>3.9+</td>
<td>Check with <code>python --version</code></td>
</tr>
<tr>
<td align="center">💾 <b>RAM</b></td>
<td>4GB</td>
<td>8GB+</td>
<td>For smooth GUI performance</td>
</tr>
<tr>
<td align="center">💿 <b>Storage</b></td>
<td>500MB</td>
<td>1GB</td>
<td>Includes dependencies & logs</td>
</tr>
<tr>
<td align="center">🌐 <b>Internet</b></td>
<td colspan="2" align="center">Stable connection</td>
<td>Required for API calls</td>
</tr>
</tbody>
</table>

### Recommended Specifications

- **Python**: 3.9 or higher
- **RAM**: 8GB or more
- **Display**: 1920x1080 or higher

---

---

## 📦 Installation

### Step 1️⃣: Install Python

#### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH"
4. Complete the installation
5. Verify: Open Command Prompt and run `python --version`

#### macOS
```bash
# Using Homebrew (recommended)
brew install python3

# Or download from python.org
# Verify installation
python3 --version
```

#### Linux
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Fedora/CentOS
sudo dnf install python3 python3-pip

# Verify installation
python3 --version
```

### Step 2️⃣: Download the Project

#### Option A: Using Git (Recommended)
```bash
# Clone the repository (if available on GitHub)
# git clone https://github.com/YOUR_USERNAME/Youtube-Automation-Suite.git
# Or download the ZIP file and extract it

cd Youtube-Automation-Suite
```

#### Option B: Download ZIP
1. Visit the GitHub repository
2. Click the green "Code" button
3. Select "Download ZIP"
4. Extract to your desired location
5. Open terminal/command prompt in the extracted folder

### Step 3️⃣: Create Virtual Environment 📦

<blockquote>
💡 <b>Pro Tip:</b> Virtual environments keep your dependencies isolated and your system Python clean!
</blockquote>

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Your prompt should now show (venv)
```

### Step 4️⃣: Install Dependencies ✅

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

**Expected packages:**
- customtkinter
- google-auth
- google-auth-oauthlib
- google-api-python-client
- pillow
- requests
- colorama

---

## Google API Configuration

This is the most important step. Follow each step carefully.

**Note**: Google's interface changes occasionally. If you can't find an exact menu name, look for something similar. The process is: Create Project → Enable API → Configure OAuth → Create Credentials.

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click the project dropdown (top-left, next to "Google Cloud")
4. Click "New Project"
5. Enter project name: `YouTube-Automation`
6. Click "Create"
7. Wait for project creation (usually takes a few seconds)

### Step 2: Enable YouTube Data API v3

1. Make sure your new project is selected
2. Navigate to "APIs & Services" > "Library"
3. Search for "YouTube Data API v3"
4. Click on the result
5. Click "Enable" button
6. Wait for API to be enabled

### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type
3. Click "Create"

**Fill in the required information:**
- **App name**: `YouTube Automation Suite`
- **User support email**: Your email address
- **Developer contact information**: Your email address

4. Click "Save and Continue"
5. On the "Scopes" page, click "Add or Remove Scopes"
6. Search for `youtube` and select:
   - `.../auth/youtube.force-ssl`
7. Click "Update" then "Save and Continue"
8. Add your email as a test user
9. Click "Save and Continue"
10. Review and click "Back to Dashboard"

### Step 4: Create OAuth 2.0 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. If prompted, configure the consent screen (see Step 3)
4. Application type: Select "Desktop Application"
5. Name: `YouTube Automation Desktop Client`
6. Click "Create"
7. A dialog will appear with your Client ID and Secret - click "OK"

### Step 5: Download Credentials File

1. In the Credentials page, find your newly created OAuth 2.0 Client ID
2. Click the download icon (⬇️) on the right
3. Save the file
4. **Important**: Rename the file to exactly `credentials.json`
5. Move `credentials.json` to your project root directory

**File location should be:**
```
youtube-automation-suite/
├── credentials.json  ← Place here
├── README.md
├── requirements.txt
└── ...
```

---

## First Run

### Authentication Process

1. **Launch the Application**
   ```bash
   # GUI Version
   python src/youtube_automation_gui.py
   
   # CLI Version
   python src/youtube_automation_cli.py --action like --file examples/likes.txt
   ```

2. **Browser Authentication**
   - A browser window will automatically open
   - If not, copy the URL from the terminal and paste in your browser

3. **Google Sign-In**
   - Sign in with the Google account you want to use
   - This should be the account associated with your YouTube channel

4. **Grant Permissions**
   - You may see "This app isn't verified" warning
   - Click "Advanced" > "Go to YouTube Automation Suite (unsafe)"
   - This is safe - it's your own application
   - Click "Allow" to grant permissions
   - Grant access to "Manage your YouTube account"

5. **Success**
   - You should see "The authentication flow has completed"
   - Return to the application
   - A `token.json` file will be created automatically

**Security Note**: The `token.json` file contains your authentication token. Keep it secure and never share it.

---

## Verification

### Test the Installation

1. **Verify Credentials**
   ```bash
   # Check if credentials.json exists
   ls credentials.json  # macOS/Linux
   dir credentials.json  # Windows
   ```

2. **Test GUI Launch**
   ```bash
   python src/youtube_automation_gui.py
   ```
   - Application window should open
   - No error messages in terminal
   - Status shows "Ready"

3. **Test CLI Help**
   ```bash
   python src/youtube_automation_cli.py --help
   ```
   - Should display help information
   - No import errors

4. **Test Authentication**
   - After first authentication, `token.json` should be created
   - Subsequent runs should not require re-authentication

---

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'customtkinter'"

**Solution:**
```bash
pip install customtkinter
# Or reinstall all dependencies
pip install -r requirements.txt --force-reinstall
```

#### "FileNotFoundError: credentials.json"

**Solution:**
- Verify `credentials.json` is in the project root directory
- Check the filename is exactly `credentials.json` (not `credentials (1).json`)
- Ensure you downloaded the correct file from Google Cloud Console

#### "Invalid credentials" or Authentication Errors

**Solution:**
```bash
# Delete old token
rm token.json  # macOS/Linux
del token.json  # Windows

# Re-run the application to re-authenticate
python src/youtube_automation_gui.py
```

#### GUI Won't Start on Linux

**Solution:**
```bash
# Install tkinter
sudo apt-get install python3-tk

# Or use CLI version
python src/youtube_automation_cli.py --help
```

#### API Quota Exceeded

**Solution:**
- Wait 24 hours for quota reset
- Check usage at [Google Cloud Console Quotas](https://console.cloud.google.com/iam-admin/quotas)
- Request quota increase if needed

### Getting More Help

- 📖 Check the [User Guide](USER_GUIDE.md) for detailed usage
- 📚 Review [Best Practices](BEST_PRACTICES.md) for optimization tips
- 💬 Contact: haseebkaloya@gmail.com

---

## Next Steps

After successful setup:

1. Read the [User Guide](USER_GUIDE.md) for usage instructions
2. Check [Best Practices](BEST_PRACTICES.md) for optimization tips
3. Prepare your input files (likes.txt, comments.txt, channels.txt)
4. Start with small test batches (5-10 items)
5. Review example files in the `examples/` directory

---

<div align="center">

**Setup Complete! 🎉**

Ready to start automating? Check out the [User Guide](USER_GUIDE.md)

[⬆ Back to Top](#setup-guide---youtube-automation-suite)

</div>

# 🤝 Contributing to YouTube Automation Suite

<div align="center">

**Thank you for your interest in contributing!**

This guide will help you get started with contributing to the project.

[🚀 Getting Started](#-getting-started) • [💻 Development](#-development-setup) • [✍️ Code Style](#️-coding-standards) • [📝 Pull Requests](#-pull-request-process)

</div>

---

## 👨‍💻 Project Maintainer

<table>
<tr>
<td>

**Haseeb Kaloya**  
📧 haseebkaloya@gmail.com  
📱 +92 3294163702

</td>
</tr>
</table>

---

## 📋 Table of Contents

- [Code of Conduct](#-code-of-conduct)
- [Getting Started](#-getting-started)
- [Types of Contributions](#-types-of-contributions)
- [Development Setup](#-development-setup)
- [Coding Standards](#️-coding-standards)
- [Pull Request Process](#-pull-request-process)
- [Reporting Bugs](#-reporting-bugs)
- [Suggesting Features](#-suggesting-features)

---

## 📜 Code of Conduct

This project follows a Code of Conduct that all contributors must adhere to.

<table>
<tr>
<td width="25%" align="center">🤝<br><b>Be Respectful</b></td>
<td width="25%" align="center">💡<br><b>Be Constructive</b></td>
<td width="25%" align="center">🌍<br><b>Be Inclusive</b></td>
<td width="25%" align="center">❤️<br><b>Be Kind</b></td>
</tr>
</table>

👉 Read the full [Code of Conduct](CODE_OF_CONDUCT.md)

---

## 🚀 Getting Started

### Prerequisites

<table>
<tr>
<td width="50%">

**Required Knowledge**
- 🐍 Python 3.8+
- 🔧 Git basics
- 📚 YouTube API understanding

</td>
<td width="50%">

**Optional Knowledge**
- 🎨 CustomTkinter (for GUI)
- 📝 Markdown
- 🧪 Testing frameworks

</td>
</tr>
</table>

### First-Time Contributors

```bash
# 1️⃣ Fork the repository on GitHub (if available)

# 2️⃣ Clone your fork or download the project
# git clone https://github.com/your-username/Youtube-Automation-Suite.git
cd Youtube-Automation-Suite

# 3️⃣ Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 4️⃣ Install dependencies
pip install -r requirements.txt
```

---

## 🎯 Types of Contributions

We welcome various types of contributions:

<table>
<tr>
<td align="center" width="20%">
🐛<br><b>Bug Reports</b><br>Found an issue?<br>Report it!
</td>
<td align="center" width="20%">
🔧<br><b>Bug Fixes</b><br>Fix existing<br>issues
</td>
<td align="center" width="20%">
✨<br><b>New Features</b><br>Add new<br>functionality
</td>
<td align="center" width="20%">
📖<br><b>Documentation</b><br>Improve docs<br>& examples
</td>
<td align="center" width="20%">
🧪<br><b>Tests</b><br>Add test<br>coverage
</td>
</tr>
</table>

### 🏷️ Good First Issues

Look for issues labeled:
- 🟢 `good first issue` - Perfect for newcomers
- 🆘 `help wanted` - Community assistance needed
- 📚 `documentation` - Documentation improvements

---

## 💻 Development Setup

### Environment Configuration

```bash
# 1️⃣ Create feature branch
git checkout -b feature/your-feature-name

# 2️⃣ Make your changes
# ... edit files ...

# 3️⃣ Test your changes
python src/youtube_automation_gui.py
python src/youtube_automation_cli.py --help

# 4️⃣ Commit your changes
git add .
git commit -m "Add: Description of changes"

# 5️⃣ Push to your fork
git push origin feature/your-feature-name
```

### Testing Checklist

<table>
<tr>
<td width="50%">

**GUI Testing**
- ✅ Window opens correctly
- ✅ All buttons work
- ✅ File selection functions
- ✅ Error handling works
- ✅ Logs display properly

</td>
<td width="50%">

**CLI Testing**
- ✅ Commands execute
- ✅ Arguments parse correctly
- ✅ Output formats properly
- ✅ Error messages clear
- ✅ Help text accurate

</td>
</tr>
</table>

---

## ✍️ Coding Standards

### Python Style Guide

Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) guidelines:

<table>
<tr>
<th>Element</th>
<th>Style</th>
<th>Example</th>
</tr>
<tr>
<td>Functions/Variables</td>
<td><code>snake_case</code></td>
<td><code>process_video_list</code></td>
</tr>
<tr>
<td>Classes</td>
<td><code>PascalCase</code></td>
<td><code>YouTubeAutomation</code></td>
</tr>
<tr>
<td>Constants</td>
<td><code>UPPER_CASE</code></td>
<td><code>MAX_RETRIES</code></td>
</tr>
<tr>
<td>Indentation</td>
<td>4 spaces</td>
<td>(no tabs)</td>
</tr>
<tr>
<td>Line Length</td>
<td>Max 100 chars</td>
<td>-</td>
</tr>
</table>

### Documentation Standards

**All functions must have docstrings:**

```python
def process_video_list(youtube_service, video_ids, delay=4.0):
    """
    Process a list of video IDs with specified delay.
    
    Args:
        youtube_service: Authenticated YouTube API service
        video_ids (list): List of video IDs to process
        delay (float): Delay between operations in seconds
    
    Returns:
        int: Number of successfully processed videos
    
    Raises:
        HttpError: If API request fails
    """
    # Implementation here
```

---

## 📝 Pull Request Process

### Before Submitting

<table>
<tr>
<td>

- ✅ Test all changes thoroughly
- ✅ Update documentation if needed
- ✅ Add comments to complex code
- ✅ Follow coding standards
- ✅ No credentials in code
- ✅ Run code formatting

</td>
</tr>
</table>

### Commit Message Format

<table>
<tr>
<th>Type</th>
<th>Description</th>
<th>Example</th>
</tr>
<tr>
<td>✨ <code>Add:</code></td>
<td>New feature or file</td>
<td><code>Add: Dark mode toggle</code></td>
</tr>
<tr>
<td>🐛 <code>Fix:</code></td>
<td>Bug fix</td>
<td><code>Fix: Window size issue</code></td>
</tr>
<tr>
<td>📝 <code>Docs:</code></td>
<td>Documentation</td>
<td><code>Docs: Update setup guide</code></td>
</tr>
<tr>
<td>♻️ <code>Refactor:</code></td>
<td>Code restructuring</td>
<td><code>Refactor: Optimize loops</code></td>
</tr>
<tr>
<td>💄 <code>Style:</code></td>
<td>Code formatting</td>
<td><code>Style: Format with black</code></td>
</tr>
</table>

### Pull Request Template

When creating a PR, include:

```markdown
## 📝 Description
Brief description of changes

## 🔧 Type of Change
- [ ] 🐛 Bug fix
- [ ] ✨ New feature
- [ ] 📝 Documentation update
- [ ] ♻️ Code refactoring

## 🧪 Testing
How have you tested these changes?

## 📸 Screenshots
Add screenshots for UI changes

## ✅ Checklist
- [ ] Code follows project style
- [ ] Self-reviewed the code
- [ ] Commented complex sections
- [ ] Updated documentation
- [ ] No breaking changes
- [ ] Tested thoroughly
```

---

## 🐛 Reporting Bugs

### Before Reporting

<table>
<tr>
<td>

1. 🔍 Search existing issues
2. 📖 Check troubleshooting guide
3. ✅ Verify latest version
4. 🧪 Test with minimal config

</td>
</tr>
</table>

### Bug Report Structure

**Use this template when reporting bugs:**

```markdown
### 🐛 Bug Description
Clear description of the bug

### 🔄 Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

### ✅ Expected Behavior
What you expected to happen

### ❌ Actual Behavior
What actually happened

### 🖥️ Environment
- OS: Windows 10
- Python: 3.9.5
- Version: 1.0.0

### 📋 Error Logs
```
Paste error logs here
```
```

---

## 💡 Suggesting Features

### Feature Request Guidelines

<table>
<tr>
<td width="50%">

**Good Feature Requests Include:**
- 🎯 Clear problem statement
- 💡 Proposed solution
- 🔄 Alternative approaches
- 📝 Real-world use cases
- 🛠️ Implementation ideas

</td>
<td width="50%">

**Example Structure:**
```markdown
### 💡 Feature
Description

### 🎯 Problem
What it solves

### 📝 Solution
How it works

### 💻 Example
Usage example
```

</td>
</tr>
</table>

---

## 🏗️ Development Guidelines

### Project Structure

```
Youtube-Automation-Suite/
├── 📁 .github/                      # GitHub templates
│   ├── ISSUE_TEMPLATE/
│   └── pull_request_template.md
├── 📁 docs/                        # Documentation
│   ├── API.md
│   ├── BEST_PRACTICES.md
│   ├── SETUP.md
│   └── USER_GUIDE.md
├── 📁 examples/                    # Example files
│   ├── likes.txt
│   ├── comments.txt
│   └── channels.txt
├── 📁 src/                         # Source code
│   ├── youtube_automation_gui.py
│   ├── youtube_automation_cli.py
│   └── __init__.py
├── 📄 Youtube_Automation.py       # CLI launcher
├── 📄 Youtube_Automation_Gui.py   # GUI launcher
├── 📄 START_GUI.bat / start_gui.sh # Launchers
├── 📄 README.md
├── 📄 CHANGELOG.md
├── 📄 CODE_OF_CONDUCT.md
├── 📄 CONTRIBUTING.md
├── 📄 requirements.txt
├── 📄 LICENSE
├── 📄 credentials.json           # User-provided
└── 📄 token.json                 # Auto-generated
```

### Code Review Checklist

Reviewers will check:

<table>
<tr>
<td>

- ✅ Code is clean and readable
- ✅ Follows project conventions
- ✅ No hardcoded credentials
- ✅ Error handling is robust
- ✅ Documentation updated
- ✅ No breaking changes
- ✅ Performance acceptable
- ✅ Security practices followed

</td>
</tr>
</table>

---

## 🎓 Learning Resources

<table>
<tr>
<td align="center" width="25%">
🐍<br><b><a href="https://www.python.org/dev/peps/pep-0008/">PEP 8</a></b><br>Python Style Guide
</td>
<td align="center" width="25%">
📚<br><b><a href="https://docs.github.com">GitHub Docs</a></b><br>Git & GitHub Guide
</td>
<td align="center" width="25%">
🎨<br><b><a href="https://customtkinter.tomschimansky.com/">CustomTkinter</a></b><br>GUI Framework
</td>
<td align="center" width="25%">
🎬<br><b><a href="https://developers.google.com/youtube/v3">YouTube API</a></b><br>API Documentation
</td>
</tr>
</table>

---

## 🏆 Recognition

Contributors will be:

<table>
<tr>
<td align="center" width="33%">
📜<br><b>Listed in Release Notes</b>
</td>
<td align="center" width="33%">
⭐<br><b>Credited in README</b>
</td>
<td align="center" width="33%">
💾<br><b>Forever in Git History</b>
</td>
</tr>
</table>

---

## 📞 Get Help

<table>
<tr>
<td align="center" width="33%">
📖<br><b><a href="docs/">Documentation</a></b><br>Read the guides
</td>
<td align="center" width="33%">
💬<br><b>Community</b><br>Ask questions
</td>
<td align="center" width="33%">
📧<br><b>haseebkaloya@gmail.com</b><br>Email support
</td>
</tr>
</table>

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

<div align="center">

### 🎉 Thank you for contributing! 🎉

**Every contribution, no matter how small, helps improve this project.**

Made with ❤️ by **Haseeb Kaloya** and contributors

[⬆ Back to Top](#-contributing-to-youtube-automation-suite)

</div>

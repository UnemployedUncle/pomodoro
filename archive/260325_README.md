# Pomodoro Timer App

test

A clean, minimalist Flask-based web application that implements the Pomodoro Technique with a unique reward system featuring personalized photos and motivational quotes.

## 🎯 Core Features

### Pomodoro Timer
- **Focus Session**: 25 minutes of focused work (configurable for testing)
- **Short Break**: 5 minutes of rest between sessions
- **Long Break**: 15 minutes after completing 4 focus sessions
- **Session Counter**: Tracks completed focus sessions (1-4)
- **Real-time Updates**: Smooth, live timer updates without page refresh
- **Progress Visualization**: Dual progress bars showing current session and overall cycle progress

### Reward System
- **Photo Rewards**: Users provide keywords for desired photos
- **Quote Rewards**: Users provide keywords for motivational quotes
- **Package Delivery**: Complete 4 focus sessions to receive your personalized package
- **Content Storage**: Photos and quotes saved in separate files for easy access

### Clean UI Design
- **Minimalist Interface**: Clean, distraction-free design
- **Top Navigation**: App name on top-left, icons on top-right (Timer, Rewards, Settings)
- **Progress Bars**: Bottom-positioned progress indicators
- **Responsive Design**: Works on desktop and mobile devices
- **Helvetica Font**: Clean, modern typography

## 🏗️ Architecture

### File Structure
```
pomodoro/
├── app.py                 # Main Flask application
├── config.py             # Configuration settings
├── models/
│   ├── __init__.py
│   ├── timer.py          # Timer logic and session management
│   └── rewards.py        # Photo and quote management
├── static/
│   ├── css/
│   │   └── style.css     # Styling with modern design
│   └── js/
│       └── timer.js      # Frontend timer functionality
├── templates/
│   ├── base.html         # Base template with new header
│   ├── index.html        # Main timer interface
│   ├── setup.html        # Photo/quote preferences setup
│   ├── rewards.html      # Rewards display page
│   ├── 404.html          # Custom error page
│   └── 500.html          # Custom error page
├── data/
│   ├── photos/           # Stored user photos
│   ├── quotes/           # Stored user quotes
│   └── user_data.json    # User preferences and progress
├── requirements.txt      # Python dependencies
├── start.sh             # Quick startup script
└── README.md            # This file
```

### Key Components

#### 1. Timer Module (`models/timer.py`)
- Session state management (focus/break/long break)
- Time tracking and countdown
- Session completion tracking
- Progress calculation for smooth UI updates

#### 2. Rewards Module (`models/rewards.py`)
- Photo keyword processing and storage
- Quote keyword processing and storage
- Package generation after 4 completed sessions
- Content file management

#### 3. Flask Routes (`app.py`)
- `/`: Main timer interface
- `/setup`: User preferences setup
- `/start`: Start timer session
- `/pause`: Pause timer
- `/reset`: Reset timer
- `/rewards`: Display completed package
- `/api/timer-status`: AJAX endpoint for timer updates with progress data

## 🚀 Getting Started

### Prerequisites
- Python 3.7+
- Flask
- Web browser with JavaScript enabled

### Quick Start

1. **Use the startup script (recommended)**
```bash
./start.sh
```

2. **Or install dependencies manually**
```bash
pip3 install -r requirements.txt
```

3. **Run the application**
```bash
python3 app.py
```

4. **Access the application**
   - Open your browser and go to `e  u`
   - Set up your photo and quote preferences
   - Start your first Pomodoro session!

### Current Status
✅ **Application is running successfully!**
- Flask server is active on port 5001
- All routes are functional
- Timer functionality is working with real-time updates
- Setup and rewards pages are accessible
- Modern, clean UI with smooth progress animations
- Responsive design for all devices

## 📋 Usage Flow

### 1. Initial Setup
- Visit the app and click the settings icon (top-right)
- Enter keywords for photos you want to see (e.g., "nature", "mountains", "ocean")
- Enter keywords for motivational quotes (e.g., "success", "perseverance", "growth")
- Save your preferences

### 2. Pomodoro Sessions
- Start a focus session using the Start button
- Watch the timer count down in real-time
- Monitor progress with the bottom progress bars
- Complete the session to earn progress
- Take breaks between sessions
- After 4 sessions, enjoy a long break

### 3. Reward Collection
- Complete all 4 focus sessions
- Click the rewards icon to view your personalized package
- Enjoy photos and quotes matching your keywords

## 🔧 Configuration

### Timer Settings (config.py)
- Focus session duration: 25 seconds (for testing)
- Short break duration: 5 seconds (for testing)
- Long break duration: 15 seconds (for testing)
- Sessions per cycle: 4

**Note**: Testing durations are set for quick verification. Change to 25/5/15 minutes for production use.

### File Storage
- Photos stored in `data/photos/`
- Quotes stored in `data/quotes/`
- User data in `data/user_data.json`

## 🎨 UI Features

### Clean Design
- **Minimalist Header**: App name on left, navigation icons on right
- **Timer Display**: Large, white text with no background box
- **Progress Bars**: Clean, thin lines at bottom of screen
- **Smooth Animations**: Gradual progress updates with CSS transitions
- **Responsive Layout**: Adapts to different screen sizes

### Navigation
- **Timer Icon**: Returns to main timer page
- **Rewards Icon**: Shows completed reward packages
- **Settings Icon**: Opens preferences setup
- **App Name**: Clickable link to return to timer

### Progress Visualization
- **Current Session Bar**: Shows progress within current session
- **Cycle Progress Bar**: Shows progress toward 4-session goal
- **Smooth Updates**: Real-time updates every 200ms
- **Visual Feedback**: Clear indication of session completion

## 🔮 Recent Updates

### UI Improvements
- ✅ Removed lockdown mode for simpler experience
- ✅ Simplified session type text ("Timer", "Break", "Long Break")
- ✅ Removed status messages for cleaner interface
- ✅ Cleaned up navigation with icon-only buttons
- ✅ Improved progress bar animations
- ✅ Enhanced responsive design

### Technical Improvements
- ✅ Real-time timer updates without page refresh
- ✅ Smoother progress bar animations
- ✅ Better error handling
- ✅ Optimized JavaScript performance
- ✅ Cleaner code structure

## 🔮 Future Enhancements

- User accounts and progress persistence
- Statistics and productivity analytics
- Custom timer durations
- Integration with external photo/quote APIs
- Sound notifications
- Export functionality for completed packages
- Dark/light theme toggle

## 📝 License

This project is open source and available under the MIT License.

---

**Built with Flask and Python** | **Focus better, achieve more** 🎯 
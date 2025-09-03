#!/usr/bin/env python3
"""
Demo Initialization Script for Pomodoro Timer
This script demonstrates the timer functionality using the existing app components.
Run this while the Flask app is running to test the timer features.
"""

import time
import requests
import json

class PomodoroDemo:
    """Demo class that uses the running Flask app's API endpoints"""
    
    def __init__(self, base_url="http://127.0.0.1:5001"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def check_app_status(self):
        """Check if the Flask app is running"""
        try:
            response = self.session.get(f"{self.base_url}/api/timer-status")
            if response.status_code == 200:
                print("✅ Flask app is running and accessible")
                return True
            else:
                print(f"❌ App responded with status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to Flask app. Make sure it's running on http://127.0.0.1:5001")
            return False
        except Exception as e:
            print(f"❌ Error checking app status: {e}")
            return False
    
    def get_timer_status(self):
        """Get current timer status"""
        try:
            response = self.session.get(f"{self.base_url}/api/timer-status")
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Failed to get timer status: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error getting timer status: {e}")
            return None
    
    def start_timer(self):
        """Start the timer"""
        try:
            response = self.session.get(f"{self.base_url}/start")
            if response.status_code == 200:
                data = response.json()
                print("🚀 Timer started successfully!")
                print(f"   Current time: {data['remaining_time']}")
                print(f"   Status: {data['session_status']}")
                return data
            else:
                print(f"❌ Failed to start timer: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error starting timer: {e}")
            return None
    
    def pause_timer(self):
        """Pause the timer"""
        try:
            response = self.session.get(f"{self.base_url}/pause")
            if response.status_code == 200:
                data = response.json()
                print("⏸️  Timer paused successfully!")
                print(f"   Current time: {data['remaining_time']}")
                print(f"   Status: {data['session_status']}")
                return data
            else:
                print(f"❌ Failed to pause timer: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error pausing timer: {e}")
            return None
    
    def reset_timer(self):
        """Reset the timer"""
        try:
            response = self.session.get(f"{self.base_url}/reset")
            if response.status_code == 200:
                data = response.json()
                print("🔄 Timer reset successfully!")
                print(f"   Current time: {data['remaining_time']}")
                print(f"   Status: {data['session_status']}")
                return data
            else:
                print(f"❌ Failed to reset timer: {response.status_code}")
                return None
        except Exception as e:
            print(f"❌ Error resetting timer: {e}")
            return None
    
    def monitor_timer(self, duration=30):
        """Monitor timer progress for a specified duration"""
        print(f"\n📊 Monitoring timer for {duration} seconds...")
        print("=" * 50)
        
        start_time = time.time()
        while time.time() - start_time < duration:
            status = self.get_timer_status()
            if status:
                elapsed = time.time() - start_time
                print(f"[{elapsed:5.1f}s] {status['remaining_time']} | "
                      f"State: {status['current_state']} | "
                      f"Status: {status['session_status']} | "
                      f"Progress: {status['completed_sessions']}/{status['total_sessions']}")
                
                # Check if session completed
                if status['is_complete']:
                    print("🎉 Session cycle completed!")
                    break
            
            time.sleep(1)
        
        print("=" * 50)
        print("📊 Monitoring completed")
    
    def run_demo_cycle(self):
        """Run a complete demo cycle"""
        print("\n" + "="*60)
        print("🎬 POMODORO TIMER DEMO CYCLE")
        print("="*60)
        print("This demo will:")
        print("1. Start the timer")
        print("2. Monitor progress for 30 seconds")
        print("3. Pause the timer")
        print("4. Resume the timer")
        print("5. Monitor for another 20 seconds")
        print("6. Reset the timer")
        print("="*60)
        
        # Step 1: Start timer
        print("\n🚀 Step 1: Starting timer...")
        self.start_timer()
        
        # Step 2: Monitor progress
        print("\n📊 Step 2: Monitoring timer progress...")
        self.monitor_timer(30)
        
        # Step 3: Pause timer
        print("\n⏸️  Step 3: Pausing timer...")
        self.pause_timer()
        
        # Step 4: Resume timer
        print("\n▶️  Step 4: Resuming timer...")
        self.start_timer()
        
        # Step 5: Monitor more progress
        print("\n📊 Step 5: Monitoring resumed timer...")
        self.monitor_timer(20)
        
        # Step 6: Reset timer
        print("\n🔄 Step 6: Resetting timer...")
        self.reset_timer()
        
        print("\n🎉 Demo cycle completed!")
        print("💡 You can now use the web interface to continue testing")
    
    def run_interactive_demo(self):
        """Run an interactive demo with user input"""
        print("\n🎮 INTERACTIVE DEMO MODE")
        print("Commands:")
        print("  start  - Start the timer")
        print("  pause  - Pause the timer")
        print("  reset  - Reset the timer")
        print("  status - Show current status")
        print("  monitor - Monitor for 10 seconds")
        print("  quit   - Exit demo")
        print("="*40)
        
        while True:
            try:
                command = input("\n🎮 Enter command: ").lower().strip()
                
                if command == 'start':
                    self.start_timer()
                elif command == 'pause':
                    self.pause_timer()
                elif command == 'reset':
                    self.reset_timer()
                elif command == 'status':
                    status = self.get_timer_status()
                    if status:
                        print(f"⏰ Timer: {status['remaining_time']}")
                        print(f"📊 State: {status['current_state']}")
                        print(f"🔄 Status: {status['session_status']}")
                        print(f"📈 Progress: {status['completed_sessions']}/{status['total_sessions']}")
                elif command == 'monitor':
                    self.monitor_timer(10)
                elif command == 'quit':
                    print("👋 Exiting demo...")
                    break
                else:
                    print("❌ Unknown command. Type 'quit' to exit.")
                    
            except KeyboardInterrupt:
                print("\n👋 Demo interrupted. Exiting...")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main demo function"""
    print("�� Pomodoro Timer Demo Initializer")
    print("Make sure the Flask app is running on http://127.0.0.1:5001")
    
    demo = PomodoroDemo()
    
    # Check if app is running
    if not demo.check_app_status():
        print("\n❌ Cannot proceed without a running Flask app.")
        print("Please start the app with: python3 app.py")
        return
    
    # Show demo options
    print("\n🎬 Choose demo mode:")
    print("1. Automatic demo cycle")
    print("2. Interactive demo")
    print("3. Exit")
    
    try:
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            demo.run_demo_cycle()
        elif choice == '2':
            demo.run_interactive_demo()
        elif choice == '3':
            print("👋 Exiting...")
        else:
            print("❌ Invalid choice. Exiting...")
            
    except KeyboardInterrupt:
        print("\n👋 Demo cancelled.")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")

if __name__ == "__main__":
    main()

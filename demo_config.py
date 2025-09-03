#!/usr/bin/env python3
"""
Demo Configuration - Shows current timer settings
This file displays the current configuration without modifying anything.
"""

from config import Config

def show_demo_settings():
    """Display current demo settings"""
    print("🎯 CURRENT POMODORO TIMER SETTINGS")
    print("=" * 50)
    print(f"Focus Session Duration: {Config.FOCUS_DURATION * 60:.0f} seconds")
    print(f"Short Break Duration: {Config.SHORT_BREAK_DURATION * 60:.0f} seconds")
    print(f"Long Break Duration: {Config.LONG_BREAK_DURATION * 60:.0f} seconds")
    print(f"Sessions per Cycle: {Config.SESSIONS_PER_CYCLE}")
    
    # Calculate total cycle time
    total_focus = Config.FOCUS_DURATION * Config.SESSIONS_PER_CYCLE * 60
    total_short_breaks = Config.SHORT_BREAK_DURATION * (Config.SESSIONS_PER_CYCLE - 1) * 60
    total_long_break = Config.LONG_BREAK_DURATION * 60
    total_cycle = total_focus + total_short_breaks + total_long_break
    
    print(f"\n⏱️  Total Cycle Time: {total_cycle:.0f} seconds ({total_cycle/60:.1f} minutes)")
    print("\n📋 Demo Cycle Breakdown:")
    print(f"   • {Config.SESSIONS_PER_CYCLE} Focus Sessions: {total_focus:.0f}s")
    print(f"   • {Config.SESSIONS_PER_CYCLE - 1} Short Breaks: {total_short_breaks:.0f}s")
    print(f"   • 1 Long Break: {total_long_break:.0f}s")
    
    print("\n💡 These are the current settings in your config.py file.")
    print("   The demo will use these exact settings without modification.")

if __name__ == "__main__":
    show_demo_settings()

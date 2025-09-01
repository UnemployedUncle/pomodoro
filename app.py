from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired
import json
import os

from config import Config
from models.timer import PomodoroTimer
from models.rewards import RewardManager

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Ensure directories exist
Config.ensure_directories()

# Initialize global instances
timer = PomodoroTimer()
reward_manager = RewardManager()

# Forms
class PreferencesForm(FlaskForm):
    photo_keywords = TextAreaField('Photo Keywords (one per line)', 
                                 validators=[DataRequired()],
                                 description='Enter keywords for photos you want to see')
    quote_keywords = TextAreaField('Quote Keywords (one per line)', 
                                 validators=[DataRequired()],
                                 description='Enter keywords for motivational quotes')
    submit = SubmitField('Save Preferences')

@app.route('/')
def index():
    """Main timer interface"""
    timer_status = timer.get_status()
    current_package = reward_manager.get_current_package()
    
    return render_template('index.html', 
                         timer_status=timer_status,
                         current_package=current_package)

@app.route('/setup')
def setup():
    """User preferences setup page"""
    form = PreferencesForm()
    
    # Pre-populate form with existing data
    if reward_manager.user_data['photo_keywords']:
        form.photo_keywords.data = '\n'.join(reward_manager.user_data['photo_keywords'])
    if reward_manager.user_data['quote_keywords']:
        form.quote_keywords.data = '\n'.join(reward_manager.user_data['quote_keywords'])
    
    return render_template('setup.html', form=form)

@app.route('/setup', methods=['POST'])
def save_preferences():
    """Save user preferences"""
    form = PreferencesForm()
    
    if form.validate_on_submit():
        # Parse keywords from textarea (one per line)
        photo_keywords = [kw.strip() for kw in form.photo_keywords.data.split('\n') if kw.strip()]
        quote_keywords = [kw.strip() for kw in form.quote_keywords.data.split('\n') if kw.strip()]
        
        # Update preferences
        reward_manager.update_preferences(photo_keywords, quote_keywords)
        
        flash('Preferences saved successfully!', 'success')
        return redirect(url_for('index'))
    
    return render_template('setup.html', form=form)

@app.route('/start')
def start_timer():
    """Start the Pomodoro timer"""
    timer.start()
    return jsonify(timer.get_status())

@app.route('/pause')
def pause_timer():
    """Pause the Pomodoro timer"""
    timer.pause()
    return jsonify(timer.get_status())

@app.route('/reset')
def reset_timer():
    """Reset the Pomodoro timer"""
    timer.reset()
    return jsonify(timer.get_status())

@app.route('/api/timer-status')
def timer_status():
    """API endpoint for timer status updates"""
    status = timer.get_status()
    
    # Add session progress to the response
    status['session_progress'] = timer.get_session_progress()
    
    # Check if cycle is complete and generate package
    if status['is_complete'] and not reward_manager.get_current_package().get('completed_at'):
        package = reward_manager.generate_package()
        status['package_ready'] = True
    else:
        status['package_ready'] = False
    
    return jsonify(status)

@app.route('/rewards')
def rewards():
    """Display rewards page"""
    current_package = reward_manager.get_current_package()
    completed_packages = reward_manager.get_completed_packages()
    
    return render_template('rewards.html', 
                         current_package=current_package,
                         completed_packages=completed_packages)

@app.route('/collect-rewards')
def collect_rewards():
    """Collect current rewards and clear package"""
    reward_manager.clear_current_package()
    timer.reset()  # Reset timer for new cycle
    flash('Rewards collected! Start a new Pomodoro cycle.', 'success')
    return redirect(url_for('index'))

@app.route('/api/session-progress')
def session_progress():
    """Get session progress data"""
    return jsonify({
        'session_progress': timer.get_session_progress(),
        'cycle_progress': timer.get_cycle_progress()
    })

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=Config.DEBUG, host='0.0.0.0', port=5001) 
import json
import os
import requests
from datetime import datetime
from config import Config

class RewardManager:
    """Manages photo and quote rewards for completed Pomodoro sessions"""
    
    def __init__(self):
        self.user_data_file = Config.USER_DATA_FILE
        self.photos_dir = Config.PHOTOS_DIR
        self.quotes_dir = Config.QUOTES_DIR
        self.load_user_data()
    
    def load_user_data(self):
        """Load user preferences and data"""
        if os.path.exists(self.user_data_file):
            try:
                with open(self.user_data_file, 'r') as f:
                    self.user_data = json.load(f)
            except json.JSONDecodeError:
                self.user_data = self.get_default_user_data()
        else:
            self.user_data = self.get_default_user_data()
            self.save_user_data()
    
    def get_default_user_data(self):
        """Get default user data structure"""
        return {
            'photo_keywords': [],
            'quote_keywords': [],
            'completed_packages': [],
            'current_package': {
                'photos': [],
                'quotes': [],
                'completed_at': None
            }
        }
    
    def save_user_data(self):
        """Save user data to file"""
        os.makedirs(os.path.dirname(self.user_data_file), exist_ok=True)
        with open(self.user_data_file, 'w') as f:
            json.dump(self.user_data, f, indent=2)
    
    def update_preferences(self, photo_keywords, quote_keywords):
        """Update user preferences for photos and quotes"""
        self.user_data['photo_keywords'] = photo_keywords
        self.user_data['quote_keywords'] = quote_keywords
        self.save_user_data()
    
    def get_photo(self, keyword):
        """Get a photo based on keyword using Unsplash API"""
        try:
            # Using Unsplash API for free photos
            url = "https://api.unsplash.com/photos/random"
            params = {
                'query': keyword,
                'client_id': 'your-unsplash-access-key'  # Replace with actual key
            }
            
            # For demo purposes, return a placeholder
            # In production, you would use the actual API
            return {
                'url': f"https://source.unsplash.com/800x600/?{keyword}",
                'alt': f"Photo related to {keyword}",
                'keyword': keyword,
                'filename': f"{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            }
        except Exception as e:
            # Fallback to placeholder
            return {
                'url': f"https://via.placeholder.com/800x600/4CAF50/FFFFFF?text={keyword}",
                'alt': f"Placeholder for {keyword}",
                'keyword': keyword,
                'filename': f"{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            }
    
    def get_quote(self, keyword):
        """Get a motivational quote based on keyword"""
        # Sample quotes for demo purposes
        # In production, you could use a quotes API
        quotes_database = {
            'success': [
                "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
                "The only way to do great work is to love what you do. - Steve Jobs",
                "Success usually comes to those who are too busy to be looking for it. - Henry David Thoreau"
            ],
            'perseverance': [
                "Perseverance is not a long race; it is many short races one after the other. - Walter Elliot",
                "The difference between the impossible and the possible lies in determination. - Tommy Lasorda",
                "It always seems impossible until it's done. - Nelson Mandela"
            ],
            'growth': [
                "Growth is the only evidence of life. - John Henry Newman",
                "The only person you are destined to become is the person you decide to be. - Ralph Waldo Emerson",
                "Change is the end result of all true learning. - Leo Buscaglia"
            ],
            'focus': [
                "Concentrate all your thoughts upon the work at hand. The sun's rays do not burn until brought to a focus. - Alexander Graham Bell",
                "The successful warrior is the average man, with laser-like focus. - Bruce Lee",
                "Focus is a matter of deciding what things you're not going to do. - John Carmack"
            ],
            'motivation': [
                "Motivation is what gets you started. Habit is what keeps you going. - Jim Ryun",
                "The only limit to our realization of tomorrow is our doubts of today. - Franklin D. Roosevelt",
                "Believe you can and you're halfway there. - Theodore Roosevelt"
            ]
        }
        
        # Get quotes for the keyword or use default
        available_quotes = quotes_database.get(keyword.lower(), quotes_database['motivation'])
        
        # Return a random quote (for demo, return first one)
        return {
            'text': available_quotes[0],
            'keyword': keyword,
            'filename': f"{keyword}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        }
    
    def generate_package(self):
        """Generate a new reward package with photos and quotes"""
        package = {
            'photos': [],
            'quotes': [],
            'completed_at': datetime.now().isoformat()
        }
        
        # Generate photos for each keyword
        for keyword in self.user_data['photo_keywords']:
            photo = self.get_photo(keyword)
            package['photos'].append(photo)
        
        # Generate quotes for each keyword
        for keyword in self.user_data['quote_keywords']:
            quote = self.get_quote(keyword)
            package['quotes'].append(quote)
        
        # Save package to user data
        self.user_data['current_package'] = package
        self.user_data['completed_packages'].append(package)
        self.save_user_data()
        
        return package
    
    def get_current_package(self):
        """Get the current reward package"""
        return self.user_data.get('current_package', {})
    
    def get_completed_packages(self):
        """Get all completed packages"""
        return self.user_data.get('completed_packages', [])
    
    def clear_current_package(self):
        """Clear the current package (after user collects it)"""
        self.user_data['current_package'] = {
            'photos': [],
            'quotes': [],
            'completed_at': None
        }
        self.save_user_data()
    
    def save_photo_locally(self, photo_data):
        """Save photo to local storage"""
        try:
            response = requests.get(photo_data['url'])
            if response.status_code == 200:
                filepath = os.path.join(self.photos_dir, photo_data['filename'])
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                return filepath
        except Exception as e:
            print(f"Error saving photo: {e}")
        return None
    
    def save_quote_locally(self, quote_data):
        """Save quote to local storage"""
        try:
            filepath = os.path.join(self.quotes_dir, quote_data['filename'])
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(quote_data['text'])
            return filepath
        except Exception as e:
            print(f"Error saving quote: {e}")
        return None 
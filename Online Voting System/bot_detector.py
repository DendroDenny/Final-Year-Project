import re
from sklearn.ensemble import RandomForestClassifier

class EmailBotDetector:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=50, random_state=42)
        self._train_model()
    
    def _extract_email_features(self, email):
        """Extract features from email to detect bots"""
        features = []
        
        # Length features
        features.append(len(email))
        features.append(len(email.split('@')[0]))  # username length
        
        # Pattern features
        features.append(len(re.findall(r'\d', email)))  # digit count
        features.append(len(re.findall(r'[a-z]', email)))  # lowercase count
        features.append(len(re.findall(r'[A-Z]', email)))  # uppercase count
        features.append(email.count('.'))
        features.append(email.count('_'))
        features.append(email.count('-'))
        
        # Suspicious patterns
        features.append(1 if re.search(r'\d{4,}', email) else 0)  # 4+ consecutive digits
        features.append(1 if email.split('@')[0].isdigit() else 0)  # all digits username
        features.append(1 if len(set(email.split('@')[0])) < 3 else 0)  # repeated chars
        
        return features
    
    def _train_model(self):
        """Train with common bot/human email patterns"""
        # Bot-like emails (labeled as 1)
        bot_emails = [
            'user123456@gmail.com', 'test999@yahoo.com', 'bot12345@hotmail.com',
            'aaaaaa@gmail.com', '111111@test.com', 'user_bot_123@email.com',
            'automated123@temp.com', '999test@fake.com', 'botuser999@mail.com'
        ]
        
        # Human-like emails (labeled as 0)
        human_emails = [
            'john.doe@gmail.com', 'sarah.smith@yahoo.com', 'mike.johnson@hotmail.com',
            'alice.brown@email.com', 'david.wilson@company.com', 'lisa.garcia@uni.edu',
            'robert.miller@work.org', 'emma.davis@personal.net', 'james.taylor@home.com'
        ]
        
        # Prepare training data
        X = []
        y = []
        
        for email in bot_emails:
            X.append(self._extract_email_features(email))
            y.append(1)  # Bot
            
        for email in human_emails:
            X.append(self._extract_email_features(email))
            y.append(0)  # Human
        
        self.model.fit(X, y)
    
    def is_bot_email(self, email):
        """Predict if email belongs to a bot"""
        features = self._extract_email_features(email)
        prediction = self.model.predict([features])[0]
        confidence = self.model.predict_proba([features])[0].max()
        
        return prediction == 1, confidence

def check_bot_email(email):
    """Check if email is from a bot"""
    detector = EmailBotDetector()
    is_bot, confidence = detector.is_bot_email(email)
    return is_bot, confidence
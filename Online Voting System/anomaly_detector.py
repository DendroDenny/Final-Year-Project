import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from datetime import datetime, timedelta
import sqlite3

class VotingAnomalyDetector:
    def __init__(self, db_path="instance/database.db"):
        self.db_path = db_path
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
    
    def extract_features(self):
        """Extract features from voting data"""
        conn = sqlite3.connect(self.db_path)
        
        # Get voting patterns with user info
        query = """
        SELECT v.id, v.user_id, v.voted_candidate,
               u.email, u.first_name,
               datetime('now') as vote_time
        FROM vote v
        JOIN user u ON v.user_id = u.id
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        if df.empty:
            return None
            
        # Feature engineering
        df['vote_time'] = pd.to_datetime(df['vote_time'])
        df['hour'] = df['vote_time'].dt.hour
        df['day_of_week'] = df['vote_time'].dt.dayofweek
        
        # Aggregate features per user
        user_features = df.groupby('user_id').agg({
            'id': 'count',  # vote_count
            'hour': 'mean',  # avg_voting_hour
            'day_of_week': 'mean'  # avg_voting_day
        }).rename(columns={'id': 'vote_count'})
        
        return user_features
    
    def detect_anomalies(self):
        """Detect anomalous voting patterns"""
        features = self.extract_features()
        if features is None or len(features) < 2:
            return []
            
        # Scale features
        scaled_features = self.scaler.fit_transform(features)
        
        # Detect anomalies
        anomalies = self.model.fit_predict(scaled_features)
        
        # Return anomalous user IDs
        anomalous_users = features[anomalies == -1].index.tolist()
        return anomalous_users

def check_voting_anomalies():
    """Quick function to check for anomalies"""
    detector = VotingAnomalyDetector()
    anomalous_users = detector.detect_anomalies()
    
    if anomalous_users:
        print(f"⚠️  Detected {len(anomalous_users)} anomalous voting patterns")
        print(f"Suspicious user IDs: {anomalous_users}")
        return anomalous_users
    else:
        print("✅ No anomalies detected")
        return []
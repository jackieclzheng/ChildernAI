import os
import sys
import sqlite3
from datetime import datetime

class DatabaseManager:
    """Database management class, responsible for all database operations"""
    
    def __init__(self, database_path="data/children_companion.db"):
        """Initialize database connection"""
        self.database_path = database_path
        self.ensure_directory_exists()
        self.connection = None
        self.cursor = None
        
    def ensure_directory_exists(self):
        """Ensure database directory exists"""
        directory = os.path.dirname(self.database_path)
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def connect_database(self):
        """Connect to SQLite database"""
        try:
            self.connection = sqlite3.connect(self.database_path)
            self.connection.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
            self.cursor = self.connection.cursor()
            return True
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
    
    def initialize_database(self):
        """Create all necessary tables"""
        if not self.connect_database():
            return False
        
        try:
            # Create users table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                user_type TEXT NOT NULL,  -- 'child' or 'parent'
                creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create children information table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS children_info (
                child_id INTEGER PRIMARY KEY,
                parent_id INTEGER NOT NULL,
                name TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                interests TEXT,
                FOREIGN KEY (child_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (parent_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            ''')
            
            # Create content resources table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS content_resources (
                resource_id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                type TEXT NOT NULL,  -- 'story', 'song', 'game', 'learning'
                subtype TEXT,  -- like 'fairy tale', 'fable' etc.
                description TEXT,
                content_path TEXT NOT NULL,
                thumbnail_path TEXT,
                age_range TEXT,  -- like '2-4 years', '5-7 years' etc.
                tags TEXT,
                creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # Create usage records table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usage_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                resource_id INTEGER,
                activity_type TEXT NOT NULL,  -- 'browse', 'play', 'learn', 'game' etc.
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                duration INTEGER,  -- unit: seconds
                completion_status TEXT,  -- 'completed', 'interrupted', 'abandoned' etc.
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (resource_id) REFERENCES content_resources(resource_id) ON DELETE SET NULL
            )
            ''')
            
            # Create learning progress table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS learning_progress (
                progress_id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                subject TEXT NOT NULL,  -- 'literacy', 'arithmetic', 'english' etc.
                topic TEXT NOT NULL,
                level INTEGER NOT NULL,
                completion_rate REAL DEFAULT 0,  -- 0-100 percentage
                last_learning_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES children_info(child_id) ON DELETE CASCADE
            )
            ''')
            
            # Create habit formation table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habit_formation (
                habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
                child_id INTEGER NOT NULL,
                habit_name TEXT NOT NULL,
                description TEXT,
                frequency TEXT NOT NULL,  -- 'daily', 'weekly' etc.
                reminder_time TEXT,
                creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (child_id) REFERENCES children_info(child_id) ON DELETE CASCADE
            )
            ''')
            
            # Create habit completion records table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habit_completion_records (
                record_id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                completion_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completion_status TEXT NOT NULL,  -- 'completed', 'partially completed', 'not completed'
                notes TEXT,
                FOREIGN KEY (habit_id) REFERENCES habit_formation(habit_id) ON DELETE CASCADE
            )
            ''')
            
            # Create parental control settings table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS parental_control_settings (
                setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                parent_id INTEGER NOT NULL,
                child_id INTEGER NOT NULL,
                daily_time_limit INTEGER,  -- unit: minutes
                disabled_periods TEXT,  -- JSON format storing multiple time periods
                content_filter_level TEXT,  -- 'low', 'medium', 'high'
                allowed_content_types TEXT,  -- JSON format storing allowed content types
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (parent_id) REFERENCES users(user_id) ON DELETE CASCADE,
                FOREIGN KEY (child_id) REFERENCES children_info(child_id) ON DELETE CASCADE
            )
            ''')
            
            # Create system settings table
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_settings (
                setting_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                setting_type TEXT NOT NULL,  -- 'interface', 'sound', 'notification' etc.
                setting_name TEXT NOT NULL,
                setting_value TEXT NOT NULL,
                update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
            )
            ''')
            
            self.connection.commit()
            print("Database initialized successfully")
            return True
            
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
            self.connection.rollback()
            return False
        finally:
            self.close_connection()
    
    def add_user(self, username, password, user_type):
        """Add new user"""
        if not self.connect_database():
            return False
        
        try:
            self.cursor.execute(
                "INSERT INTO users (username, password, user_type) VALUES (?, ?, ?)",
                (username, password, user_type)
            )
            self.connection.commit()
            user_id = self.cursor.lastrowid
            print(f"User added successfully, ID: {user_id}")
            return user_id
        except sqlite3.Error as e:
            print(f"Add user error: {e}")
            self.connection.rollback()
            return False
        finally:
            self.close_connection()
    
    def add_child_info(self, child_id, parent_id, name, age=None, gender=None, interests=None):
        """Add child information"""
        if not self.connect_database():
            return False
        
        try:
            self.cursor.execute(
                "INSERT INTO children_info (child_id, parent_id, name, age, gender, interests) VALUES (?, ?, ?, ?, ?, ?)",
                (child_id, parent_id, name, age, gender, interests)
            )
            self.connection.commit()
            print(f"Child information added successfully, ID: {child_id}")
            return True
        except sqlite3.Error as e:
            print(f"Add child information error: {e}")
            self.connection.rollback()
            return False
        finally:
            self.close_connection()
    
    def add_content_resource(self, title, type, content_path, subtype=None, description=None, thumbnail_path=None, age_range=None, tags=None):
        """Add content resource"""
        if not self.connect_database():
            return False
        
        try:
            self.cursor.execute(
                "INSERT INTO content_resources (title, type, subtype, description, content_path, thumbnail_path, age_range, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (title, type, subtype, description, content_path, thumbnail_path, age_range, tags)
            )
            self.connection.commit()
            resource_id = self.cursor.lastrowid
            print(f"Content resource added successfully, ID: {resource_id}")
            return resource_id
        except sqlite3.Error as e:
            print(f"Add content resource error: {e}")
            self.connection.rollback()
            return False
        finally:
            self.close_connection()
    
    def add_usage_record(self, user_id, resource_id, activity_type):
        """Add usage record (at start)"""
        if not self.connect_database():
            return False
        
        try:
            self.cursor.execute(
                "INSERT INTO usage_records (user_id, resource_id, activity_type) VALUES (?, ?, ?)",
                (user_id, resource_id, activity_type)
            )
            self.connection.commit()
            record_id = self.cursor.lastrowid
            print(f"Usage record added successfully, ID: {record_id}")
            return record_id
        except sqlite3.Error as e:
            print(f"Add usage record error: {e}")
            self.connection.rollback()
            return False
        finally:
            self.close_connection()
    
    def update_usage_record(self, record_id, end_time=None, completion_status=None):
        """Update usage record (at end)"""
        if not self.connect_database():
            return False
        
        try:
            # If end time is not provided, use current time
            if end_time is None:
                end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Get start time
            self.cursor.execute("SELECT start_time FROM usage_records WHERE record_id = ?", (record_id,))
            result = self.cursor.fetchone()
            if not result:
                print(f"Record ID not found: {record_id}")
                return False
            
            start_time = datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S')
            end_time_obj = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')
            duration = int((end_time_obj - start_time).total_seconds())
            
            self.cursor.execute(
                "UPDATE usage_records SET end_time = ?, duration = ?, completion_status = ? WHERE record_id = ?",
                (end_time, duration, completion_status, record_id)
            )
            self.connection.commit()
            print(f"Usage record updated successfully, ID: {record_id}")
            return True
        except sqlite3.Error as e:
            print(f"Update usage record error: {e}")
            self.connection.rollback()
            return False
        except ValueError as e:
            print(f"Date format error: {e}")
            return False
        finally:
            self.close_connection()
    
    def add_learning_progress(self, child_id, subject, topic, level, completion_rate=0):
        """Add or update learning progress"""
        if not self.connect_database():
            return False
        
        try:
            # Check if progress record already exists
            self.cursor.execute(
                "SELECT progress_id, completion_rate FROM learning_progress WHERE child_id = ? AND subject = ? AND topic = ? AND level = ?",
                (child_id, subject, topic, level)
            )
            
            result = self.cursor.fetchone()
            
            if result:
                # If exists, update only if new completion rate is higher
                progress_id, current_completion_rate = result
                if completion_rate > current_completion_rate:
                    self.cursor.execute(
                        "UPDATE learning_progress SET completion_rate = ?, last_learning_time = CURRENT_TIMESTAMP WHERE progress_id = ?",
                        (completion_rate, progress_id)
                    )
                    self.connection.commit()
                    print(f"Learning progress updated successfully, ID: {progress_id}")
                else:
                    print(f"Learning progress not updated, current rate is higher: {current_completion_rate} > {completion_rate}")
                return progress_id
            else:
                # If not exists, add new record
                self.cursor.execute(
                    "INSERT INTO learning_progress (child_id, subject, topic, level, completion_rate) VALUES (?, ?, ?, ?, ?)",
                    (child_id, subject, topic, level, completion_rate)
                )
                self.connection.commit()
                progress_id = self.cursor.lastrowid
                print(f"Learning progress added successfully, ID: {progress_id}")
                return progress_id
        except sqlite3.Error as e:
            print(f"Add learning progress error: {e}")
            self.connection.rollback()
            return False
        finally:
            self.close_connection()
    
    def add_habit(self, child_id, habit_name, frequency, description=None, reminder_time=None):
        """Add habit formation task"""
        if not self.connect_database():
            return False
        
        try:
            self.cursor.execute(
                "INSERT INTO habit_formation (child_id, habit_name, description, frequency, reminder_time) VALUES (?, ?, ?, ?, ?)",
                (child_id, habit_name, description, frequency, reminder_time)
            )
            self.connection.commit()
            habit_id = self.cursor.lastrowid
            print(f"Habit added successfully, ID: {habit_id}")
            return habit_id
        except sqlite3.Error as e:
            print(f"Add habit error: {e}")
            self.connection.rollback()
            return False
        finally:
            self.close_connection()
    
    def record_habit_completion(self, habit_id, completion_status, notes=None):
        """Record habit completion"""
        if not self.connect_database():
            return False
        
        try:
            self.cursor.execute(
                "INSERT INTO habit_completion_records (habit_id, completion_status, notes) VALUES (?, ?, ?)",
                (habit_id, completion_status, notes)
            )
            self.connection.commit()
            record_id = self.cursor.lastrowid
            print(f"Habit completion recorded successfully, ID: {record_id}")
            return record_id
        except sqlite3.Error as e:
            print(f"Record habit completion error: {e}")
            self.connection.rollback()
            return False
        finally:
            self.close_connection()
    
    def set_parental_control(self, parent_id, child_id, daily_time_limit=None, disabled_periods=None, content_filter_level=None, allowed_content_types=None):
        """Set parental control settings"""
        if not self.connect_database():
            return False
        
        try:
            # Check if settings already exist
            self.cursor.execute(
                "SELECT setting_id FROM parental_control_settings WHERE parent_id = ? AND child_id = ?",
                (parent_id, child_id)
            )
            
            result = self.cursor.fetchone()
            
            if result:
                # If exists, update
                setting_id = result[0]
                self.cursor.execute(
                    """UPDATE parental_control_settings SET 
                    daily_time_limit = COALESCE(?, daily_time_limit),
                    disabled_periods = COALESCE(?, disabled_periods),
                    content_filter_level = COALESCE(?, content_filter_level),
                    allowed_content_types = COALESCE(?, allowed_content_types),
                    update_time = CURRENT_TIMESTAMP
                    WHERE setting_id = ?""",
                    (daily_time_limit, disabled_periods, content_filter_level, allowed_content_types, setting_id)
                )
                self.connection.commit()
                print(f"Parental control settings updated successfully, ID: {setting_id}")
                return setting_id
            else:
                # If not exists, add new record
                self.cursor.execute(
                    """INSERT INTO parental_control_settings 
                    (parent_id, child_id, daily_time_limit, disabled_periods, content_filter_level, allowed_content_types) 
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (parent_id, child_id, daily_time_limit, disabled_periods, content_filter_level, allowed_content_types)
                )
                self.connection.commit()
                setting_id = self.cursor.lastrowid
                print(f"Parental control settings added successfully, ID: {setting_id}")
                return setting_id
        except sqlite3.Error as e:
            print(f"Set parental control error: {e}")
            self.connection.rollback()
            return False
        finally:
            self.close_connection()
    
    def get_user_info(self, username=None, user_id=None):
        """Get user information"""
        if not self.connect_database():
            return None
        
        try:
            if username:
                self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            elif user_id:
                self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            else:
                print("Must provide username or user_id")
                return None
            
            result = self.cursor.fetchone()
            if result:
                column_names = [description[0] for description in self.cursor.description]
                return dict(zip(column_names, result))
            else:
                return None
        except sqlite3.Error as e:
            print(f"Get user information error: {e}")
            return None
        finally:
            self.close_connection()
    
    def get_child_info(self, child_id):
        """Get child detailed information"""
        if not self.connect_database():
            return None
        
        try:
            self.cursor.execute("""
            SELECT c.*, u.username 
            FROM children_info c
            JOIN users u ON c.child_id = u.user_id
            WHERE c.child_id = ?
            """, (child_id,))
            
            result = self.cursor.fetchone()
            if result:
                column_names = [description[0] for description in self.cursor.description]
                return dict(zip(column_names, result))
            else:
                return None
        except sqlite3.Error as e:
            print(f"Get child information error: {e}")
            return None
        finally:
            self.close_connection()
    
    def get_parent_children_list(self, parent_id):
        """Get all children information associated with parent"""
        if not self.connect_database():
            return []
        
        try:
            self.cursor.execute("""
            SELECT c.*, u.username 
            FROM children_info c
            JOIN users u ON c.child_id = u.user_id
            WHERE c.parent_id = ?
            """, (parent_id,))
            
            results = self.cursor.fetchall()
            if results:
                column_names = [description[0] for description in self.cursor.description]
                return [dict(zip(column_names, row)) for row in results]
            else:
                return []
        except sqlite3.Error as e:
            print(f"Get parent's children list error: {e}")
            return []
        finally:
            self.close_connection()
    
    def get_content_resources(self, type=None, subtype=None, age_range=None, tags=None, limit=10):
        """Get content resources list, can be filtered by conditions"""
        if not self.connect_database():
            return []
        
        try:
            query = "SELECT * FROM content_resources WHERE 1=1"
            params = []
            
            if type:
                query += " AND type = ?"
                params.append(type)
            
            if subtype:
                query += " AND subtype = ?"
                params.append(subtype)
            
            if age_range:
                query += " AND age_range = ?"
                params.append(age_range)
            
            if tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tags}%")
            
            query += " ORDER BY creation_time DESC LIMIT ?"
            params.append(limit)
            
            self.cursor.execute(query, params)
            
            results = self.cursor.fetchall()
            if results:
                column_names = [description[0] for description in self.cursor.description]
                return [dict(zip(column_names, row)) for row in results]
            else:
                return []
        except sqlite3.Error as e:
            print(f"Get content resources error: {e}")
            return []
        finally:
            self.close_connection()
    
    def get_usage_statistics(self, user_id, start_date=None, end_date=None):
        """Get user usage statistics"""
        if not self.connect_database():
            return {}
        
        try:
            # If date range not provided, default to last 30 days
            if not start_date:
                start_date = (datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
            if not end_date:
                end_date = datetime.now().strftime('%Y-%m-%d')
            
            # Total usage duration
            self.cursor.execute("""
            SELECT SUM(duration) 
            FROM usage_records 
            WHERE user_id = ? AND start_time BETWEEN ? AND ?
            """, (user_id, start_date, end_date + ' 23:59:59'))
            
            total_duration = self.cursor.fetchone()[0] or 0
            
            # Statistics by activity type
            self.cursor.execute("""
            SELECT activity_type, SUM(duration) as duration
            FROM usage_records 
            WHERE user_id = ? AND start_time BETWEEN ? AND ?
            GROUP BY activity_type
            """, (user_id, start_date, end_date + ' 23:59:59'))
            
            activity_statistics = {}
            for row in self.cursor.fetchall():
                activity_statistics[row[0]] = row[1]
            
            # Statistics by date
            self.cursor.execute("""
            SELECT date(start_time) as date, SUM(duration) as duration
            FROM usage_records 
            WHERE user_id = ? AND start_time BETWEEN ? AND ?
            GROUP BY date(start_time)
            ORDER BY date
            """, (user_id, start_date, end_date + ' 23:59:59'))
            
            date_statistics = {}
            for row in self.cursor.fetchall():
                date_statistics[row[0]] = row[1]
            
            # Most frequently used content
            self.cursor.execute("""
            SELECT r.resource_id, c.title, c.type, SUM(r.duration) as duration
            FROM usage_records r
            JOIN content_resources c ON r.resource_id = c.resource_id
            WHERE r.user_id = ? AND r.start_time BETWEEN ? AND ?
            GROUP BY r.resource_id
            ORDER BY duration DESC
            LIMIT 5
            """, (user_id, start_date, end_date + ' 23:59:59'))
            
            frequent_content = []
            for row in self.cursor.fetchall():
                frequent_content.append({
                    'resource_id': row[0],
                    'title': row[1],
                    'type': row[2],
                    'usage_duration': row[3]
                })
            
            return {
                'total_usage_duration': total_duration,
                'activity_statistics': activity_statistics,
                'date_statistics': date_statistics,
                'frequent_content': frequent_content
            }
        except sqlite3.Error as e:
            print(f"Get usage statistics error: {e}")
            return {}
        finally:
            self.close_connection()
    
    def get_learning_progress(self, child_id, subject=None):
        """Get child learning progress"""
        if not self.connect_database():
            return []
        
        try:
            query = "SELECT * FROM learning_progress WHERE child_id = ?"
            params = [child_id]
            
            if subject:
                query += " AND subject = ?"
                params.append(subject)
            
            query += " ORDER BY subject, level"
            
            self.cursor.execute(query, params)
            
            results = self.cursor.fetchall()
            if results:
                column_names = [description[0] for description in self.cursor.description]
                return [dict(zip(column_names, row)) for row in results]
            else:
                return []
        except sqlite3.Error as e:
            print(f"Get learning progress error: {e}")
            return []
        finally:
            self.close_connection()
    
    def get_habit_list(self, child_id):
        """Get child's habit formation list"""
        if not self.connect_database():
            return []
        
        try:
            self.cursor.execute("""
            SELECT h.*, 
                  (SELECT COUNT(*) FROM habit_completion_records WHERE habit_id = h.habit_id AND completion_status = 'completed') as completion_count,
                  (SELECT completion_time FROM habit_completion_records WHERE habit_id = h.habit_id ORDER BY completion_time DESC LIMIT 1) as last_completion_time
            FROM habit_formation h
            WHERE h.child_id = ?
            ORDER BY h.habit_name
            """, (child_id,))
            
            results = self.cursor.fetchall()
            if results:
                column_names = [description[0] for description in self.cursor.description]
                return [dict(zip(column_names, row)) for row in results]
            else:
                return []
        except sqlite3.Error as e:
            print(f"Get habit list error: {e}")
            return []
        finally:
            self.close_connection()
    
    def get_parental_control_settings(self, parent_id, child_id):
        """Get parental control settings"""
        if not self.connect_database():
            return None
        
        try:
            self.cursor.execute("""
            SELECT * FROM parental_control_settings
            WHERE parent_id = ? AND child_id = ?
            """, (parent_id, child_id))
            
            result = self.cursor.fetchone()
            if result:
                column_names = [description[0] for description in self.cursor.description]
                return dict(zip(column_names, result))
            else:
                return None
        except sqlite3.Error as e:
            print(f"Get parental control settings error: {e}")
            return None
        finally:
            self.close_connection()
    
    def authenticate_user(self, username, password):
        """Authenticate user login"""
        if not self.connect_database():
            return None
        
        try:
            self.cursor.execute("""
            SELECT user_id, user_type FROM users
            WHERE username = ? AND password = ?
            """, (username, password))
            
            result = self.cursor.fetchone()
            if result:
                return {
                    'user_id': result[0],
                    'user_type': result[1]
                }
            else:
                return None
        except sqlite3.Error as e:
            print(f"Authenticate user error: {e}")
            return None
        finally:
            self.close_connection()
    
    def search_content(self, keyword, type=None, limit=20):
        """Search content resources"""
        if not self.connect_database():
            return []
        
        try:
            query = """
            SELECT * FROM content_resources
            WHERE (title LIKE ? OR description LIKE ? OR tags LIKE ?)
            """
            params = [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]
            
            if type:
                query += " AND type = ?"
                params.append(type)
            
            query += " ORDER BY creation_time DESC LIMIT ?"
            params.append(limit)
            
            self.cursor.execute(query, params)
            
            results = self.cursor.fetchall()
            if results:
                column_names = [description[0] for description in self.cursor.description]
                return [dict(zip(column_names, row)) for row in results]
            else:
                return []
        except sqlite3.Error as e:
            print(f"Search content error: {e}")
            return []
        finally:
            self.close_connection()
    
    def backup_database(self, backup_path=None):
        """Backup database to specified path"""
        if not backup_path:
            backup_path = f"backup/children_companion_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        
        # Ensure backup directory exists
        backup_dir = os.path.dirname(backup_path)
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        if not self.connect_database():
            return False
        
        try:
            # Create backup database connection
            backup_connection = sqlite3.connect(backup_path)
            
            # Copy current database content to backup database
            with backup_connection:
                self.connection.backup(backup_connection)
            
            backup_connection.close()
            print(f"Database has been backed up to: {backup_path}")
            return True
        except sqlite3.Error as e:
            print(f"Backup database error: {e}")
            return False
        finally:
            self.close_connection()


# Test code
if __name__ == "__main__":
    # Create database manager instance
    db = DatabaseManager("test_database.db")
    
    # Initialize database
    db.initialize_database()
    
    # Add test users
    parent_id = db.add_user("parent", "password123", "parent")
    child_id = db.add_user("child", "password123", "child")
    
    # Add child information
    db.add_child_info(child_id, parent_id, "Xiaoming", 6, "male", "drawing,dinosaurs")
    
    # Add content resource
    story_id = db.add_content_resource("Little Red Riding Hood", "story", "content/stories/little_red_riding_hood.json", "fairy tale", "Classic fairy tale", "images/little_red_riding_hood.jpg", "4-8 years", "fairy tale,classic,forest")
    
    # Add usage record
    record_id = db.add_usage_record(child_id, story_id, "play")
    
    # Update usage record
    db.update_usage_record(record_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "completed")
    
    # Add learning progress
    db.add_learning_progress(child_id, "literacy", "basic characters", 1, 80)
    
    # Add habit
    habit_id = db.add_habit(child_id, "brush teeth", "daily", "morning and evening", "07:30,19:30")
    
    # Record habit completion
    db.record_habit_completion(habit_id, "completed", "brushed teeth on own initiative today")
    
    # Set parental control
    db.set_parental_control(parent_id, child_id, 120, '[{"start":"22:00", "end":"06:00"}]', "medium", '["story", "song", "learning"]')
    
    print("Test data added successfully")

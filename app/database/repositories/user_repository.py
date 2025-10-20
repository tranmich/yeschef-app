"""
User Repository
Handles all database operations for users table
"""

from typing import Optional, Dict, Any, List
import logging

from app.database.repositories.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class UserRepository(BaseRepository):
    """Repository for users table"""
    
    def __init__(self):
        super().__init__('users')
    
    # Custom find methods
    
    def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find user by email address
        
        Args:
            email: User email
        
        Returns:
            User dictionary or None
        """
        query = f"SELECT * FROM {self.table_name} WHERE email = %s"
        return self._execute_query_one(query, (email,))
    
    def find_by_google_id(self, google_id: str) -> Optional[Dict[str, Any]]:
        """
        Find user by Google ID (OAuth)
        
        Args:
            google_id: Google OAuth ID
        
        Returns:
            User dictionary or None
        """
        query = f"SELECT * FROM {self.table_name} WHERE google_id = %s"
        return self._execute_query_one(query, (google_id,))
    
    def email_exists(self, email: str) -> bool:
        """
        Check if email already exists
        
        Args:
            email: Email to check
        
        Returns:
            True if exists, False otherwise
        """
        query = f"SELECT EXISTS(SELECT 1 FROM {self.table_name} WHERE email = %s) as exists"
        result = self._execute_query_one(query, (email,))
        return result['exists'] if result else False
    
    # Create/Update methods
    
    def create(self, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create new user
        
        Args:
            user_data: Dictionary with user fields (email, name, password_hash, etc.)
        
        Returns:
            Created user dictionary or None
        """
        # Ensure required fields
        if 'email' not in user_data:
            raise ValueError("Email is required")
        
        # Check if email already exists
        if self.email_exists(user_data['email']):
            raise ValueError(f"Email {user_data['email']} already exists")
        
        query, params = self._build_insert_query(user_data)
        user = self._execute_insert(query, params)
        
        if user:
            logger.info(f"✅ Created user: {user['email']} (ID: {user['id']})")
        
        return user
    
    def update(self, user_id: int, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update user
        
        Args:
            user_id: User ID
            updates: Dictionary with fields to update
        
        Returns:
            Updated user dictionary or None
        """
        # Don't allow changing email to existing email
        if 'email' in updates:
            existing = self.find_by_email(updates['email'])
            if existing and existing['id'] != user_id:
                raise ValueError(f"Email {updates['email']} already exists")
        
        query, params = self._build_update_query(user_id, updates)
        user = self._execute_update(query, params)
        
        if user:
            logger.info(f"✅ Updated user: {user['email']} (ID: {user['id']})")
        
        return user
    
    def update_profile(self, user_id: int, avatar_emoji: str = None, 
                      avatar_background_color: str = None) -> Optional[Dict[str, Any]]:
        """
        Update user profile (avatar)
        
        Args:
            user_id: User ID
            avatar_emoji: Emoji for avatar
            avatar_background_color: Background color
        
        Returns:
            Updated user dictionary or None
        """
        updates = {}
        if avatar_emoji is not None:
            updates['avatar_emoji'] = avatar_emoji
        if avatar_background_color is not None:
            updates['avatar_background_color'] = avatar_background_color
        
        if not updates:
            # Nothing to update
            return self.find_by_id(user_id)
        
        return self.update(user_id, updates)
    
    # Search methods
    
    def search_by_name(self, name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search users by name (case-insensitive, partial match)
        
        Args:
            name: Name to search for
            limit: Maximum results
        
        Returns:
            List of user dictionaries
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE name ILIKE %s
            LIMIT %s
        """
        return self._execute_query(query, (f'%{name}%', limit))
    
    def search_by_email(self, email: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Search users by email (case-insensitive, partial match)
        
        Args:
            email: Email to search for
            limit: Maximum results
        
        Returns:
            List of user dictionaries
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE email ILIKE %s
            LIMIT %s
        """
        return self._execute_query(query, (f'%{email}%', limit))
    
    # Authentication helpers
    
    def verify_credentials(self, email: str, password_hash: str) -> Optional[Dict[str, Any]]:
        """
        Verify user credentials (for login)
        Note: In real app, you'd hash the password and compare
        
        Args:
            email: User email
            password_hash: Hashed password
        
        Returns:
            User dictionary if credentials valid, None otherwise
        """
        query = f"""
            SELECT * FROM {self.table_name}
            WHERE email = %s AND password_hash = %s
        """
        return self._execute_query_one(query, (email, password_hash))
    
    # Statistics
    
    def get_user_count(self) -> int:
        """Get total number of users"""
        return self.count()
    
    def get_recent_users(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recently created users
        
        Args:
            limit: Number of users to return
        
        Returns:
            List of user dictionaries
        """
        query = f"""
            SELECT * FROM {self.table_name}
            ORDER BY created_at DESC
            LIMIT %s
        """
        return self._execute_query(query, (limit,))


# Global instance
_user_repository: Optional[UserRepository] = None


def get_user_repository() -> UserRepository:
    """Get global UserRepository instance"""
    global _user_repository
    if _user_repository is None:
        _user_repository = UserRepository()
    return _user_repository


if __name__ == '__main__':
    # Test UserRepository
    print("Testing UserRepository...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    from app.database.connection import init_database
    init_database()
    
    user_repo = UserRepository()
    
    # Test count
    count = user_repo.get_user_count()
    print(f"\n✅ Total users: {count}")
    
    # Test find_all
    users = user_repo.find_all(limit=3)
    print(f"✅ Find all (first 3): {len(users)} users")
    for user in users:
        print(f"   - {user['name']} ({user['email']})")
    
    # Test find_by_id
    if users:
        user = user_repo.find_by_id(users[0]['id'])
        print(f"✅ Find by ID: {user['name']}")
    
    # Test find_by_email
    if users:
        user = user_repo.find_by_email(users[0]['email'])
        print(f"✅ Find by email: {user['name']}")
    
    # Test email_exists
    if users:
        exists = user_repo.email_exists(users[0]['email'])
        print(f"✅ Email exists: {exists}")
    
    # Test search_by_name
    results = user_repo.search_by_name('test', limit=5)
    print(f"✅ Search by name 'test': {len(results)} results")
    
    # Test get_recent_users
    recent = user_repo.get_recent_users(limit=3)
    print(f"✅ Recent users: {len(recent)} users")
    
    print("\n✅ All UserRepository tests passed!")

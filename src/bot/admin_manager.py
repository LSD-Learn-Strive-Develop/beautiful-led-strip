"""Admin management for the bot."""

from pathlib import Path
from typing import Set


class AdminManager:
    """Manages the list of admin users.
    
    Super admin (from config) always has admin rights.
    Additional admins are stored in a file.
    """
    
    def __init__(self, admins_file: Path, super_admin_id: int):
        """Initialize admin manager.
        
        Args:
            admins_file: Path to file storing admin IDs
            super_admin_id: Super admin ID from config (always has rights)
        """
        self.admins_file = admins_file
        self.super_admin_id = super_admin_id
        self._admins: Set[int] = set()
        self._ensure_file()
        self._load_admins()
    
    def _ensure_file(self) -> None:
        """Ensure admins file and directory exist."""
        self.admins_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.admins_file.exists():
            self.admins_file.write_text("")
    
    def _load_admins(self) -> None:
        """Load admin IDs from file."""
        try:
            content = self.admins_file.read_text().strip()
            if content:
                self._admins = {int(line.strip()) for line in content.split('\n') if line.strip()}
            else:
                self._admins = set()
        except (ValueError, OSError) as e:
            print(f"Error loading admins: {e}")
            self._admins = set()
    
    def _save_admins(self) -> None:
        """Save admin IDs to file."""
        content = '\n'.join(str(admin_id) for admin_id in sorted(self._admins))
        self.admins_file.write_text(content)
    
    def is_super_admin(self, user_id: int) -> bool:
        """Check if user is super admin.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is super admin
        """
        return user_id == self.super_admin_id
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user has admin rights.
        
        Super admin and admins from file have rights.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is admin or super admin
        """
        return user_id == self.super_admin_id or user_id in self._admins
    
    def add_admin(self, user_id: int) -> bool:
        """Add a new admin.
        
        Args:
            user_id: Telegram user ID to add
            
        Returns:
            True if added, False if already exists
        """
        if user_id in self._admins:
            return False
        
        self._admins.add(user_id)
        self._save_admins()
        return True
    
    def remove_admin(self, user_id: int) -> bool:
        """Remove an admin.
        
        Args:
            user_id: Telegram user ID to remove
            
        Returns:
            True if removed, False if not found
        """
        if user_id not in self._admins:
            return False
        
        self._admins.discard(user_id)
        self._save_admins()
        return True
    
    def list_admins(self) -> Set[int]:
        """Get all admin IDs (excluding super admin).
        
        Returns:
            Set of admin user IDs
        """
        return self._admins.copy()

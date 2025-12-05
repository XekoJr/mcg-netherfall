import json
import base64
import os
from cryptography.fernet import Fernet

class SaveManager:
    """Manages game saves with encryption."""
    
    def __init__(self, save_file="save/save.dat"):
        # Create save directory if it doesn't exist
        self.save_dir = "save"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        self.save_file = save_file
        self.key = self._get_or_create_key()
        self.cipher = Fernet(self.key)
        
        # Default settings structure
        self.default_settings = {
            "master_volume": 100,
            "music_volume": 100,
            "effects_volume": 100,
            "resolution": (1366, 768),
            "fullscreen": False,
            "borderless": False,
            "language": "en",
            "high_score": 0,
            "skill_points": 0,
            "skills": {
                "max_health": {
                    "type": "stats",
                    "level": 0,
                    "max_level": 6,
                    "costs": [1, 2, 3, 6, 8, 10],
                    "effect": "+20 HP per level"
                },
                "speed": {
                    "type": "stats",
                    "level": 0,
                    "max_level": 6,
                    "costs": [1, 2, 3, 6, 7, 8],
                    "effect": "+5% Speed per level"
                },
                "heal": {
                    "type": "abilities",
                    "level": 0,
                    "max_level": 5,
                    "costs": [5, 6, 7, 8, 9],
                    "effect": "+2 HP/sec per level",
                    "requires": [["max_health", 3], ["speed", 3]]
                },
                "damage": {
                    "type": "stats",
                    "level": 0,
                    "max_level": 6,
                    "costs": [2, 3, 4, 5, 6, 7],
                    "effect": "+10% Damage per level",
                    "requires": [["heal", 2]]
                },
                "fire_rate": {
                    "type": "stats",
                    "level": 0,
                    "max_level": 6,
                    "costs": [3, 4, 5, 6, 7, 8],
                    "effect": "+10% Fire Rate per level",
                    "requires": [["damage", 1]]
                },
                "crit_damage": {
                    "type": "stats",
                    "level": 0,
                    "max_level": 6,
                    "costs": [4, 5, 6, 7, 8, 9],
                    "effect": "+30% Crit damage per level",
                    "requires": [["heal", 2]]
                },
                "crit_chance": {
                    "type": "stats",
                    "level": 0,
                    "max_level": 6,
                    "costs": [4, 5, 6, 7, 8, 9],
                    "effect": "+5% Crit Rate per level",
                    "requires": [["crit_damage", 1]]
                },
                "shield": {
                    "type": "abilities",
                    "level": 0,
                    "max_level": 5,
                    "costs": [3, 4, 5, 6, 7],
                    "effect": "-1s Cooldown per level",
                    "requires": [["crit_chance", 3], ["fire_rate", 3]]
                },
                "burn_damage": {
                    "type": "abilities",
                    "level": 0,
                    "max_level": 5,
                    "costs": [4, 5, 6, 7, 8],
                    "effect": "+0.5 Fire Damage per level",
                    "achievement_required": "beat_Pyraxis"
                },
                "burn_duration": {
                    "type": "abilities",
                    "level": 0,
                    "max_level": 5,
                    "costs": [4, 5, 6, 7, 8],
                    "effect": "+1s Fire Duration per level",
                    "requires": [["burn_damage", 3]],
                    "achievement_required": "beat_Pyraxis"
                },
                "invincibility": {
                    "type": "abilities",
                    "level": 0,
                    "max_level": 5,
                    "costs": [6, 7, 8, 9, 10],
                    "effect": "+0.5s Invincibility per level",
                    "requires": [["burn_duration", 1]],
                    "achievement_required": "beat_Arcanos"
                }
            },
            "achievements": {
                "beat_Pyraxis": False,
                "beat_Arcanos": False,
                "beat_Nyxblade": False,
            },
            "characters_unlocked": {
                "ranger": True,
                "gigachad": False
            }
        }

    def _get_or_create_key(self):
        """Get encryption key or create one."""
        key_file = os.path.join(self.save_dir, ".key")
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                return f.read()
        else:
            # Generate new key
            key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(key)
            return key

    def load(self):
        """Load and decrypt save data."""
        if not os.path.exists(self.save_file):
            return self.default_settings.copy()
        
        try:
            with open(self.save_file, "rb") as f:
                encrypted_data = f.read()
            
            # Decrypt
            decrypted_data = self.cipher.decrypt(encrypted_data)
            data = json.loads(decrypted_data.decode())
            
            # Merge with defaults to ensure all keys exist
            merged_data = self._merge_with_defaults(data)
            return merged_data
            
        except Exception as e:
            print(f"Failed to load save file: {e}")
            return self.default_settings.copy()

    def save(self, data):
        """Encrypt and save data."""
        try:
            # Convert to JSON
            json_data = json.dumps(data, indent=4)
            
            # Encrypt
            encrypted_data = self.cipher.encrypt(json_data.encode())
            
            # Write to file
            with open(self.save_file, "wb") as f:
                f.write(encrypted_data)
            
            return True
            
        except Exception as e:
            print(f"Failed to save file: {e}")
            return False

    def _merge_with_defaults(self, data):
        """Merge loaded data with defaults to ensure all keys exist."""
        merged = self.default_settings.copy()
        
        for key, value in data.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict): # Recursive merge for nested dicts
                merged[key].update(value)
            else:
                merged[key] = value
        
        return merged

    def reset(self):
        """Delete save file and reset to defaults."""
        try:
            if os.path.exists(self.save_file):
                os.remove(self.save_file)
            return self.default_settings.copy()
        except Exception as e:
            print(f"Failed to delete save file: {e}")
            return self.default_settings.copy()

    def get(self, key, default=None):
        """Get a specific value from settings."""
        data = self.load()
        return data.get(key, default)

    def set(self, key, value):
        """Set a specific value and save."""
        data = self.load()
        data[key] = value
        self.save(data)
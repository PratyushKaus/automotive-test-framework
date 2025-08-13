import pytest
from src.lib.test_base import TestBase
from src.lib.can_interface import CANInterface
from src.lib.diagnostic_interface import DiagnosticInterface
import time

class TestSecurityAccess(TestBase):
    """Test cases for Security Access"""
    
    def setup(self):
        """Test setup - initialize interfaces"""
        self.can_interface = CANInterface(
            channel='can0',
            bitrate=500000
        )
        self.diag_interface = DiagnosticInterface(self.can_interface)
        
    def teardown(self):
        """Test cleanup"""
        if hasattr(self, 'can_interface'):
            self.can_interface.close()
    
    def request_seed(self, level: int) -> tuple:
        """
        Helper method to request seed for security access
        
        Args:
            level: Security access level
            
        Returns:
            Tuple of (success, seed data)
        """
        # UDS Service 0x27 with odd level (request seed)
        return self.diag_interface.send_diagnostic_request(0x27, 2 * level - 1, [])
    
    def send_key(self, level: int, key: list) -> bool:
        """
        Helper method to send key for security access
        
        Args:
            level: Security access level
            key: Calculated key bytes
            
        Returns:
            bool: True if key accepted
        """
        # UDS Service 0x27 with even level (send key)
        return self.diag_interface.send_diagnostic_request(0x27, 2 * level, key)
    
    def test_security_access_level_1(self):
        """Test security access level 1 (usually programming)"""
        # Request seed
        success, seed_data = self.request_seed(1)
        self.validate_response(success, True, "Requesting seed for level 1")
        assert seed_data is not None, "No seed received"
        
        # Calculate key (implement your key calculation algorithm)
        key = self.calculate_key(seed_data)
        
        # Send key
        success = self.send_key(1, key)
        self.validate_response(success, True, "Sending key for level 1")
    
    def test_security_access_level_3(self):
        """Test security access level 3 (usually configuration)"""
        # Request seed
        success, seed_data = self.request_seed(3)
        self.validate_response(success, True, "Requesting seed for level 3")
        assert seed_data is not None, "No seed received"
        
        # Calculate key (implement your key calculation algorithm)
        key = self.calculate_key(seed_data)
        
        # Send key
        success = self.send_key(3, key)
        self.validate_response(success, True, "Sending key for level 3")
    
    def test_invalid_key(self):
        """Test response to invalid key"""
        # Request seed
        success, seed_data = self.request_seed(1)
        self.validate_response(success, True, "Requesting seed")
        
        # Send invalid key
        invalid_key = [0x00, 0x00, 0x00, 0x00]
        success = self.send_key(1, invalid_key)
        
        # Should fail
        assert not success, "Invalid key was accepted"
    
    def test_delay_after_invalid_attempts(self):
        """Test delay enforcement after invalid attempts"""
        max_attempts = 3
        
        for _ in range(max_attempts):
            # Request seed
            success, seed_data = self.request_seed(1)
            self.validate_response(success, True, "Requesting seed")
            
            # Send invalid key
            invalid_key = [0x00, 0x00, 0x00, 0x00]
            self.send_key(1, invalid_key)
        
        # Try one more time - should be delayed
        start_time = time.time()
        success, _ = self.request_seed(1)
        end_time = time.time()
        
        # Verify delay was enforced (usually 10 seconds)
        assert end_time - start_time >= 10, "Delay not enforced after invalid attempts"
    
    def calculate_key(self, seed_data: list) -> list:
        """
        Calculate key from seed (example implementation)
        
        Args:
            seed_data: Seed received from ECU
            
        Returns:
            Calculated key bytes
        """
        # TODO: Implement actual key calculation algorithm
        # This is just a placeholder
        return [x ^ 0xFF for x in seed_data]  # Simple XOR example
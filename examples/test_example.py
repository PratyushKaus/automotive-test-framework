import pytest
from src.lib.test_base import TestBase
from src.lib.can_interface import CANInterface
from src.lib.diagnostic_interface import DiagnosticInterface

class TestECUDiagnostics(TestBase):
    """Example test case for ECU diagnostics"""
    
    def setup(self):
        """Test setup - initialize interfaces"""
        # Initialize CAN interface
        self.can_interface = CANInterface(
            channel='can0',  # Update with your CAN interface
            bitrate=500000
        )
        
        # Initialize diagnostic interface
        self.diag_interface = DiagnosticInterface(self.can_interface)
        
        # Set custom diagnostic IDs if needed
        self.diag_interface.set_ids(tester_id=0x7E0, ecu_id=0x7E8)
        
    def teardown(self):
        """Test cleanup"""
        if hasattr(self, 'can_interface'):
            self.can_interface.close()
            
    def test_read_part_number(self):
        """Test reading ECU part number"""
        # DID for part number (example)
        PART_NUMBER_DID = 0xF123
        
        # Read part number
        success, data = self.diag_interface.read_data_by_identifier(PART_NUMBER_DID)
        
        # Validate response
        self.validate_response(success, True, "Reading part number")
        assert data is not None, "No data received"
        
        # Store part number for later use
        self.set_test_data('part_number', data)
        
    def test_write_configuration(self):
        """Test writing configuration data"""
        # DID for configuration (example)
        CONFIG_DID = 0xF124
        CONFIG_DATA = [0x01, 0x02, 0x03, 0x04]
        
        # Write configuration
        success = self.diag_interface.write_data_by_identifier(CONFIG_DID, CONFIG_DATA)
        
        # Validate write operation
        self.validate_response(success, True, "Writing configuration")
        
        # Read back and verify
        read_success, read_data = self.diag_interface.read_data_by_identifier(CONFIG_DID)
        self.validate_response(read_success, True, "Reading back configuration")
        self.validate_response(read_data, CONFIG_DATA, "Verifying configuration data")
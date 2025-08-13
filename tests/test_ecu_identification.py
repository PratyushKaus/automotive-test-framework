import pytest
from src.lib.test_base import TestBase
from src.lib.can_interface import CANInterface
from src.lib.diagnostic_interface import DiagnosticInterface

class TestECUIdentification(TestBase):
    """Test cases for ECU identification"""
    
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
    
    def test_read_vin(self):
        """Test reading Vehicle Identification Number"""
        VIN_DID = 0xF190  # Standard DID for VIN
        
        success, data = self.diag_interface.read_data_by_identifier(VIN_DID)
        self.validate_response(success, True, "Reading VIN")
        assert data is not None, "No VIN data received"
        
        # Convert byte array to ASCII string
        vin = ''.join(chr(x) for x in data)
        self.set_test_data('vin', vin)
        
        # Validate VIN format (17 characters)
        assert len(vin) == 17, f"Invalid VIN length: {len(vin)}"
    
    def test_read_ecu_serial(self):
        """Test reading ECU Serial Number"""
        SERIAL_DID = 0xF18C  # Standard DID for ECU Serial Number
        
        success, data = self.diag_interface.read_data_by_identifier(SERIAL_DID)
        self.validate_response(success, True, "Reading ECU Serial")
        assert data is not None, "No Serial Number data received"
        
        serial = ''.join(chr(x) for x in data)
        self.set_test_data('ecu_serial', serial)
    
    def test_read_sw_version(self):
        """Test reading Software Version"""
        SW_VERSION_DID = 0xF189  # Standard DID for SW Version
        
        success, data = self.diag_interface.read_data_by_identifier(SW_VERSION_DID)
        self.validate_response(success, True, "Reading Software Version")
        assert data is not None, "No Software Version data received"
        
        version = ''.join(chr(x) for x in data)
        self.set_test_data('sw_version', version)
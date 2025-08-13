import pytest
from src.lib.test_base import TestBase
from src.lib.can_interface import CANInterface
from src.lib.diagnostic_interface import DiagnosticInterface
import time

class TestDTCOperations(TestBase):
    """Test cases for Diagnostic Trouble Code operations"""
    
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
    
    def read_dtcs(self):
        """Helper method to read DTCs"""
        # UDS Service 0x19 with sub-function 0x02 (Read DTC by status mask)
        success, data = self.diag_interface.send_diagnostic_request(0x19, 0x02, [0xFF])
        return success, data
    
    def test_clear_dtcs(self):
        """Test clearing DTCs"""
        # First read initial DTCs
        success, initial_dtcs = self.read_dtcs()
        self.validate_response(success, True, "Reading initial DTCs")
        
        # UDS Service 0x14 (Clear diagnostic information)
        success = self.diag_interface.send_diagnostic_request(0x14, 0xFF, [])
        self.validate_response(success, True, "Clearing DTCs")
        
        # Wait for ECU to process
        time.sleep(1)
        
        # Read DTCs again to verify they are cleared
        success, final_dtcs = self.read_dtcs()
        self.validate_response(success, True, "Reading DTCs after clear")
        
        # Verify no DTCs are present
        assert len(final_dtcs) <= 3, "DTCs still present after clear"
    
    def test_dtc_snapshot(self):
        """Test reading DTC snapshot data"""
        # UDS Service 0x19 with sub-function 0x04 (Read DTC snapshot records)
        success, data = self.diag_interface.send_diagnostic_request(0x19, 0x04, [])
        self.validate_response(success, True, "Reading DTC snapshot")
        
        if data and len(data) > 3:
            # Store snapshot data for analysis
            self.set_test_data('dtc_snapshot', data)
    
    def test_dtc_extended_data(self):
        """Test reading DTC extended data"""
        # UDS Service 0x19 with sub-function 0x06 (Read DTC extended data)
        success, data = self.diag_interface.send_diagnostic_request(0x19, 0x06, [])
        self.validate_response(success, True, "Reading DTC extended data")
        
        if data and len(data) > 3:
            # Store extended data for analysis
            self.set_test_data('dtc_extended_data', data)
    
    @pytest.mark.skip_production
    def test_dtc_permanent_status(self):
        """Test reading permanent DTC status"""
        # UDS Service 0x19 with sub-function 0x0A (Read permanent DTCs)
        success, data = self.diag_interface.send_diagnostic_request(0x19, 0x0A, [])
        self.validate_response(success, True, "Reading permanent DTCs")
        
        if data and len(data) > 3:
            # Store permanent DTC data
            self.set_test_data('permanent_dtcs', data)
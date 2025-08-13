import pytest
from src.lib.test_base import TestBase
from src.lib.can_interface import CANInterface
from src.lib.diagnostic_interface import DiagnosticInterface
import time

class TestRoutineControl(TestBase):
    """Test cases for Routine Control"""
    
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
    
    def start_routine(self, routine_id: int, params: list = None) -> bool:
        """
        Start a routine
        
        Args:
            routine_id: Identifier for the routine
            params: Optional parameters for the routine
            
        Returns:
            bool: True if routine started successfully
        """
        # UDS Service 0x31 with sub-function 0x01 (start routine)
        data = [(routine_id >> 8) & 0xFF, routine_id & 0xFF]
        if params:
            data.extend(params)
        return self.diag_interface.send_diagnostic_request(0x31, 0x01, data)
    
    def stop_routine(self, routine_id: int) -> bool:
        """
        Stop a routine
        
        Args:
            routine_id: Identifier for the routine
            
        Returns:
            bool: True if routine stopped successfully
        """
        # UDS Service 0x31 with sub-function 0x02 (stop routine)
        data = [(routine_id >> 8) & 0xFF, routine_id & 0xFF]
        return self.diag_interface.send_diagnostic_request(0x31, 0x02, data)
    
    def get_routine_results(self, routine_id: int) -> tuple:
        """
        Get results from a routine
        
        Args:
            routine_id: Identifier for the routine
            
        Returns:
            Tuple of (success, results data)
        """
        # UDS Service 0x31 with sub-function 0x03 (request routine results)
        data = [(routine_id >> 8) & 0xFF, routine_id & 0xFF]
        return self.diag_interface.send_diagnostic_request(0x31, 0x03, data)
    
    def test_self_test_routine(self):
        """Test ECU self-test routine"""
        SELF_TEST_ROUTINE_ID = 0xFF00
        
        # Start self-test
        success = self.start_routine(SELF_TEST_ROUTINE_ID)
        self.validate_response(success, True, "Starting self-test routine")
        
        # Wait for routine to complete
        time.sleep(5)
        
        # Get results
        success, results = self.get_routine_results(SELF_TEST_ROUTINE_ID)
        self.validate_response(success, True, "Getting self-test results")
        assert results is not None, "No results received"
        
        # Store results for analysis
        self.set_test_data('self_test_results', results)
    
    def test_actuator_test_routine(self):
        """Test actuator test routine"""
        ACTUATOR_TEST_ID = 0xFF01
        
        # Start actuator test
        success = self.start_routine(ACTUATOR_TEST_ID)
        self.validate_response(success, True, "Starting actuator test")
        
        # Monitor for 10 seconds
        time.sleep(10)
        
        # Stop test
        success = self.stop_routine(ACTUATOR_TEST_ID)
        self.validate_response(success, True, "Stopping actuator test")
    
    def test_memory_check_routine(self):
        """Test memory check routine"""
        MEMORY_CHECK_ID = 0xFF02
        
        # Start memory check with parameters
        params = [0x01, 0x02]  # Example parameters
        success = self.start_routine(MEMORY_CHECK_ID, params)
        self.validate_response(success, True, "Starting memory check")
        
        # Wait for check to complete
        time.sleep(3)
        
        # Get results
        success, results = self.get_routine_results(MEMORY_CHECK_ID)
        self.validate_response(success, True, "Getting memory check results")
        assert results is not None, "No results received"
    
    def test_invalid_routine(self):
        """Test response to invalid routine ID"""
        INVALID_ROUTINE_ID = 0x0000
        
        # Try to start invalid routine
        success = self.start_routine(INVALID_ROUTINE_ID)
        
        # Should fail
        assert not success, "Invalid routine was accepted"
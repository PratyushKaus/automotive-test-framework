import pytest
from loguru import logger
from datetime import datetime
from typing import Any, Dict, Optional

class TestBase:
    """Base class for all test cases"""
    
    def __init__(self):
        self.test_name = self.__class__.__name__
        self.start_time = None
        self.end_time = None
        self.test_result = None
        self.test_data = {}
        
    def setup_method(self, method):
        """Setup method called before each test method"""
        self.start_time = datetime.now()
        logger.info(f"Starting test: {self.test_name}")
        self.setup()
        
    def teardown_method(self, method):
        """Teardown method called after each test method"""
        self.end_time = datetime.now()
        self.teardown()
        duration = (self.end_time - self.start_time).total_seconds()
        logger.info(f"Test {self.test_name} completed in {duration:.2f} seconds")
        
    def setup(self):
        """
        Setup method to be implemented by test cases
        This method should contain test-specific setup
        """
        pass
        
    def teardown(self):
        """
        Teardown method to be implemented by test cases
        This method should contain test-specific cleanup
        """
        pass
    
    def set_test_data(self, key: str, value: Any):
        """
        Store test-specific data
        
        Args:
            key: Data identifier
            value: Data to store
        """
        self.test_data[key] = value
        
    def get_test_data(self, key: str) -> Optional[Any]:
        """
        Retrieve test-specific data
        
        Args:
            key: Data identifier
            
        Returns:
            Stored data or None if not found
        """
        return self.test_data.get(key)
    
    @staticmethod
    def validate_response(actual: Any, expected: Any, description: str = ""):
        """
        Validate test response
        
        Args:
            actual: Actual value
            expected: Expected value
            description: Description of the validation
        """
        try:
            assert actual == expected, f"{description}: Expected {expected}, got {actual}"
            logger.info(f"Validation passed: {description}")
        except AssertionError as e:
            logger.error(str(e))
            raise
            
    def skip_test(self, reason: str):
        """
        Skip the current test
        
        Args:
            reason: Reason for skipping the test
        """
        logger.warning(f"Skipping test {self.test_name}: {reason}")
        pytest.skip(reason)
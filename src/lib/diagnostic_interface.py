from loguru import logger
from typing import List, Optional, Tuple

class DiagnosticInterface:
    """Base class for diagnostic communication"""
    
    def __init__(self, can_interface):
        """
        Initialize diagnostic interface
        
        Args:
            can_interface: CAN interface instance
        """
        self.can_interface = can_interface
        self.tester_id = 0x7E0  # Default tester ID
        self.ecu_id = 0x7E8    # Default ECU response ID
        
    def send_diagnostic_request(self, service_id: int, sub_function: int = None,
                              data: List[int] = None) -> bool:
        """
        Send a diagnostic request
        
        Args:
            service_id: UDS service ID
            sub_function: Optional sub-function
            data: Optional additional data
            
        Returns:
            bool: True if request sent successfully
        """
        message_data = [service_id]
        
        if sub_function is not None:
            message_data.append(sub_function)
            
        if data:
            message_data.extend(data)
            
        # Pad message to 8 bytes if needed
        while len(message_data) < 8:
            message_data.append(0x00)
            
        return self.can_interface.send_message(self.tester_id, message_data)
        
    def receive_diagnostic_response(self, timeout: float = 1.0) -> Tuple[bool, Optional[List[int]]]:
        """
        Receive a diagnostic response
        
        Args:
            timeout: Time to wait for response in seconds
            
        Returns:
            Tuple containing:
            - bool: True if valid response received
            - List[int]: Response data or None if no valid response
        """
        msg = self.can_interface.receive_message(timeout)
        
        if msg is None:
            logger.warning("No diagnostic response received")
            return False, None
            
        if msg.arbitration_id != self.ecu_id:
            logger.warning(f"Received message with unexpected ID: {hex(msg.arbitration_id)}")
            return False, None
            
        return True, list(msg.data)
        
    def set_ids(self, tester_id: int, ecu_id: int):
        """
        Set custom tester and ECU IDs
        
        Args:
            tester_id: Custom tester ID
            ecu_id: Custom ECU response ID
        """
        self.tester_id = tester_id
        self.ecu_id = ecu_id
        logger.info(f"Set tester ID to {hex(tester_id)} and ECU ID to {hex(ecu_id)}")
        
    def read_data_by_identifier(self, did: int) -> Tuple[bool, Optional[List[int]]]:
        """
        Read data by identifier (Service 0x22)
        
        Args:
            did: Data identifier
            
        Returns:
            Tuple containing:
            - bool: True if read successful
            - List[int]: Data read or None if failed
        """
        service_id = 0x22
        data = [(did >> 8) & 0xFF, did & 0xFF]  # Split DID into bytes
        
        if not self.send_diagnostic_request(service_id, data=data):
            return False, None
            
        success, response = self.receive_diagnostic_response()
        if not success or response[0] != service_id + 0x40:  # Check positive response
            return False, None
            
        return True, response[3:]  # Return data without service ID and DID
        
    def write_data_by_identifier(self, did: int, data: List[int]) -> bool:
        """
        Write data by identifier (Service 0x2E)
        
        Args:
            did: Data identifier
            data: Data to write
            
        Returns:
            bool: True if write successful
        """
        service_id = 0x2E
        request_data = [(did >> 8) & 0xFF, did & 0xFF]  # Split DID into bytes
        request_data.extend(data)
        
        if not self.send_diagnostic_request(service_id, data=request_data):
            return False
            
        success, response = self.receive_diagnostic_response()
        if not success or response[0] != service_id + 0x40:  # Check positive response
            return False
            
        return True
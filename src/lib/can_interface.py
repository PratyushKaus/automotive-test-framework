import can
from loguru import logger
from typing import Optional, Dict, List

class CANInterface:
    """Base class for CAN communication"""
    
    def __init__(self, channel: str, bitrate: int = 500000, bus_type: str = 'socketcan'):
        """
        Initialize CAN interface
        
        Args:
            channel: CAN interface name
            bitrate: Bitrate of CAN bus
            bus_type: Type of CAN bus (socketcan, kvaser, etc.)
        """
        try:
            self.bus = can.interface.Bus(channel=channel, 
                                       bustype=bus_type,
                                       bitrate=bitrate)
            logger.info(f"Successfully initialized CAN interface on {channel}")
        except Exception as e:
            logger.error(f"Failed to initialize CAN interface: {str(e)}")
            raise
    
    def send_message(self, arbitration_id: int, data: List[int], extended_id: bool = False) -> bool:
        """
        Send a CAN message
        
        Args:
            arbitration_id: CAN message ID
            data: List of bytes to send
            extended_id: Whether to use extended CAN ID
            
        Returns:
            bool: True if message sent successfully
        """
        try:
            msg = can.Message(arbitration_id=arbitration_id,
                            data=data,
                            is_extended_id=extended_id)
            self.bus.send(msg)
            logger.debug(f"Sent CAN message: ID={hex(arbitration_id)}, Data={data}")
            return True
        except Exception as e:
            logger.error(f"Failed to send CAN message: {str(e)}")
            return False
    
    def receive_message(self, timeout: float = 1.0) -> Optional[can.Message]:
        """
        Receive a CAN message
        
        Args:
            timeout: Time to wait for message in seconds
            
        Returns:
            Received CAN message or None if timeout
        """
        try:
            msg = self.bus.recv(timeout=timeout)
            if msg:
                logger.debug(f"Received CAN message: ID={hex(msg.arbitration_id)}, Data={msg.data}")
            return msg
        except Exception as e:
            logger.error(f"Error receiving CAN message: {str(e)}")
            return None
    
    def close(self):
        """Close the CAN interface"""
        try:
            self.bus.shutdown()
            logger.info("CAN interface closed successfully")
        except Exception as e:
            logger.error(f"Error closing CAN interface: {str(e)}")
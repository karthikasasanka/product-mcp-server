"""
Dynamic argument extraction for CSV classifier.
Enhances the CSV classifier to extract actual values from user messages.
"""

import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class ArgumentExtractor:
    """Extracts dynamic arguments from user messages for product operations."""
    
    def __init__(self):
        # Regex patterns for different field types
        self.name_patterns = [
            r'(?:add|create|new product called?|product called?|named?)\s+([^,]+?)(?:\s*,|\s+with|\s+price|$)',
            r'(?:add|create)\s+([^,]+?)(?:\s*,|\s+with|\s+price|$)',
        ]
        
        self.price_patterns = [
            r'price\s*\$?(\d+(?:\.\d{2})?)',
            r'\$(\d+(?:\.\d{2})?)',
            r'(\d+(?:\.\d{2})?)\s*dollars?',
            r'(\d+(?:\.\d{2})?)\s*USD',
        ]
        
        self.id_patterns = [
            r'(?:product\s+)?id\s+(\d+)',
            r'(?:update|modify|change|edit|delete|remove|drop|get|find|retrieve)\s+(?:product\s+)?(\d+)',
        ]
        
        self.description_patterns = [
            r'with\s+([^,]+?)(?:\s*,|\s+price|$)',
            r'description[:\s]+([^,]+?)(?:\s*,|\s+price|$)',
            r'features?[:\s]+([^,]+?)(?:\s*,|\s+price|$)',
        ]
        
        self.name_prefix_patterns = [
            r'starting\s+with\s+([A-Za-z])',
            r'that\s+start\s+with\s+([A-Za-z])',
            r'beginning\s+with\s+([A-Za-z])',
            r'starting\s+with\s+letter\s+([A-Za-z])',
        ]
    
    def extract_arguments(self, message: str, tool_name: str, static_args: Dict[str, Any]) -> Dict[str, Any]:
        """Extract dynamic arguments from user message based on tool type."""
        message_lower = message.lower()
        
        if tool_name == "product.create":
            return self._extract_create_args(message, message_lower)
        elif tool_name == "product.update":
            return self._extract_update_args(message, message_lower)
        elif tool_name == "product.delete":
            return self._extract_delete_args(message, message_lower)
        elif tool_name == "product.get":
            return self._extract_get_args(message, message_lower)
        elif tool_name == "product.list":
            return self._extract_list_args(message, message_lower)
        else:
            # For other tools, return static args
            return static_args
    
    def _extract_create_args(self, message: str, message_lower: str) -> Dict[str, Any]:
        """Extract arguments for product creation."""
        args = {}
        
        # Extract name
        name = self._extract_name(message, message_lower)
        if name:
            args['name'] = name
        
        # Extract price
        price = self._extract_price(message, message_lower)
        if price:
            args['price'] = price
        
        # Extract description
        description = self._extract_description(message, message_lower)
        if description:
            args['description'] = description
        
        logger.info(f"📝 Extracted create args: {args}")
        return args
    
    def _extract_update_args(self, message: str, message_lower: str) -> Dict[str, Any]:
        """Extract arguments for product updates."""
        args = {}
        
        # Extract ID
        product_id = self._extract_id(message, message_lower)
        if product_id:
            args['id'] = product_id
        
        # Extract other fields (name, price, description)
        name = self._extract_name(message, message_lower)
        if name:
            args['name'] = name
        
        price = self._extract_price(message, message_lower)
        if price:
            args['price'] = price
        
        description = self._extract_description(message, message_lower)
        if description:
            args['description'] = description
        
        logger.info(f"📝 Extracted update args: {args}")
        return args
    
    def _extract_delete_args(self, message: str, message_lower: str) -> Dict[str, Any]:
        """Extract arguments for product deletion."""
        args = {}
        
        product_id = self._extract_id(message, message_lower)
        if product_id:
            args['id'] = product_id
        
        logger.info(f"📝 Extracted delete args: {args}")
        return args
    
    def _extract_get_args(self, message: str, message_lower: str) -> Dict[str, Any]:
        """Extract arguments for product retrieval."""
        args = {}
        
        product_id = self._extract_id(message, message_lower)
        if product_id:
            args['id'] = product_id
        
        logger.info(f"📝 Extracted get args: {args}")
        return args
    
    def _extract_list_args(self, message: str, message_lower: str) -> Dict[str, Any]:
        """Extract arguments for product listing."""
        args = {}
        
        # Extract name prefix for filtering
        name_prefix = self._extract_name_prefix(message, message_lower)
        if name_prefix:
            args['name_prefix'] = name_prefix
        
        logger.info(f"📝 Extracted list args: {args}")
        return args
    
    def _extract_name_prefix(self, message: str, message_lower: str) -> Optional[str]:
        """Extract name prefix from message for filtering."""
        for pattern in self.name_prefix_patterns:
            match = re.search(pattern, message_lower)
            if match:
                prefix = match.group(1).strip().upper()  # Convert to uppercase for consistency
                return prefix
        return None
    
    def _extract_name(self, message: str, message_lower: str) -> Optional[str]:
        """Extract product name from message."""
        for pattern in self.name_patterns:
            match = re.search(pattern, message_lower)
            if match:
                name = match.group(1).strip()
                # Clean up the name
                name = re.sub(r'\s+', ' ', name)  # Normalize whitespace
                return name.title()  # Capitalize properly
        return None
    
    def _extract_price(self, message: str, message_lower: str) -> Optional[float]:
        """Extract price from message."""
        for pattern in self.price_patterns:
            match = re.search(pattern, message_lower)
            if match:
                try:
                    price = float(match.group(1))
                    return price
                except ValueError:
                    continue
        return None
    
    def _extract_id(self, message: str, message_lower: str) -> Optional[int]:
        """Extract product ID from message."""
        for pattern in self.id_patterns:
            match = re.search(pattern, message_lower)
            if match:
                try:
                    product_id = int(match.group(1))
                    return product_id
                except ValueError:
                    continue
        return None
    
    def _extract_description(self, message: str, message_lower: str) -> Optional[str]:
        """Extract description from message."""
        for pattern in self.description_patterns:
            match = re.search(pattern, message_lower)
            if match:
                description = match.group(1).strip()
                # Clean up the description
                description = re.sub(r'\s+', ' ', description)  # Normalize whitespace
                return description
        
        # If no explicit description pattern, try to extract everything after name and price
        # This is a fallback for cases like "add Smartphone Pro, with touchscreen, price $1249"
        name = self._extract_name(message, message_lower)
        price = self._extract_price(message, message_lower)
        
        if name:
            # Remove name and price from message, what's left might be description
            temp_message = message_lower
            temp_message = re.sub(rf'(?:add|create|new product called?|product called?|named?)\s+{re.escape(name.lower())}', '', temp_message)
            if price:
                temp_message = re.sub(rf'price\s*\$?{price}|${price}|{price}\s*dollars?', '', temp_message)
            
            # Clean up and extract remaining text
            temp_message = re.sub(r'^\s*[,]\s*', '', temp_message)  # Remove leading comma
            temp_message = re.sub(r'\s+', ' ', temp_message).strip()  # Normalize whitespace
            
            if temp_message and len(temp_message) > 2:  # Only if there's meaningful content
                return temp_message
        
        return None

# Global instance
argument_extractor = ArgumentExtractor()

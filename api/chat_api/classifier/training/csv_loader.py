"""
CSV pattern loader for the classifier.
"""

import csv
import logging
from pathlib import Path
from typing import List
from ..models import QueryPattern

logger = logging.getLogger(__name__)

class CSVPatternLoader:
    """Loads query patterns from CSV files."""
    
    def __init__(self, data_dir: str = "api/chat_api/classifier/training/patterns"):
        self.data_dir = Path(data_dir)
    
    def load_patterns_from_csv(self) -> List[QueryPattern]:
        """Load all patterns from CSV files in the data directory."""
        patterns = []
        
        # Load from all CSV files in the patterns directory
        for csv_file in self.data_dir.glob("*.csv"):
            logger.info(f"📂 Loading patterns from {csv_file}")
            patterns.extend(self._load_csv_file(csv_file))
        
        logger.info(f"✅ Loaded {len(patterns)} patterns from CSV files")
        return patterns
    
    def _load_csv_file(self, csv_file: Path) -> List[QueryPattern]:
        """Load patterns from a single CSV file."""
        patterns = []
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    pattern = QueryPattern(
                        query_pattern=row['query_pattern'].strip(),
                        tool_name=row['tool_name'].strip(),
                        tool_args=row['tool_args'].strip(),
                        confidence=float(row['confidence']),
                        query_type=row['query_type'].strip(),
                        entity=row['entity'].strip(),
                        intent=row['intent'].strip(),
                        description=row['description'].strip()
                    )
                    patterns.append(pattern)
        except Exception as e:
            logger.error(f"❌ Error loading {csv_file}: {e}")
        
        return patterns

import hashlib
import re

from backend.agents.security_agent.models.domain import NormalizedDatasetRecord

class DatasetCleaner:
    def __init__(self):
        self.seen_hashes = set()

    def _hash_text(self, text: str) -> str:
        """Create a deterministic hash for duplicate detection."""
        return hashlib.sha256(text.lower().strip().encode("utf-8")).hexdigest()

    def clean_record(self, record: NormalizedDatasetRecord) -> NormalizedDatasetRecord | None:
        """
        Cleans a single record.
        Returns None if the record is invalid or a duplicate.
        """
        # Validate missing fields
        if not record.text or not record.text.strip():
            return None
            
        # Whitespace normalization
        cleaned_text = re.sub(r'\s+', ' ', record.text).strip()
        record.text = cleaned_text
        
        # Check for duplicates
        text_hash = self._hash_text(record.text)
        if text_hash in self.seen_hashes:
            return None
            
        self.seen_hashes.add(text_hash)
        
        # Fallback values
        if not record.category:
            record.category = "Unknown"
        if not record.severity:
            record.severity = "MEDIUM"
            
        return record

    def clean_batch(self, records: list[NormalizedDatasetRecord]) -> dict:
        """
        Cleans a batch of records.
        Returns a dictionary with 'cleaned_records' and statistics.
        """
        cleaned = []
        stats = {
            "total_input": len(records),
            "valid": 0,
            "duplicates_removed": 0,
            "invalid_skipped": 0
        }
        
        initial_seen = len(self.seen_hashes)
        
        for record in records:
            if not record.text or not record.text.strip():
                stats["invalid_skipped"] += 1
                continue
                
            text_hash = self._hash_text(record.text)
            if text_hash in self.seen_hashes:
                stats["duplicates_removed"] += 1
                continue
                
            # If we get here, it's valid and unique (within this session)
            cleaned_record = self.clean_record(record)
            if cleaned_record:
                cleaned.append(cleaned_record)
                stats["valid"] += 1
            else:
                stats["invalid_skipped"] += 1
                
        return {
            "cleaned_records": cleaned,
            "stats": stats
        }

def mask_sensitive_value(value: str, pii_type: str = "") -> str:
    """
    Masks sensitive values based on their type or length.
    
    Args:
        value: The raw string to mask.
        pii_type: Optional type hint (e.g., 'EMAIL', 'PHONE', 'CREDIT_CARD').
        
    Returns:
        The masked string.
    """
    if not value:
        return value
        
    ptype = pii_type.upper()
    
    if ptype == "EMAIL" or "@" in value:
        parts = value.split("@")
        if len(parts) == 2:
            user, domain = parts
            masked_user = user[0] + "***" if len(user) > 0 else "***"
            domain_parts = domain.split(".")
            if len(domain_parts) >= 2:
                masked_domain = domain_parts[0][0] + "***." + ".".join(domain_parts[1:])
            else:
                masked_domain = domain[0] + "***" if len(domain) > 0 else "***"
            return f"{masked_user}@{masked_domain}"
            
    if ptype in ["CREDIT_CARD", "CREDIT CARD", "PCI-DSS"]:
        # Mask all but first 4 and last 4 if long enough
        clean_val = value.replace(" ", "").replace("-", "")
        if len(clean_val) >= 12:
            return value[:4] + "*" * (len(value) - 8) + value[-4:]
            
    if ptype in ["PHONE"]:
        clean_val = value.replace(" ", "").replace("-", "")
        if len(clean_val) >= 10:
            return value[:2] + "*" * (len(value) - 4) + value[-2:]
            
    if ptype in ["AWS_ACCESS_KEY", "AWS KEY"]:
        if value.startswith("AKIA") or value.startswith("ASIA"):
            return value[:4] + "*" * (len(value) - 8) + value[-4:]
            
    if ptype in ["JWT_TOKEN", "JWT"]:
        if value.startswith("eyJ"):
            return value[:4] + "*" * 8
            
    if ptype in ["PASSWORD", "SECRET"]:
        return "*" * len(value)
        
    # Generic fallback mask: show first 20%, mask next 60%, show last 20%
    length = len(value)
    if length <= 4:
        return "*" * length
    
    visible = max(1, length // 5)
    return value[:visible] + "*" * (length - (visible * 2)) + value[-visible:]


from typing import List, Dict, Any, Tuple

def remove_overlapping_spans(raw_findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Takes a list of dictionaries that must contain 'start' and 'end' keys.
    Sorts them by span length (descending) and removes any findings that overlap
    with already accepted longer findings.
    
    Args:
        raw_findings: List of raw regex/match findings containing 'start' and 'end' int keys.
        
    Returns:
        List of deduplicated findings (without 'start' and 'end' keys).
    """
    if not raw_findings:
        return []

    # Sort findings by length of span descending, then start index ascending
    raw_findings.sort(key=lambda x: (x["end"] - x["start"]), reverse=True)

    findings: List[Dict[str, Any]] = []
    used_spans: List[Tuple[int, int]] = []
    
    for f in raw_findings:
        start, end = f.get("start"), f.get("end")
        if start is None or end is None:
            # If no start/end provided, just include it
            findings.append(f)
            continue
            
        overlap = False
        for u_start, u_end in used_spans:
            # Check for overlap between [start, end) and [u_start, u_end)
            if max(start, u_start) < min(end, u_end):
                overlap = True
                break
                
        if not overlap:
            used_spans.append((start, end))
            # Create a copy without start/end
            clean_f = {k: v for k, v in f.items() if k not in ("start", "end")}
            findings.append(clean_f)

    return findings



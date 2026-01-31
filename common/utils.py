from typing import List, Dict, Any

def get_centroid_y(bbox: Dict[str, float]) -> float:
    """Calculate vertical centroid of a bbox."""
    return (bbox["y1"] + bbox["y2"]) / 2

def spatial_sort(detections: List[Dict[str, Any]], y_tolerance: int = 10) -> List[Dict[str, Any]]:
    """
    Sorts a list of detections based on reading order (Top-to-Bottom, Left-to-Right).
    
    Args:
        detections: List of dicts, each containing a 'bbox' dict {x1, y1, x2, y2}.
        y_tolerance: Vertical pixels to consider as 'same row'.
        
    Returns:
        Sorted list of methods.
    """
    if not detections:
        return []
        
    # Python's sort is stable. 
    # Primary key: y coordinate (bucketed by tolerance to handle slight misalignments)
    # Secondary key: x coordinate
    
    return sorted(detections, key=lambda d: (
        int(d["bbox"]["y1"] / y_tolerance), # Row bucket
        d["bbox"]["x1"]                     # Column position
    ))

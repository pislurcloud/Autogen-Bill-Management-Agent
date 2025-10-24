"""
JSON Output Formatting
Creates structured output from bill processing results
"""

import json
from datetime import datetime
from typing import Dict, List, Any


def create_final_output(
    bill_data: Dict[str, Any],
    summary_data: Dict[str, Any],
    metadata: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Create final structured JSON output
    
    Args:
        bill_data: Bill processing results
        summary_data: Summary and insights
        metadata: Processing metadata
        
    Returns:
        Complete structured output
    """
    output = {
        "bill_metadata": {
            "bill_id": metadata.get("bill_id"),
            "merchant_name": bill_data.get("merchant_name", "Unknown"),
            "bill_date": bill_data.get("bill_date", "Unknown"),
            "processing_timestamp": datetime.now().isoformat(),
            "image_quality": bill_data.get("quality_assessment", {}).get("overall_quality", "unknown"),
            "overall_confidence": bill_data.get("quality_assessment", {}).get("confidence_score", 0.0),
            "model_used": metadata.get("model_used", "unknown"),
            "fallback_used": metadata.get("fallback_used", False)
        },
        
        "expenses": bill_data.get("line_items", []),
        
        "summary": summary_data.get("summary", {}),
        
        "insights": summary_data.get("insights", {}),
        
        "quality_metrics": {
            **summary_data.get("quality_metrics", {}),
            "image_quality_assessment": bill_data.get("quality_assessment", {})
        },
        
        "metadata": {
            "processing_time_seconds": metadata.get("processing_time", 0.0),
            "model_used": metadata.get("model_used", "unknown"),
            "fallback_used": metadata.get("fallback_used", False),
            "total_items": len(bill_data.get("line_items", []))
        }
    }
    
    return output


def format_for_display(output_data: Dict[str, Any]) -> str:
    """Pretty format JSON for display"""
    return json.dumps(output_data, indent=2, ensure_ascii=False)


def create_csv_export(expenses: List[Dict[str, Any]]) -> str:
    """
    Create CSV string from expenses
    
    Args:
        expenses: List of expense items
        
    Returns:
        CSV formatted string
    """
    import csv
    import io
    
    output = io.StringIO()
    if not expenses:
        return output.getvalue()
    
    writer = csv.DictWriter(
        output,
        fieldnames=['description', 'amount', 'category', 'confidence']
    )
    
    writer.writeheader()
    for expense in expenses:
        writer.writerow({
            'description': expense.get('description', ''),
            'amount': expense.get('amount', 0.0),
            'category': expense.get('category', ''),
            'confidence': expense.get('confidence', 0.0)
        })
    
    return output.getvalue()
"""
Bill Processor - Core Processing Logic
Uses Vision Language Models for bill analysis
"""

import json
from typing import Dict, Any
from datetime import datetime

from src.utils.vlm_provider import ModelManager, extract_json_from_response
from src.utils.image_processor import prepare_image_for_vlm
from src.utils.json_formatter import create_final_output
from src.database.db_manager import DatabaseManager
from src.config.model_config import MIN_CONFIDENCE_SCORE


class BillProcessor:
    """Main bill processing coordinator using VLMs"""
    
    def __init__(self, model_manager: ModelManager, db_manager: DatabaseManager):
        self.model_manager = model_manager
        self.db_manager = db_manager
    
    def process_bill(self, image_path: str) -> Dict[str, Any]:
        """
        Complete bill processing workflow using VLM
        
        Args:
            image_path: Path to bill image
            
        Returns:
            Complete processing results
        """
        try:
            # Step 1: Prepare image for VLM
            print("📸 Preparing image for VLM...")
            processed_image, image_metadata = prepare_image_for_vlm(image_path)
            
            # Step 2: Extract bill data using VLM
            print("🔍 Analyzing bill with VLM...")
            extraction_result = self._extract_bill_data_with_vlm(processed_image)
            
            if not extraction_result['success']:
                return {
                    "success": False,
                    "error": extraction_result['error'],
                    "stage": "vlm_extraction"
                }
            
            bill_data = extraction_result['data']
            
            # Step 3: Check quality
            quality_score = bill_data.get('quality_assessment', {}).get('confidence_score', 0.0)
            
            if quality_score < MIN_CONFIDENCE_SCORE:
                return {
                    "success": False,
                    "error": "Image quality too low. Please upload a clearer image.",
                    "quality_score": quality_score,
                    "stage": "quality_check",
                    "details": bill_data.get('quality_assessment', {})
                }
            
            # Step 4: Generate summary using VLM
            print("📊 Generating insights with VLM...")
            summary_result = self._generate_summary_with_vlm(bill_data)
            
            if not summary_result['success']:
                return {
                    "success": False,
                    "error": summary_result['error'],
                    "stage": "summary_generation"
                }
            
            summary_data = summary_result['data']
            
            # Step 5: Create metadata
            processing_metadata = {
                "model_used": extraction_result.get('model_used'),
                "fallback_used": extraction_result.get('fallback_used', False),
                "processing_time": (
                    extraction_result.get('processing_time', 0) +
                    summary_result.get('processing_time', 0)
                )
            }
            
            # Step 6: Save to database
            print("💾 Saving to database...")
            bill_id = self._save_to_database(bill_data, image_path, processing_metadata)
            processing_metadata["bill_id"] = bill_id
            
            # Step 7: Create final output
            final_output = create_final_output(bill_data, summary_data, processing_metadata)
            
            print("✅ Processing complete!")
            return {
                "success": True,
                "data": final_output,
                "bill_id": bill_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Processing failed: {str(e)}",
                "stage": "unknown"
            }
    
    def _extract_bill_data_with_vlm(self, image_path: str) -> Dict[str, Any]:
        """Extract bill data using Vision Language Model"""
        
        prompt = """Analyze this bill/receipt image and extract all information in JSON format.

You MUST extract:
1. Merchant/vendor name
2. Date in YYYY-MM-DD format
3. All line items with descriptions and prices
4. Total amount
5. Categorize each item into one of: groceries, dining, utilities, shopping, entertainment, or uncategorized

Also assess the image quality:
- Is text clear and readable?
- Is information complete?
- Provide confidence score (0.0 to 1.0)

Respond ONLY with valid JSON in this exact format:
{
    "merchant_name": "store name",
    "bill_date": "YYYY-MM-DD",
    "quality_assessment": {
        "is_clear": true,
        "is_complete": true,
        "overall_quality": "excellent",
        "confidence_score": 0.95,
        "issues": []
    },
    "line_items": [
        {
            "description": "item name",
            "amount": 12.50,
            "category": "groceries",
            "confidence": 0.90
        }
    ],
    "total_amount": 12.50,
    "currency": "USD"
}"""
        
        result = self.model_manager.analyze_image_with_fallback(image_path, prompt)
        
        if not result['success']:
            return result
        
        try:
            bill_data = extract_json_from_response(result['response'])
            
            return {
                "success": True,
                "data": bill_data,
                "model_used": result['model_used'],
                "fallback_used": result['fallback_used'],
                "processing_time": result['processing_time']
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse VLM response: {str(e)}",
                "raw_response": result['response']
            }
    
    def _generate_summary_with_vlm(self, bill_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary and insights using VLM"""
        
        expenses_json = json.dumps(bill_data.get('line_items', []), indent=2)
        
        prompt = f"""Analyze these expenses and provide insights in JSON format.

Expenses data:
{expenses_json}

Generate:
1. Total spending per category
2. Category percentages
3. Insights about spending patterns
4. Quality metrics

Respond ONLY with valid JSON in this exact format:
{{
    "summary": {{
        "total_amount": 156.49,
        "item_count": 12,
        "category_breakdown": {{
            "groceries": 89.20,
            "dining": 45.00,
            "utilities": 0.00,
            "shopping": 22.29,
            "entertainment": 0.00,
            "uncategorized": 0.00
        }},
        "category_percentages": {{
            "groceries": 57.0,
            "dining": 29.0,
            "utilities": 0.0,
            "shopping": 14.0,
            "entertainment": 0.0,
            "uncategorized": 0.0
        }},
        "highest_spending_category": "groceries",
        "lowest_spending_category": "utilities"
    }},
    "insights": {{
        "primary_insight": "Groceries account for 57% of total spending",
        "spending_patterns": ["Pattern 1", "Pattern 2"],
        "unusual_items": [],
        "recommendations": []
    }},
    "quality_metrics": {{
        "average_confidence": 0.90,
        "items_with_high_confidence": 10,
        "items_with_low_confidence": 2,
        "overall_data_quality": "excellent"
    }}
}}"""
        
        result = self.model_manager.generate_text_with_fallback(prompt)
        
        if not result['success']:
            return result
        
        try:
            summary_data = extract_json_from_response(result['response'])
            
            return {
                "success": True,
                "data": summary_data,
                "processing_time": result['processing_time']
            }
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Failed to parse summary: {str(e)}",
                "raw_response": result['response']
            }
    
    def _save_to_database(
        self,
        bill_data: Dict[str, Any],
        image_path: str,
        metadata: Dict[str, Any]
    ) -> int:
        """Save processed bill to database"""
        
        quality_assessment = bill_data.get('quality_assessment', {})
        
        # Save bill
        bill_id = self.db_manager.save_bill(
            merchant_name=bill_data.get('merchant_name', 'Unknown'),
            bill_date=bill_data.get('bill_date', datetime.now().strftime('%Y-%m-%d')),
            total_amount=float(bill_data.get('total_amount', 0.0)),
            image_path=image_path,
            quality_score=float(quality_assessment.get('confidence_score', 0.0)),
            confidence_score=float(quality_assessment.get('confidence_score', 0.0)),
            model_used=metadata.get('model_used', 'unknown'),
            fallback_used=metadata.get('fallback_used', False),
            processing_time=metadata.get('processing_time', 0.0)
        )
        
        # Save expenses
        expenses = bill_data.get('line_items', [])
        if expenses:
            self.db_manager.save_expenses(bill_id, expenses)
        
        return bill_id
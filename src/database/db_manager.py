"""
Database Manager
Handles all database operations
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from src.config.settings import DB_PATH, PROJECT_ROOT


class DatabaseManager:
    """Manages database operations"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with schema"""
        schema_path = PROJECT_ROOT / "database" / "schema.sql"
        
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        conn = self._get_connection()
        try:
            conn.executescript(schema_sql)
            conn.commit()
        finally:
            conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def save_bill(
        self,
        merchant_name: str,
        bill_date: str,
        total_amount: float,
        image_path: str,
        quality_score: float,
        confidence_score: float,
        model_used: str,
        fallback_used: bool,
        processing_time: float,
        user_id: int = 1
    ) -> int:
        """Save bill to database"""
        conn = self._get_connection()
        try:
            cursor = conn.execute("""
                INSERT INTO bills (
                    user_id, merchant_name, bill_date, total_amount,
                    image_path, quality_score, confidence_score,
                    model_used, fallback_used, processing_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id, merchant_name, bill_date, total_amount,
                image_path, quality_score, confidence_score,
                model_used, fallback_used, processing_time
            ))
            conn.commit()
            return cursor.lastrowid
        finally:
            conn.close()
    
    def save_expenses(self, bill_id: int, expenses: List[Dict[str, Any]]) -> List[int]:
        """Save expenses for a bill"""
        conn = self._get_connection()
        expense_ids = []
        
        try:
            for expense in expenses:
                cursor = conn.execute("""
                    INSERT INTO expenses (
                        bill_id, item_description, amount,
                        category, confidence_score
                    ) VALUES (?, ?, ?, ?, ?)
                """, (
                    bill_id,
                    expense.get('description', ''),
                    expense.get('amount', 0.0),
                    expense.get('category', 'uncategorized'),
                    expense.get('confidence', 0.0)
                ))
                expense_ids.append(cursor.lastrowid)
            
            conn.commit()
            return expense_ids
        finally:
            conn.close()
    
    def get_bill(self, bill_id: int) -> Optional[Dict[str, Any]]:
        """Get bill by ID"""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT * FROM bills WHERE bill_id = ?", (bill_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()
    
    def get_bill_expenses(self, bill_id: int) -> List[Dict[str, Any]]:
        """Get expenses for a bill"""
        conn = self._get_connection()
        try:
            cursor = conn.execute("SELECT * FROM expenses WHERE bill_id = ?", (bill_id,))
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def get_statistics(self, user_id: int = 1) -> Dict[str, Any]:
        """Get user statistics"""
        conn = self._get_connection()
        try:
            # Total bills
            cursor = conn.execute("SELECT COUNT(*) as count FROM bills WHERE user_id = ?", (user_id,))
            total_bills = cursor.fetchone()['count']
            
            # Total spent
            cursor = conn.execute("SELECT SUM(total_amount) as total FROM bills WHERE user_id = ?", (user_id,))
            total_spent = cursor.fetchone()['total'] or 0.0
            
            # Average
            avg_bill = total_spent / total_bills if total_bills > 0 else 0.0
            
            return {
                "total_bills": total_bills,
                "total_spent": float(total_spent),
                "average_bill": float(avg_bill)
            }
        finally:
            conn.close()
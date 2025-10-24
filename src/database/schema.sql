-- Bill Management Agent Database Schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Bills table
CREATE TABLE IF NOT EXISTS bills (
    bill_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER DEFAULT 1,
    merchant_name TEXT,
    bill_date DATE,
    total_amount DECIMAL(10, 2),
    currency TEXT DEFAULT 'USD',
    image_path TEXT,
    quality_score DECIMAL(3, 2),
    confidence_score DECIMAL(3, 2),
    model_used TEXT,
    fallback_used BOOLEAN DEFAULT 0,
    processing_time REAL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Expenses table
CREATE TABLE IF NOT EXISTS expenses (
    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
    bill_id INTEGER NOT NULL,
    item_description TEXT,
    amount DECIMAL(10, 2),
    category TEXT CHECK(category IN ('groceries', 'dining', 'utilities', 'shopping', 'entertainment', 'uncategorized')),
    confidence_score DECIMAL(3, 2),
    FOREIGN KEY (bill_id) REFERENCES bills(bill_id) ON DELETE CASCADE
);

-- User corrections table
CREATE TABLE IF NOT EXISTS user_corrections (
    correction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_id INTEGER NOT NULL,
    original_category TEXT,
    corrected_category TEXT,
    corrected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (expense_id) REFERENCES expenses(expense_id) ON DELETE CASCADE
);

-- Category patterns table
CREATE TABLE IF NOT EXISTS category_patterns (
    pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL,
    category TEXT NOT NULL,
    confidence DECIMAL(3, 2) DEFAULT 0.5,
    times_used INTEGER DEFAULT 1,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(keyword, category)
);

-- Insert default user
INSERT OR IGNORE INTO users (user_id, username) VALUES (1, 'default_user');

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_bills_user_id ON bills(user_id);
CREATE INDEX IF NOT EXISTS idx_bills_date ON bills(bill_date);
CREATE INDEX IF NOT EXISTS idx_expenses_bill_id ON expenses(bill_id);
CREATE INDEX IF NOT EXISTS idx_expenses_category ON expenses(category);
CREATE INDEX IF NOT EXISTS idx_patterns_keyword ON category_patterns(keyword);
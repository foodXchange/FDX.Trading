"""
Error Tracking Model
Handles storage and management of website errors
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json
import logging

logger = logging.getLogger(__name__)


class ErrorTracking:
    """Model for tracking and managing website errors"""
    
    def __init__(self, db_path: str = 'foodxchange.db'):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the error tracking table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_id VARCHAR(100) NOT NULL,
                    request_id VARCHAR(100),
                    user_id INTEGER,
                    error_type VARCHAR(100) NOT NULL,
                    error_message TEXT NOT NULL,
                    stack_trace TEXT,
                    severity VARCHAR(8) DEFAULT 'medium',
                    category VARCHAR(19) DEFAULT 'general',
                    url_path VARCHAR(500),
                    http_method VARCHAR(10),
                    status_code INTEGER,
                    browser_info JSON,
                    device_info JSON,
                    request_data JSON,
                    response_data JSON,
                    context_data JSON,
                    ticket_id INTEGER,
                    resolved BOOLEAN DEFAULT FALSE,
                    resolved_at DATETIME,
                    resolved_by INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    CHECK (severity IN ('critical', 'high', 'medium', 'low'))
                )
            """)
            
            # Commit table creation first
            conn.commit()
            
            # Create indexes after table is committed
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_error_created_at 
                    ON error_logs(created_at DESC)
                """)
                conn.commit()
            except Exception as e:
                logger.warning(f"Could not create created_at index: {e}")
            
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_error_resolved 
                    ON error_logs(resolved)
                """)
                conn.commit()
            except Exception as e:
                logger.warning(f"Could not create resolved index: {e}")
            
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_error_url_path 
                    ON error_logs(url_path)
                """)
                conn.commit()
            except Exception as e:
                logger.warning(f"Could not create url_path index: {e}")
            
            conn.close()
            logger.info("Error tracking database initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize error tracking database: {e}")
    
    def log_error(self, 
                  url_path: str,
                  error_message: str,
                  stack_trace: str = None,
                  user_id: int = None,
                  severity: str = 'medium',
                  browser_info: dict = None,
                  device_info: dict = None,
                  request_data: dict = None,
                  response_data: dict = None,
                  context_data: dict = None,
                  request_id: str = None,
                  error_type: str = 'general',
                  http_method: str = None,
                  status_code: int = None) -> int:
        """Log a new error to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generate unique error ID
            import uuid
            error_id = str(uuid.uuid4())
            
            cursor.execute("""
                INSERT INTO error_logs 
                (error_id, url_path, error_message, stack_trace, user_id, 
                 severity, browser_info, device_info, request_data, response_data, 
                 context_data, request_id, error_type, http_method, status_code)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                error_id,
                url_path,
                error_message,
                stack_trace,
                user_id,
                severity,
                json.dumps(browser_info) if browser_info else None,
                json.dumps(device_info) if device_info else None,
                json.dumps(request_data) if request_data else None,
                json.dumps(response_data) if response_data else None,
                json.dumps(context_data) if context_data else None,
                request_id,
                error_type,
                http_method,
                status_code
            ))
            
            error_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"Error logged with ID: {error_id}")
            return error_id
            
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
            return -1
    
    def get_errors(self, 
                   status: str = None,
                   severity: str = None,
                   page: str = None,
                   date_from: str = None,
                   limit: int = 100,
                   offset: int = 0) -> List[Dict]:
        """Get errors with optional filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM error_logs WHERE 1=1"
            params = []
            
            if status:
                query += " AND status = ?"
                params.append(status)
            
            if severity:
                query += " AND severity = ?"
                params.append(severity)
            
            if page:
                query += " AND page = ?"
                params.append(page)
            
            if date_from:
                query += " AND timestamp >= ?"
                params.append(date_from)
            
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            errors = []
            
            for row in cursor.fetchall():
                error = dict(row)
                if error.get('additional_data'):
                    try:
                        error['additional_data'] = json.loads(error['additional_data'])
                    except:
                        pass
                errors.append(error)
            
            conn.close()
            return errors
            
        except Exception as e:
            logger.error(f"Failed to get errors: {e}")
            return []
    
    def get_error_by_id(self, error_id: int) -> Optional[Dict]:
        """Get a specific error by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM error_logs WHERE id = ?", (error_id,))
            row = cursor.fetchone()
            
            if row:
                error = dict(row)
                if error.get('additional_data'):
                    try:
                        error['additional_data'] = json.loads(error['additional_data'])
                    except:
                        pass
                conn.close()
                return error
            
            conn.close()
            return None
            
        except Exception as e:
            logger.error(f"Failed to get error by ID: {e}")
            return None
    
    def update_status(self, error_id: int, status: str, user_email: str = None) -> bool:
        """Update the status of an error"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if status == 'solved':
                cursor.execute("""
                    UPDATE error_logs 
                    SET status = ?, resolved_at = CURRENT_TIMESTAMP, resolved_by = ?
                    WHERE id = ?
                """, (status, user_email, error_id))
            else:
                cursor.execute("""
                    UPDATE error_logs 
                    SET status = ?
                    WHERE id = ?
                """, (status, error_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to update error status: {e}")
            return False
    
    def add_note(self, error_id: int, note: str) -> bool:
        """Add a note to an error"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE error_logs 
                SET notes = CASE 
                    WHEN notes IS NULL THEN ?
                    ELSE notes || '\n' || ?
                END
                WHERE id = ?
            """, (note, note, error_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to add note: {e}")
            return False
    
    def delete_error(self, error_id: int) -> bool:
        """Delete an error from the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM error_logs WHERE id = ?", (error_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete error: {e}")
            return False
    
    def get_statistics(self) -> Dict:
        """Get error statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Count by status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM error_logs 
                GROUP BY status
            """)
            status_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Count by severity
            cursor.execute("""
                SELECT severity, COUNT(*) as count 
                FROM error_logs 
                GROUP BY severity
            """)
            severity_counts = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Most error-prone pages
            cursor.execute("""
                SELECT page, COUNT(*) as count 
                FROM error_logs 
                GROUP BY page 
                ORDER BY count DESC 
                LIMIT 5
            """)
            top_pages = [{'page': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            # Total errors
            cursor.execute("SELECT COUNT(*) FROM error_logs")
            total = cursor.fetchone()[0]
            
            # Recent errors (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM error_logs 
                WHERE timestamp >= datetime('now', '-1 day')
            """)
            recent = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total': total,
                'recent_24h': recent,
                'by_status': status_counts,
                'by_severity': severity_counts,
                'top_pages': top_pages
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {
                'total': 0,
                'recent_24h': 0,
                'by_status': {},
                'by_severity': {},
                'top_pages': []
            }
    
    def cleanup_old_errors(self, days: int = 30) -> int:
        """Clean up resolved errors older than specified days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM error_logs 
                WHERE status = 'solved' 
                AND resolved_at < datetime('now', '-{} days')
            """.format(days))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            logger.info(f"Cleaned up {deleted} old resolved errors")
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to cleanup old errors: {e}")
            return 0


# Global instance
error_tracker = ErrorTracking()
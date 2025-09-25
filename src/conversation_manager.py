"""Conversation management for persisting and loading chat sessions."""

import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
from loguru import logger

from .agent import ConversationMessage, AgentSession


class ConversationManager:
    """Manages conversation persistence and loading."""
    
    def __init__(self, sessions_dir: str = "sessions"):
        """
        Initialize conversation manager.
        
        Args:
            sessions_dir: Directory to store session files
        """
        self.sessions_dir = Path(sessions_dir)
        self.sessions_dir.mkdir(exist_ok=True)
        logger.info(f"Conversation manager initialized with sessions directory: {self.sessions_dir}")
    
    def save_session(self, session: AgentSession) -> str:
        """
        Save a session to disk.
        
        Args:
            session: The session to save
            
        Returns:
            Path to the saved session file
        """
        try:
            # Convert session to dictionary
            session_data = {
                "session_id": session.session_id,
                "created_at": session.created_at.isoformat(),
                "messages": [],
                "context_cache": session.context_cache
            }
            
            # Convert messages
            for msg in session.messages:
                msg_data = {
                    "timestamp": msg.timestamp.isoformat(),
                    "role": msg.role,
                    "content": msg.content,
                    "query": msg.query,
                    "results": msg.results
                }
                session_data["messages"].append(msg_data)
            
            # Save to file
            filename = f"{session.session_id}.json"
            filepath = self.sessions_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Session saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save session {session.session_id}: {e}")
            raise
    
    def load_session(self, session_id: str) -> Optional[AgentSession]:
        """
        Load a session from disk.
        
        Args:
            session_id: The session ID to load
            
        Returns:
            Loaded session or None if not found
        """
        try:
            filename = f"{session_id}.json"
            filepath = self.sessions_dir / filename
            
            if not filepath.exists():
                logger.warning(f"Session file not found: {filepath}")
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Convert back to session object
            session = AgentSession(
                session_id=session_data["session_id"],
                created_at=datetime.fromisoformat(session_data["created_at"]),
                context_cache=session_data.get("context_cache", {})
            )
            
            # Convert messages
            for msg_data in session_data.get("messages", []):
                message = ConversationMessage(
                    timestamp=datetime.fromisoformat(msg_data["timestamp"]),
                    role=msg_data["role"],
                    content=msg_data["content"],
                    query=msg_data.get("query"),
                    results=msg_data.get("results")
                )
                session.messages.append(message)
            
            logger.info(f"Session loaded: {session_id} ({len(session.messages)} messages)")
            return session
            
        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None
    
    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all available sessions.
        
        Returns:
            List of session metadata
        """
        sessions = []
        
        try:
            for filepath in self.sessions_dir.glob("*.json"):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        session_data = json.load(f)
                    
                    sessions.append({
                        "session_id": session_data["session_id"],
                        "created_at": session_data["created_at"],
                        "message_count": len(session_data.get("messages", [])),
                        "file_path": str(filepath)
                    })
                except Exception as e:
                    logger.warning(f"Failed to read session file {filepath}: {e}")
                    continue
            
            # Sort by creation date (newest first)
            sessions.sort(key=lambda x: x["created_at"], reverse=True)
            
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
        
        return sessions
    
    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session file.
        
        Args:
            session_id: The session ID to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            filename = f"{session_id}.json"
            filepath = self.sessions_dir / filename
            
            if filepath.exists():
                filepath.unlink()
                logger.info(f"Session deleted: {session_id}")
                return True
            else:
                logger.warning(f"Session file not found: {filepath}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            return False
    
    def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """
        Clean up sessions older than specified days.
        
        Args:
            days_old: Number of days after which sessions should be cleaned up
            
        Returns:
            Number of sessions cleaned up
        """
        cleaned_count = 0
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        
        try:
            for filepath in self.sessions_dir.glob("*.json"):
                try:
                    file_mtime = filepath.stat().st_mtime
                    if file_mtime < cutoff_date:
                        filepath.unlink()
                        cleaned_count += 1
                        logger.info(f"Cleaned up old session: {filepath.name}")
                except Exception as e:
                    logger.warning(f"Failed to clean up session file {filepath}: {e}")
                    continue
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old sessions")
            
        except Exception as e:
            logger.error(f"Failed to cleanup old sessions: {e}")
        
        return cleaned_count
    
    def export_session(self, session_id: str, format: str = "json") -> Optional[str]:
        """
        Export a session to different formats.
        
        Args:
            session_id: The session ID to export
            format: Export format ('json', 'txt', 'csv')
            
        Returns:
            Path to exported file or None if failed
        """
        session = self.load_session(session_id)
        if not session:
            return None
        
        try:
            export_dir = self.sessions_dir / "exports"
            export_dir.mkdir(exist_ok=True)
            
            if format == "json":
                # JSON format (same as save_session)
                return self.save_session(session)
            
            elif format == "txt":
                # Plain text format
                filename = f"{session_id}_export.txt"
                filepath = export_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(f"Session: {session.session_id}\n")
                    f.write(f"Created: {session.created_at}\n")
                    f.write(f"Messages: {len(session.messages)}\n")
                    f.write("=" * 80 + "\n\n")
                    
                    for msg in session.messages:
                        f.write(f"[{msg.timestamp}] {msg.role.upper()}:\n")
                        f.write(f"{msg.content}\n")
                        if msg.query:
                            f.write(f"SQL: {msg.query}\n")
                        f.write("-" * 40 + "\n")
                
                return str(filepath)
            
            elif format == "csv":
                # CSV format for analysis
                import csv
                filename = f"{session_id}_export.csv"
                filepath = export_dir / filename
                
                with open(filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["timestamp", "role", "content", "query"])
                    
                    for msg in session.messages:
                        writer.writerow([
                            msg.timestamp.isoformat(),
                            msg.role,
                            msg.content,
                            msg.query or ""
                        ])
                
                return str(filepath)
            
            else:
                logger.error(f"Unsupported export format: {format}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to export session {session_id}: {e}")
            return None


# Global conversation manager instance
conversation_manager = ConversationManager()
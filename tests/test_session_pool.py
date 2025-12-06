"""Test session pool manager"""

import pytest
import time
from unittest.mock import Mock, MagicMock
from src.session_pool import SessionPool, Session


def test_session_creation():
    """Test Session wrapper"""
    mock_page = Mock()
    session = Session("test_id", mock_page)
    
    assert session.session_id == "test_id"
    assert session.page == mock_page
    assert session.is_healthy
    assert session.provider is None
    
    # Test touch
    initial_time = session.last_used
    time.sleep(0.01)
    session.touch()
    assert session.last_used > initial_time


def test_session_age_and_idle():
    """Test session age and idle time tracking"""
    mock_page = Mock()
    session = Session("test_id", mock_page)
    
    time.sleep(0.1)
    
    # Age should be positive
    assert session.age() > 0
    assert session.age() >= 0.1
    
    # Idle time should match age initially
    assert abs(session.idle_time() - session.age()) < 0.01
    
    # After touch, idle should reset
    time.sleep(0.05)
    session.touch()
    assert session.idle_time() < session.age()


def test_session_pool_init():
    """Test SessionPool initialization"""
    pool = SessionPool(max_sessions=5, max_age=1800)
    
    assert pool.max_sessions == 5
    assert pool.max_age == 1800
    assert len(pool.sessions) == 0
    assert pool.anti_detection is not None


@pytest.mark.skip(reason="Requires browser - skipping in CI")
def test_session_allocate():
    """Test session allocation"""
    pool = SessionPool(max_sessions=2)
    
    session1 = pool.allocate(provider="test")
    assert session1 is not None
    assert session1.provider == "test"
    assert len(pool.sessions) == 1
    
    session2 = pool.allocate()
    assert session2 is not None
    assert len(pool.sessions) == 2
    
    # Cleanup
    pool.cleanup_all()


def test_session_pool_exhaustion():
    """Test pool exhaustion handling"""
    # Mock the ChromiumPage to avoid browser requirement
    import src.session_pool
    original_chromium = src.session_pool.ChromiumPage
    src.session_pool.ChromiumPage = Mock
    
    try:
        pool = SessionPool(max_sessions=1)
        
        session1 = pool.allocate()
        assert len(pool.sessions) == 1
        
        # Should raise RuntimeError when exhausted
        with pytest.raises(RuntimeError, match="Pool exhausted"):
            session2 = pool.allocate()
        
        # After release, should work again
        pool.release(session1.session_id)
        assert len(pool.sessions) == 0
        
        session3 = pool.allocate()
        assert len(pool.sessions) == 1
        
        pool.cleanup_all()
    finally:
        src.session_pool.ChromiumPage = original_chromium


def test_session_release():
    """Test session release"""
    import src.session_pool
    original_chromium = src.session_pool.ChromiumPage
    
    # Mock ChromiumPage
    mock_page = Mock()
    mock_chromium = Mock(return_value=mock_page)
    src.session_pool.ChromiumPage = mock_chromium
    
    try:
        pool = SessionPool()
        session = pool.allocate()
        session_id = session.session_id
        
        assert session_id in pool.sessions
        
        pool.release(session_id)
        assert session_id not in pool.sessions
        
        # Verify quit was called
        mock_page.quit.assert_called_once()
    finally:
        src.session_pool.ChromiumPage = original_chromium


def test_get_session():
    """Test getting session by ID"""
    import src.session_pool
    original_chromium = src.session_pool.ChromiumPage
    src.session_pool.ChromiumPage = Mock
    
    try:
        pool = SessionPool()
        session = pool.allocate()
        
        retrieved = pool.get_session(session.session_id)
        assert retrieved == session
        
        # Non-existent session
        assert pool.get_session("fake_id") is None
        
        pool.cleanup_all()
    finally:
        src.session_pool.ChromiumPage = original_chromium


def test_pool_stats():
    """Test pool statistics"""
    import src.session_pool
    original_chromium = src.session_pool.ChromiumPage
    src.session_pool.ChromiumPage = Mock
    
    try:
        pool = SessionPool(max_sessions=5)
        session = pool.allocate(provider="test_provider")
        
        stats = pool.get_stats()
        assert stats["total_sessions"] == 1
        assert stats["max_sessions"] == 5
        assert stats["utilization"] == 0.2  # 1/5
        assert len(stats["sessions"]) == 1
        
        # Check session details
        session_info = stats["sessions"][0]
        assert session_info["id"] == session.session_id
        assert session_info["provider"] == "test_provider"
        assert "age" in session_info
        assert "idle" in session_info
        assert session_info["healthy"] == True
        
        pool.cleanup_all()
    finally:
        src.session_pool.ChromiumPage = original_chromium


def test_cleanup_stale_sessions():
    """Test stale session cleanup"""
    import src.session_pool
    original_chromium = src.session_pool.ChromiumPage
    src.session_pool.ChromiumPage = Mock
    
    try:
        # Use very short max_age for testing
        pool = SessionPool(max_sessions=5, max_age=0.1)
        
        session = pool.allocate()
        assert len(pool.sessions) == 1
        
        # Wait for session to become stale
        time.sleep(0.2)
        
        # Allocate another - should trigger cleanup
        session2 = pool.allocate()
        
        # First session should be cleaned up
        assert session.session_id not in pool.sessions
        assert len(pool.sessions) == 1
        
        pool.cleanup_all()
    finally:
        src.session_pool.ChromiumPage = original_chromium


def test_health_check():
    """Test session health checking"""
    import src.session_pool
    original_chromium = src.session_pool.ChromiumPage
    
    # Mock healthy page
    healthy_page = Mock()
    healthy_page.url = "https://example.com"
    
    # Mock unhealthy page
    unhealthy_page = Mock()
    unhealthy_page.url = Mock(side_effect=Exception("Connection lost"))
    
    try:
        pool = SessionPool()
        
        # Test healthy session
        healthy_session = Session("healthy", healthy_page)
        assert pool.health_check(healthy_session) == True
        assert healthy_session.is_healthy == True
        
        # Test unhealthy session
        unhealthy_session = Session("unhealthy", unhealthy_page)
        assert pool.health_check(unhealthy_session) == False
        assert unhealthy_session.is_healthy == False
        
    finally:
        src.session_pool.ChromiumPage = original_chromium


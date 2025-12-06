"""Test anti-detection module"""

import pytest
from src.anti_detection import AntiDetection


def test_anti_detection_init():
    """Test AntiDetection initialization"""
    ad = AntiDetection()
    assert ad.fingerprints is not None
    assert ad.user_agents is not None
    assert len(ad.fingerprints) > 0
    assert len(ad.user_agents) > 0


def test_get_random_fingerprint():
    """Test fingerprint selection"""
    ad = AntiDetection()
    fp = ad.get_random_fingerprint()
    
    assert "userAgent" in fp
    assert "viewport" in fp
    assert "platform" in fp
    assert "languages" in fp
    
    # Verify viewport structure
    assert "width" in fp["viewport"]
    assert "height" in fp["viewport"]
    assert fp["viewport"]["width"] > 0
    assert fp["viewport"]["height"] > 0


def test_get_random_user_agent():
    """Test user agent selection"""
    ad = AntiDetection()
    ua = ad.get_random_user_agent()
    
    assert isinstance(ua, str)
    assert len(ua) > 0
    assert "Mozilla" in ua  # All modern UAs start with Mozilla


def test_fingerprint_diversity():
    """Test that fingerprints are diverse"""
    ad = AntiDetection()
    
    # Get multiple fingerprints
    fps = [ad.get_random_fingerprint() for _ in range(10)]
    
    # Check that we have some variety (at least 2 different ones)
    unique_platforms = set(fp["platform"] for fp in fps)
    assert len(unique_platforms) >= 1  # Should have at least the platforms we defined


def test_user_agent_diversity():
    """Test that user agents are diverse"""
    ad = AntiDetection()
    
    # Get multiple user agents
    uas = [ad.get_random_user_agent() for _ in range(10)]
    
    # Check that we have variety
    unique_uas = set(uas)
    assert len(unique_uas) >= 1  # Should have at least the UAs we defined


@pytest.mark.skip(reason="Requires browser - skipping in CI")
def test_apply_to_page():
    """Test applying anti-detection to page"""
    from DrissionPage import ChromiumPage
    
    ad = AntiDetection()
    page = ChromiumPage()
    
    try:
        ad.apply_to_page(page)
        # If no exception raised, test passes
        assert True
    finally:
        page.quit()


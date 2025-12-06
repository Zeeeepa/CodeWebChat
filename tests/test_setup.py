"""Test basic setup and dependencies"""

import pytest
import sys


def test_python_version():
    """Test Python version >= 3.11"""
    assert sys.version_info >= (3, 11), "Python 3.11+ required"


def test_drissionpage_import():
    """Test DrissionPage can be imported"""
    try:
        from DrissionPage import ChromiumPage
        assert ChromiumPage is not None
    except ImportError as e:
        pytest.fail(f"Failed to import DrissionPage: {e}")


def test_fastapi_import():
    """Test FastAPI can be imported"""
    try:
        from fastapi import FastAPI
        assert FastAPI is not None
    except ImportError as e:
        pytest.fail(f"Failed to import FastAPI: {e}")


def test_pydantic_import():
    """Test Pydantic can be imported"""
    try:
        from pydantic import BaseModel
        assert BaseModel is not None
    except ImportError as e:
        pytest.fail(f"Failed to import Pydantic: {e}")


@pytest.mark.skip(reason="Skipping browser test - requires display")
def test_drissionpage_basic():
    """Test basic DrissionPage functionality"""
    from DrissionPage import ChromiumPage
    
    page = ChromiumPage()
    assert page is not None
    page.quit()


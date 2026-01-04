#!/usr/bin/env python
"""
Test script to verify FixMe platform functionality.
This script tests key features of the application.
"""
import requests
import json
import sys

BASE_URL = 'http://localhost:5000'

def test_main_page():
    """Test that the main page loads."""
    print("Testing main page...")
    response = requests.get(BASE_URL)
    assert response.status_code == 200, "Main page failed to load"
    assert 'FixMe' in response.text, "Main page missing title"
    print("✓ Main page loads successfully")

def test_api_projects():
    """Test the projects API endpoint."""
    print("\nTesting projects API...")
    response = requests.get(f'{BASE_URL}/api/projects')
    assert response.status_code == 200, "Projects API failed"
    projects = response.json()
    assert len(projects) > 0, "No projects found"
    assert projects[0]['name'] == 'Fix My Art', "Default project not found"
    print(f"✓ Found {len(projects)} project(s)")
    print(f"  - {projects[0]['name']} ({projects[0]['width']}x{projects[0]['height']})")

def test_api_current_state():
    """Test the current state API endpoint."""
    print("\nTesting current state API...")
    response = requests.get(f'{BASE_URL}/api/projects/1/current-state')
    assert response.status_code == 200, "Current state API failed"
    data = response.json()
    assert 'project' in data, "Missing project data"
    assert 'pixels' in data, "Missing pixels data"
    print(f"✓ Current state retrieved: {len(data['pixels'])} pixels")

def test_admin_panel():
    """Test that admin panel loads with authentication."""
    print("\nTesting admin panel...")
    response = requests.get(f'{BASE_URL}/admin?user=admin&pass=admin123')
    assert response.status_code == 200, "Admin panel failed to load"
    assert 'Admin Panel' in response.text, "Admin panel missing title"
    print("✓ Admin panel loads successfully")

def test_admin_unauthorized():
    """Test that admin panel rejects unauthorized access."""
    print("\nTesting admin panel security...")
    response = requests.get(f'{BASE_URL}/admin?user=wrong&pass=wrong')
    assert response.status_code == 401, "Admin panel should reject wrong credentials"
    print("✓ Admin panel properly rejects unauthorized access")

def test_create_project():
    """Test creating a new project."""
    print("\nTesting project creation...")
    project_data = {
        'name': 'Test Project',
        'description': 'A test project',
        'width': 50,
        'height': 50
    }
    response = requests.post(
        f'{BASE_URL}/api/projects',
        json=project_data,
        headers={'Content-Type': 'application/json'}
    )
    assert response.status_code == 201, "Failed to create project"
    project = response.json()
    assert project['name'] == 'Test Project', "Project name mismatch"
    assert project['width'] == 50, "Project width mismatch"
    print(f"✓ Created project: {project['name']}")

def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("FixMe Platform Test Suite")
    print("=" * 60)
    
    try:
        test_main_page()
        test_api_projects()
        test_api_current_state()
        test_admin_panel()
        test_admin_unauthorized()
        test_create_project()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(run_all_tests())

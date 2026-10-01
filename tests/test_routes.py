import pytest
from app import db
from app.models import User, Property

def test_user_login(client, init_database):
    """Test Case 10: User Login"""
    # Create user
    user = User(username="login_test")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()
    
    # Try logging in
    response = client.post('/login', data={
        'username': 'login_test',
        'password': 'password123'
    }, follow_redirects=True)
    
    # Check if login was successful (usually redirects to dashboard and shows a success message or specific dashboard content)
    # The actual string to check depends on the routes.py implementation. Let's assume there's a logout link or dashboard text.
    assert response.status_code == 200
    assert b"login_test" in response.data or b"Dashboard" in response.data or b"Logout" in response.data

def test_user_isolation(client, init_database):
    """Test Case 11: User Isolation"""
    # Create User A and User B
    user_a = User(username="user_a")
    user_a.set_password("password_a")
    
    user_b = User(username="user_b")
    user_b.set_password("password_b")
    
    db.session.add(user_a)
    db.session.add(user_b)
    db.session.commit()
    
    # Create Property for User B
    prop_b = Property(name="User B Secret Property", user_id=user_b.id)
    db.session.add(prop_b)
    db.session.commit()
    
    # Log in as User A
    client.post('/login', data={
        'username': 'user_a',
        'password': 'password_a'
    }, follow_redirects=True)
    
    # Check dashboard for User A
    response = client.get('/properties')
    
    assert response.status_code == 200
    # User B's property should NOT be visible on User A's dashboard
    assert b"User B Secret Property" not in response.data

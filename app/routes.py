from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.models import User, Property, Stand
from app.forms import RegistrationForm, LoginForm

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.properties'))
    else:
        return redirect(url_for('main.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@bp.route('/profile')
@login_required
def profile():
    return render_template('profile.html', title='My Profile')

@bp.route('/profile/delete', methods=['POST'])
@login_required
def delete_account():
    user = User.query.get(current_user.id)
    if user:
        logout_user()
        db.session.delete(user)
        db.session.commit()
        flash('Your account and all associated data have been permanently deleted.', 'success')
    return redirect(url_for('main.index'))

# --- Property Routes ---

@bp.route('/properties')
@login_required
def properties():
    user_properties = Property.query.filter_by(user_id=current_user.id).all()
    return render_template('properties.html', title='My Properties', properties=user_properties)

@bp.route('/property/new', methods=['GET', 'POST'])
@login_required
def new_property():
    from app.forms import PropertyForm
    form = PropertyForm()
    if form.validate_on_submit():
        # Handle optional lat/long conversion safely
        lat = float(form.latitude.data) if form.latitude.data else None
        lng = float(form.longitude.data) if form.longitude.data else None
        
        prop = Property(name=form.name.data, latitude=lat, longitude=lng, owner=current_user)
        db.session.add(prop)
        db.session.commit()
        flash('Property added successfully!', 'success')
        return redirect(url_for('main.properties'))
    return render_template('property_form.html', title='New Property', form=form)

@bp.route('/property/<int:property_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    from flask import abort
    prop = Property.query.get_or_404(property_id)
    
    # Security: Ensure only the owner can edit
    if prop.user_id != current_user.id:
        abort(403)
        
    from app.forms import PropertyForm
    form = PropertyForm()
    if form.validate_on_submit():
        prop.name = form.name.data
        prop.latitude = float(form.latitude.data) if form.latitude.data else None
        prop.longitude = float(form.longitude.data) if form.longitude.data else None
        db.session.commit()
        flash('Property updated successfully!', 'success')
        return redirect(url_for('main.properties'))
    elif request.method == 'GET':
        form.name.data = prop.name
        form.latitude.data = prop.latitude if prop.latitude else ''
        form.longitude.data = prop.longitude if prop.longitude else ''
        
    return render_template('property_form.html', title='Edit Property', form=form, property_id=prop.id)

@bp.route('/property/<int:property_id>/delete', methods=['POST'])
@login_required
def delete_property(property_id):
    from flask import abort
    prop = Property.query.get_or_404(property_id)
    
    # Security: Ensure only the owner can delete
    if prop.user_id != current_user.id:
        abort(403)
        
    db.session.delete(prop)
    db.session.commit()
    flash('Property deleted successfully!', 'success')
    return redirect(url_for('main.properties'))

# --- Stand Routes ---

@bp.route('/property/<int:property_id>/stands')
@login_required
def stands(property_id):
    from flask import abort
    from app.weather import WeatherManager

    prop = Property.query.get_or_404(property_id)
    if prop.user_id != current_user.id:
        abort(403)
    
    # Fetch live wind direction based on Property coordinates
    wm = WeatherManager()
    wind_degree = wm.get_wind_direction(prop.latitude, prop.longitude)
    
    # Sort stands by score (highest first). If no wind data, keep original order.
    sorted_stands = list(prop.stands)
    if wind_degree is not None:
        sorted_stands.sort(key=lambda s: s.current_score(wind_degree) if s.current_score(wind_degree) is not None else -1, reverse=True)
    
    return render_template('stands.html', title=f'Stands at {prop.name}', property=prop, wind_degree=wind_degree, sorted_stands=sorted_stands)

@bp.route('/property/<int:property_id>/stand/new', methods=['GET', 'POST'])
@login_required
def new_stand(property_id):
    from flask import abort
    prop = Property.query.get_or_404(property_id)
    if prop.user_id != current_user.id:
        abort(403)

    from app.forms import StandForm
    form = StandForm()
    if form.validate_on_submit():
        stand = Stand(name=form.name.data, degree=form.degree.data, property_id=prop.id)
        db.session.add(stand)
        db.session.commit()
        flash('Stand added successfully!', 'success')
        return redirect(url_for('main.stands', property_id=prop.id))
        
    return render_template('stand_form.html', title=f'New Stand at {prop.name}', form=form, property=prop)

@bp.route('/property/<int:property_id>/stand/<int:stand_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_stand(property_id, stand_id):
    from flask import abort
    prop = Property.query.get_or_404(property_id)
    stand = Stand.query.get_or_404(stand_id)
    
    # Security: Check property ownership and ensure stand belongs to property
    if prop.user_id != current_user.id or stand.property_id != prop.id:
        abort(403)

    from app.forms import StandForm
    form = StandForm()
    if form.validate_on_submit():
        stand.name = form.name.data
        stand.degree = form.degree.data
        db.session.commit()
        flash('Stand updated successfully!', 'success')
        return redirect(url_for('main.stands', property_id=prop.id))
    elif request.method == 'GET':
        form.name.data = stand.name
        form.degree.data = stand.degree

    return render_template('stand_form.html', title='Edit Stand', form=form, property=prop, stand=stand)

@bp.route('/property/<int:property_id>/stand/<int:stand_id>/delete', methods=['POST'])
@login_required
def delete_stand(property_id, stand_id):
    from flask import abort
    prop = Property.query.get_or_404(property_id)
    stand = Stand.query.get_or_404(stand_id)
    
    if prop.user_id != current_user.id or stand.property_id != prop.id:
        abort(403)
        
    db.session.delete(stand)
    db.session.commit()
    flash('Stand deleted successfully!', 'success')
    return redirect(url_for('main.stands', property_id=prop.id))

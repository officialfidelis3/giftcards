import os
import logging
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sheets_service import SheetsService

admin_bp = Blueprint('admin', __name__)
sheets_service = SheetsService()

def admin_required(f):
    """Decorator to require admin login"""
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Admin login page"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple admin authentication (can be enhanced)
        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123')
        
        if username == admin_username and password == admin_password:
            session['admin_logged_in'] = True
            session['admin_username'] = username
            flash('Welcome to the admin dashboard!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid username or password', 'error')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    """Admin logout"""
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """Admin dashboard with overview"""
    try:
        # Get summary statistics
        all_cards = sheets_service.get_all_gift_cards()
        categories = sheets_service.get_categories()
        analytics = sheets_service.get_analytics_data()
        
        stats = {
            'total_gift_cards': len(all_cards),
            'total_categories': len(categories),
            'total_views': analytics.get('total_views', 0),
            'total_clicks': analytics.get('total_clicks', 0)
        }
        
        return render_template('admin/dashboard.html', stats=stats)
    
    except Exception as e:
        logging.error(f"Error loading admin dashboard: {e}")
        flash('Unable to load dashboard data', 'error')
        return render_template('admin/dashboard.html', stats={})

@admin_bp.route('/manage-products', methods=['GET', 'POST'])
@admin_required
def manage_products():
    """Manage gift cards (add, edit, delete)"""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            try:
                gift_card_data = {
                    'name': request.form.get('name'),
                    'brand': request.form.get('brand'),
                    'category': request.form.get('category'),
                    'description': request.form.get('description'),
                    'image_url': request.form.get('image_url'),
                    'values': request.form.get('values'),
                    'affiliate_url': request.form.get('affiliate_url'),
                    'slug': request.form.get('slug'),
                    'popular': 'true' if request.form.get('popular') else 'false',
                    'active': 'true' if request.form.get('active') else 'false'
                }
                
                if sheets_service.add_gift_card(gift_card_data):
                    flash('Gift card added successfully!', 'success')
                else:
                    flash('Failed to add gift card', 'error')
            
            except Exception as e:
                logging.error(f"Error adding gift card: {e}")
                flash('Error adding gift card', 'error')
    
    try:
        # Get all gift cards and categories for the management page
        all_cards = sheets_service.get_all_gift_cards()
        categories = sheets_service.get_categories()
        
        return render_template('admin/manage_products.html', 
                             gift_cards=all_cards, 
                             categories=categories)
    
    except Exception as e:
        logging.error(f"Error loading manage products page: {e}")
        flash('Unable to load products data', 'error')
        return render_template('admin/manage_products.html', 
                             gift_cards=[], 
                             categories=[])

@admin_bp.route('/analytics')
@admin_required
def analytics():
    """View analytics and performance data"""
    try:
        analytics_data = sheets_service.get_analytics_data()
        return render_template('admin/analytics.html', analytics=analytics_data)
    
    except Exception as e:
        logging.error(f"Error loading analytics: {e}")
        flash('Unable to load analytics data', 'error')
        return render_template('admin/analytics.html', analytics={})

import os
import logging
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from datetime import datetime
from sheets_service import SheetsService
from admin_routes import admin_bp
from urllib.parse import quote_plus

# Configure logging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Initialize Google Sheets service
sheets_service = SheetsService()

# Register admin blueprint
app.register_blueprint(admin_bp, url_prefix='/admin')

@app.route('/')
def index():
    """Homepage with hero section and popular brands"""
    try:
        # Get popular gift cards for hero section
        popular_cards = sheets_service.get_popular_gift_cards(limit=8)
        categories = sheets_service.get_categories()
        
        return render_template('index.html', 
                             popular_cards=popular_cards, 
                             categories=categories)
    except Exception as e:
        logging.error(f"Error loading homepage: {e}")
        return render_template('index.html', 
                             popular_cards=[], 
                             categories=[],
                             error="Unable to load gift cards at the moment")

@app.route('/categories')
def categories():
    """Display all gift card categories"""
    try:
        all_categories = sheets_service.get_categories_with_cards()
        return render_template('categories.html', categories=all_categories)
    except Exception as e:
        logging.error(f"Error loading categories: {e}")
        return render_template('categories.html', 
                             categories=[],
                             error="Unable to load categories at the moment")

@app.route('/category/<category_name>')
def category_detail(category_name):
    """Display gift cards in a specific category"""
    try:
        gift_cards = sheets_service.get_gift_cards_by_category(category_name)
        return render_template('categories.html', 
                             gift_cards=gift_cards,
                             current_category=category_name)
    except Exception as e:
        logging.error(f"Error loading category {category_name}: {e}")
        return render_template('categories.html', 
                             gift_cards=[],
                             current_category=category_name,
                             error=f"Unable to load {category_name} gift cards")

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Display detailed information about a specific gift card"""
    try:
        gift_card = sheets_service.get_gift_card_by_id(product_id)
        if not gift_card:
            flash('Gift card not found', 'error')
            return redirect(url_for('categories'))
        
        # Track product view for analytics
        sheets_service.track_product_view(product_id)
        
        return render_template('product.html', gift_card=gift_card)
    except Exception as e:
        logging.error(f"Error loading product {product_id}: {e}")
        flash('Unable to load gift card details', 'error')
        return redirect(url_for('categories'))

@app.route('/search')
def search():
    """Search for gift cards by name or category"""
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('categories'))
    
    try:
        search_results = sheets_service.search_gift_cards(query)
        return render_template('categories.html', 
                             gift_cards=search_results,
                             search_query=query)
    except Exception as e:
        logging.error(f"Error searching for '{query}': {e}")
        return render_template('categories.html', 
                             gift_cards=[],
                             search_query=query,
                             error="Search is currently unavailable")

@app.route('/affiliate-redirect/<int:product_id>')
def affiliate_redirect(product_id):
    """Handle affiliate link clicks and redirect to GiftCards.com"""
    try:
        gift_card = sheets_service.get_gift_card_by_id(product_id)
        if not gift_card:
            flash('Gift card not found', 'error')
            return redirect(url_for('categories'))
        
        # Track affiliate click for analytics
        sheets_service.track_affiliate_click(product_id)
        
        # Construct affiliate URL (replace with actual affiliate parameters)
        affiliate_id = os.environ.get('GIFTCARDS_AFFILIATE_ID', 'your-affiliate-id')
        base_url = "https://www.giftcards.com/gift-cards/"
        
        # Create affiliate URL with tracking parameters
        affiliate_url = f"{base_url}{gift_card['slug']}?ref={affiliate_id}&utm_source=affiliate&utm_medium=website&utm_campaign=giftcard-{product_id}"
        
        return redirect(affiliate_url)
    except Exception as e:
        logging.error(f"Error processing affiliate redirect for product {product_id}: {e}")
        flash('Unable to process purchase request', 'error')
        return redirect(url_for('categories'))

@app.route('/about')
def about():
    """About Us page"""
    return render_template('about.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact Us page with form handling"""
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            subject = request.form.get('subject')
            message = request.form.get('message')
            
            # Save contact form submission to Google Sheets
            sheets_service.save_contact_form(name, email, subject, message)
            
            flash('Thank you for your message! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))
        except Exception as e:
            logging.error(f"Error saving contact form: {e}")
            flash('Unable to send your message. Please try again later.', 'error')
    
    return render_template('contact.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

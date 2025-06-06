import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
import gspread
from google.oauth2.service_account import Credentials

class SheetsService:
    """Service class for Google Sheets database operations"""
    
    def __init__(self):
        self.gc = None
        self.spreadsheet = None
        self._initialize_sheets()
    
    def _initialize_sheets(self):
        """Initialize Google Sheets connection"""
        try:
            # Get service account credentials from environment
            service_account_info = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
            if service_account_info:
                # Parse JSON credentials
                credentials_dict = json.loads(service_account_info)
                credentials = Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=[
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                )
            else:
                # Fallback to service account file
                credentials = Credentials.from_service_account_file(
                    'service-account.json',
                    scopes=[
                        'https://www.googleapis.com/auth/spreadsheets',
                        'https://www.googleapis.com/auth/drive'
                    ]
                )
            
            self.gc = gspread.authorize(credentials)
            
            # Open or create the main spreadsheet
            spreadsheet_id = os.environ.get('GOOGLE_SHEETS_ID')
            if spreadsheet_id:
                self.spreadsheet = self.gc.open_by_key(spreadsheet_id)
            else:
                # Create new spreadsheet if none specified
                self.spreadsheet = self.gc.create('GiftCard Affiliate Database')
                logging.info(f"Created new spreadsheet: {self.spreadsheet.url}")
            
            # Initialize worksheets
            self._initialize_worksheets()
            
        except Exception as e:
            logging.error(f"Failed to initialize Google Sheets: {e}")
            self.gc = None
            self.spreadsheet = None
    
    def _initialize_worksheets(self):
        """Create necessary worksheets if they don't exist"""
        try:
            worksheets = {
                'gift_cards': [
                    'ID', 'Name', 'Brand', 'Category', 'Description', 'Image_URL', 
                    'Values', 'Affiliate_URL', 'Slug', 'Popular', 'Active', 'Created_Date'
                ],
                'categories': [
                    'ID', 'Name', 'Description', 'Image_URL', 'Active', 'Created_Date'
                ],
                'analytics': [
                    'Date', 'Product_ID', 'Event_Type', 'Count', 'Additional_Data'
                ],
                'contacts': [
                    'Date', 'Name', 'Email', 'Subject', 'Message', 'Status'
                ],
                'admin_users': [
                    'ID', 'Username', 'Password_Hash', 'Email', 'Active', 'Last_Login'
                ]
            }
            
            existing_worksheets = [ws.title for ws in self.spreadsheet.worksheets()]
            
            for sheet_name, headers in worksheets.items():
                if sheet_name not in existing_worksheets:
                    worksheet = self.spreadsheet.add_worksheet(title=sheet_name, rows=1000, cols=len(headers))
                    worksheet.insert_row(headers, 1)
                    logging.info(f"Created worksheet: {sheet_name}")
        
        except Exception as e:
            logging.error(f"Error initializing worksheets: {e}")
    
    def get_popular_gift_cards(self, limit: int = 8) -> List[Dict]:
        """Get popular gift cards for homepage"""
        try:
            if not self.spreadsheet:
                # Return demo data when Google Sheets is not available
                return self._get_demo_popular_cards()[:limit]
            
            worksheet = self.spreadsheet.worksheet('gift_cards')
            records = worksheet.get_all_records()
            
            # Filter active and popular cards
            popular_cards = [
                record for record in records 
                if str(record.get('Active', '')).lower() == 'true' and 
                   str(record.get('Popular', '')).lower() == 'true'
            ][:limit]
            
            # If no data in sheets, return demo data
            if not popular_cards:
                return self._get_demo_popular_cards()[:limit]
            
            return popular_cards
        
        except Exception as e:
            logging.error(f"Error getting popular gift cards: {e}")
            return self._get_demo_popular_cards()[:limit]
    
    def get_categories(self) -> List[Dict]:
        """Get all active categories"""
        try:
            if not self.spreadsheet:
                return self._get_demo_categories()
            
            worksheet = self.spreadsheet.worksheet('categories')
            records = worksheet.get_all_records()
            
            # Filter active categories
            active_categories = [
                record for record in records 
                if str(record.get('Active', '')).lower() == 'true'
            ]
            
            if not active_categories:
                return self._get_demo_categories()
            
            return active_categories
        
        except Exception as e:
            logging.error(f"Error getting categories: {e}")
            return self._get_demo_categories()
    
    def get_categories_with_cards(self) -> List[Dict]:
        """Get categories with their associated gift cards"""
        try:
            categories = self.get_categories()
            gift_cards = self.get_all_gift_cards()
            
            # Group gift cards by category
            for category in categories:
                category['gift_cards'] = [
                    card for card in gift_cards 
                    if card.get('Category') == category.get('Name')
                ]
            
            return categories
        
        except Exception as e:
            logging.error(f"Error getting categories with cards: {e}")
            return []
    
    def get_all_gift_cards(self) -> List[Dict]:
        """Get all active gift cards"""
        try:
            if not self.spreadsheet:
                return self._get_demo_popular_cards()
            
            worksheet = self.spreadsheet.worksheet('gift_cards')
            records = worksheet.get_all_records()
            
            # Filter active cards
            active_cards = [
                record for record in records 
                if str(record.get('Active', '')).lower() == 'true'
            ]
            
            if not active_cards:
                return self._get_demo_popular_cards()
            
            return active_cards
        
        except Exception as e:
            logging.error(f"Error getting all gift cards: {e}")
            return self._get_demo_popular_cards()
    
    def get_gift_cards_by_category(self, category_name: str) -> List[Dict]:
        """Get gift cards in a specific category"""
        try:
            all_cards = self.get_all_gift_cards()
            category_cards = [
                card for card in all_cards 
                if card.get('Category', '').lower() == category_name.lower()
            ]
            
            return category_cards
        
        except Exception as e:
            logging.error(f"Error getting gift cards by category {category_name}: {e}")
            return []
    
    def get_gift_card_by_id(self, product_id: int) -> Optional[Dict]:
        """Get a specific gift card by ID"""
        try:
            all_cards = self.get_all_gift_cards()
            for card in all_cards:
                if str(card.get('ID')) == str(product_id):
                    return card
            
            return None
        
        except Exception as e:
            logging.error(f"Error getting gift card by ID {product_id}: {e}")
            return None
    
    def search_gift_cards(self, query: str) -> List[Dict]:
        """Search gift cards by name, brand, or category"""
        try:
            all_cards = self.get_all_gift_cards()
            query_lower = query.lower()
            
            matching_cards = [
                card for card in all_cards
                if (query_lower in card.get('Name', '').lower() or
                    query_lower in card.get('Brand', '').lower() or
                    query_lower in card.get('Category', '').lower() or
                    query_lower in card.get('Description', '').lower())
            ]
            
            return matching_cards
        
        except Exception as e:
            logging.error(f"Error searching gift cards for '{query}': {e}")
            return []
    
    def track_product_view(self, product_id: int):
        """Track product page view for analytics"""
        try:
            if not self.spreadsheet:
                return
            
            worksheet = self.spreadsheet.worksheet('analytics')
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            worksheet.append_row([
                current_date,
                product_id,
                'product_view',
                1,
                ''
            ])
        
        except Exception as e:
            logging.error(f"Error tracking product view for {product_id}: {e}")
    
    def track_affiliate_click(self, product_id: int):
        """Track affiliate link click for analytics"""
        try:
            if not self.spreadsheet:
                return
            
            worksheet = self.spreadsheet.worksheet('analytics')
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            worksheet.append_row([
                current_date,
                product_id,
                'affiliate_click',
                1,
                ''
            ])
        
        except Exception as e:
            logging.error(f"Error tracking affiliate click for {product_id}: {e}")
    
    def save_contact_form(self, name: str, email: str, subject: str, message: str):
        """Save contact form submission"""
        try:
            if not self.spreadsheet:
                return
            
            worksheet = self.spreadsheet.worksheet('contacts')
            current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            worksheet.append_row([
                current_date,
                name,
                email,
                subject,
                message,
                'new'
            ])
        
        except Exception as e:
            logging.error(f"Error saving contact form: {e}")
    
    def add_gift_card(self, gift_card_data: Dict) -> bool:
        """Add a new gift card (admin function)"""
        try:
            if not self.spreadsheet:
                return False
            
            worksheet = self.spreadsheet.worksheet('gift_cards')
            current_date = datetime.now().strftime('%Y-%m-%d')
            
            # Get next ID
            records = worksheet.get_all_records()
            next_id = max([int(r.get('ID', 0)) for r in records], default=0) + 1
            
            row_data = [
                next_id,
                gift_card_data.get('name', ''),
                gift_card_data.get('brand', ''),
                gift_card_data.get('category', ''),
                gift_card_data.get('description', ''),
                gift_card_data.get('image_url', ''),
                gift_card_data.get('values', ''),
                gift_card_data.get('affiliate_url', ''),
                gift_card_data.get('slug', ''),
                gift_card_data.get('popular', 'false'),
                gift_card_data.get('active', 'true'),
                current_date
            ]
            
            worksheet.append_row(row_data)
            return True
        
        except Exception as e:
            logging.error(f"Error adding gift card: {e}")
            return False
    
    def get_analytics_data(self) -> Dict:
        """Get analytics data for admin dashboard"""
        try:
            if not self.spreadsheet:
                return {}
            
            worksheet = self.spreadsheet.worksheet('analytics')
            records = worksheet.get_all_records()
            
            # Aggregate data
            analytics = {
                'total_views': len([r for r in records if r.get('Event_Type') == 'product_view']),
                'total_clicks': len([r for r in records if r.get('Event_Type') == 'affiliate_click']),
                'recent_activity': records[-20:] if records else []
            }
            
            return analytics
        
        except Exception as e:
            logging.error(f"Error getting analytics data: {e}")
            return {}
    
    def _get_demo_popular_cards(self) -> List[Dict]:
        """Return demo gift card data for development/testing"""
        return [
            {
                'ID': 1,
                'Name': 'Amazon Gift Card',
                'Brand': 'Amazon',
                'Category': 'Online Shopping',
                'Description': 'Shop millions of items on Amazon with this versatile gift card. Perfect for any occasion.',
                'Image_URL': 'https://images.unsplash.com/photo-1523474253046-8cd2748b5fd2?w=400&h=300&fit=crop',
                'Values': '$25, $50, $100, $200',
                'Affiliate_URL': 'https://www.giftcards.com/amazon',
                'Slug': 'amazon-gift-card',
                'Popular': 'true',
                'Active': 'true'
            },
            {
                'ID': 2,
                'Name': 'Starbucks Gift Card',
                'Brand': 'Starbucks',
                'Category': 'Food & Dining',
                'Description': 'Enjoy your favorite coffee, tea, and food at any Starbucks location worldwide.',
                'Image_URL': 'https://images.unsplash.com/photo-1559056199-641a0ac8b55e?w=400&h=300&fit=crop',
                'Values': '$10, $25, $50',
                'Affiliate_URL': 'https://www.giftcards.com/starbucks',
                'Slug': 'starbucks-gift-card',
                'Popular': 'true',
                'Active': 'true'
            },
            {
                'ID': 3,
                'Name': 'Netflix Gift Card',
                'Brand': 'Netflix',
                'Category': 'Entertainment',
                'Description': 'Stream unlimited movies and TV shows with a Netflix subscription gift card.',
                'Image_URL': 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=400&h=300&fit=crop',
                'Values': '$15, $30, $60',
                'Affiliate_URL': 'https://www.giftcards.com/netflix',
                'Slug': 'netflix-gift-card',
                'Popular': 'true',
                'Active': 'true'
            },
            {
                'ID': 4,
                'Name': 'Target Gift Card',
                'Brand': 'Target',
                'Category': 'Retail',
                'Description': 'Shop for everything you need at Target stores or online with this gift card.',
                'Image_URL': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=300&fit=crop',
                'Values': '$25, $50, $100',
                'Affiliate_URL': 'https://www.giftcards.com/target',
                'Slug': 'target-gift-card',
                'Popular': 'true',
                'Active': 'true'
            },
            {
                'ID': 5,
                'Name': 'Steam Gift Card',
                'Brand': 'Steam',
                'Category': 'Gaming',
                'Description': 'Purchase games, software, and in-game content on the Steam platform.',
                'Image_URL': 'https://images.unsplash.com/photo-1552820728-8b83bb6b773f?w=400&h=300&fit=crop',
                'Values': '$20, $50, $100',
                'Affiliate_URL': 'https://www.giftcards.com/steam',
                'Slug': 'steam-gift-card',
                'Popular': 'true',
                'Active': 'true'
            },
            {
                'ID': 6,
                'Name': 'Spotify Gift Card',
                'Brand': 'Spotify',
                'Category': 'Music',
                'Description': 'Listen to millions of songs and podcasts with Spotify Premium.',
                'Image_URL': 'https://images.unsplash.com/photo-1611339555312-e607c8352fd7?w=400&h=300&fit=crop',
                'Values': '$10, $30, $60',
                'Affiliate_URL': 'https://www.giftcards.com/spotify',
                'Slug': 'spotify-gift-card',
                'Popular': 'true',
                'Active': 'true'
            },
            {
                'ID': 7,
                'Name': 'Apple Gift Card',
                'Brand': 'Apple',
                'Category': 'Technology',
                'Description': 'Use for App Store, Apple Music, iCloud, and more Apple services and products.',
                'Image_URL': 'https://images.unsplash.com/photo-1512499617640-c74ae3a79d37?w=400&h=300&fit=crop',
                'Values': '$25, $50, $100',
                'Affiliate_URL': 'https://www.giftcards.com/apple',
                'Slug': 'apple-gift-card',
                'Popular': 'true',
                'Active': 'true'
            },
            {
                'ID': 8,
                'Name': 'Walmart Gift Card',
                'Brand': 'Walmart',
                'Category': 'Retail',
                'Description': 'Shop for groceries, electronics, clothing and more at America\'s largest retailer.',
                'Image_URL': 'https://images.unsplash.com/photo-1563013544-824ae1b704d3?w=400&h=300&fit=crop',
                'Values': '$25, $50, $100, $200',
                'Affiliate_URL': 'https://www.giftcards.com/walmart',
                'Slug': 'walmart-gift-card',
                'Popular': 'true',
                'Active': 'true'
            }
        ]
    
    def _get_demo_categories(self) -> List[Dict]:
        """Return demo category data for development/testing"""
        return [
            {
                'ID': 1,
                'Name': 'Online Shopping',
                'Description': 'Gift cards for popular online retailers and e-commerce platforms',
                'Image_URL': 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=400&h=300&fit=crop',
                'Active': 'true'
            },
            {
                'ID': 2,
                'Name': 'Food & Dining',
                'Description': 'Restaurant and food delivery gift cards for every taste',
                'Image_URL': 'https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=400&h=300&fit=crop',
                'Active': 'true'
            },
            {
                'ID': 3,
                'Name': 'Entertainment',
                'Description': 'Movie, streaming, and entertainment service gift cards',
                'Image_URL': 'https://images.unsplash.com/photo-1489599809927-48ef22504ef8?w=400&h=300&fit=crop',
                'Active': 'true'
            },
            {
                'ID': 4,
                'Name': 'Gaming',
                'Description': 'Gaming platform and in-game purchase gift cards',
                'Image_URL': 'https://images.unsplash.com/photo-1511512578047-dfb367046420?w=400&h=300&fit=crop',
                'Active': 'true'
            },
            {
                'ID': 5,
                'Name': 'Technology',
                'Description': 'Tech and software service gift cards',
                'Image_URL': 'https://images.unsplash.com/photo-1518709268805-4e9042af2176?w=400&h=300&fit=crop',
                'Active': 'true'
            },
            {
                'ID': 6,
                'Name': 'Retail',
                'Description': 'Department store and retail chain gift cards',
                'Image_URL': 'https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=400&h=300&fit=crop',
                'Active': 'true'
            }
        ]

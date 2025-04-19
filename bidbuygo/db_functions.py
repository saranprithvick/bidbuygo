from django.db import connection
from django.db.models import F
from .models import Product, Order, Bidding

def create_database_objects():
    with connection.cursor() as cursor:
        # Function to calculate total order amount
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_totals (
            order_id INTEGER PRIMARY KEY,
            total_amount DECIMAL(10,2)
        );
        """)

        # Function to check product availability
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS product_availability (
            product_id INTEGER PRIMARY KEY,
            is_available BOOLEAN
        );
        """)

        # Function to get auction status
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS auction_status (
            product_id INTEGER PRIMARY KEY,
            status TEXT,
            last_bid_time TIMESTAMP
        );
        """)

        # Trigger to update product quantity after payment
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_quantity_after_payment
        AFTER UPDATE OF status ON bidbuygo_order
        WHEN NEW.status = 'PAID' AND OLD.status != 'PAID'
        BEGIN
            UPDATE bidbuygo_product
            SET quantity = quantity - 1
            WHERE id = NEW.product_id;
            
            UPDATE bidbuygo_product
            SET is_available = CASE 
                WHEN quantity = 0 THEN 0
                ELSE 1
            END
            WHERE id = NEW.product_id;
        END;
        """)

        # Trigger to update product bid information
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS update_bid_info
        AFTER INSERT ON bidbuygo_bidding
        BEGIN
            UPDATE bidbuygo_product
            SET current_bid = NEW.bid_amt,
                last_bid_time = NEW.bid_time
            WHERE id = NEW.product_id;
        END;
        """)

        # Trigger to handle auction ending
        cursor.execute("""
        CREATE TRIGGER IF NOT EXISTS check_auction_ending
        AFTER UPDATE OF last_bid_time ON bidbuygo_product
        WHEN datetime('now') > datetime(NEW.last_bid_time, '+24 hours')
        BEGIN
            -- Mark the highest bid as won
            UPDATE bidbuygo_bidding
            SET bid_status = 'Won'
            WHERE product_id = NEW.id
            AND bid_amt = (
                SELECT MAX(bid_amt) 
                FROM bidbuygo_bidding 
                WHERE product_id = NEW.id
            );
            
            -- Mark other bids as lost
            UPDATE bidbuygo_bidding
            SET bid_status = 'Lost'
            WHERE product_id = NEW.id
            AND bid_amt < (
                SELECT MAX(bid_amt) 
                FROM bidbuygo_bidding 
                WHERE product_id = NEW.id
            );
            
            -- Update product status
            UPDATE bidbuygo_product
            SET auction_status = 'Ended'
            WHERE id = NEW.id;
        END;
        """)

        # Create views for procedures
        cursor.execute("""
        CREATE VIEW IF NOT EXISTS payment_processing AS
        SELECT 
            o.id as order_id,
            o.status as order_status,
            o.razorpay_order_id,
            t.payment_id,
            t.amount,
            t.status as transaction_status
        FROM bidbuygo_order o
        LEFT JOIN bidbuygo_transaction t ON o.id = t.order_id;
        """)

        cursor.execute("""
        CREATE VIEW IF NOT EXISTS auction_management AS
        SELECT 
            p.id as product_id,
            p.auction_status,
            p.last_bid_time,
            b.bid_amt,
            b.bid_status,
            b.user_id
        FROM bidbuygo_product p
        LEFT JOIN bidbuygo_bidding b ON p.id = b.product_id;
        """)

        cursor.execute("""
        CREATE VIEW IF NOT EXISTS inventory_management AS
        SELECT 
            id as product_id,
            quantity,
            is_available,
            CASE 
                WHEN quantity <= 0 THEN 0
                ELSE 1
            END as should_be_available
        FROM bidbuygo_product;
        """)

        # Create function to calculate cart total
        cursor.execute("""
        CREATE FUNCTION IF NOT EXISTS calculate_cart_total(cart_id INTEGER)
        RETURNS DECIMAL(10,2)
        BEGIN
            DECLARE total DECIMAL(10,2);
            SELECT COALESCE(SUM(p.price * ci.quantity), 0)
            INTO total
            FROM bidbuygo_cartitem ci
            JOIN bidbuygo_product p ON ci.product_id = p.product_id
            WHERE ci.cart_id = cart_id;
            RETURN total;
        END;
        """)
        
        # Create view for cart totals
        cursor.execute("""
        CREATE VIEW IF NOT EXISTS cart_totals AS
        SELECT 
            c.id as cart_id,
            c.user_id,
            calculate_cart_total(c.id) as total_price
        FROM bidbuygo_cart c;
        """)

def setup_database():
    """Function to be called from Django shell to set up database objects"""
    try:
        create_database_objects()
        print("Successfully created database objects")
    except Exception as e:
        print(f"Error creating database objects: {str(e)}") 
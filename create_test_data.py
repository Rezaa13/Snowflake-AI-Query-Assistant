"""Script to create synthetic test data in Snowflake for testing the AI agent."""

import sys
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any
import json

# Add src to path for imports
sys.path.insert(0, 'src')

from snowflake_client import snowflake_client
from rich.console import Console
from rich.progress import Progress, TaskID

console = Console()


class SyntheticDataGenerator:
    """Generates synthetic business data for testing."""
    
    def __init__(self):
        """Initialize the data generator."""
        self.console = Console()
        
        # Sample data for generation
        self.first_names = [
            "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
            "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
            "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
            "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna"
        ]
        
        self.last_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
            "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
            "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
            "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young"
        ]
        
        self.companies = [
            "Tech Solutions Inc", "Global Dynamics", "Innovation Corp", "Future Systems",
            "Digital Ventures", "Smart Analytics", "Data Insights", "Cloud Computing Co",
            "AI Technologies", "Quantum Solutions", "NextGen Software", "Cyber Security LLC",
            "Mobile Apps Ltd", "Web Services Inc", "Network Solutions", "IT Consulting Group"
        ]
        
        self.cities = [
            ("New York", "NY"), ("Los Angeles", "CA"), ("Chicago", "IL"), ("Houston", "TX"),
            ("Phoenix", "AZ"), ("Philadelphia", "PA"), ("San Antonio", "TX"), ("San Diego", "CA"),
            ("Dallas", "TX"), ("San Jose", "CA"), ("Austin", "TX"), ("Jacksonville", "FL"),
            ("Fort Worth", "TX"), ("Columbus", "OH"), ("Charlotte", "NC"), ("San Francisco", "CA"),
            ("Indianapolis", "IN"), ("Seattle", "WA"), ("Denver", "CO"), ("Boston", "MA")
        ]
        
        self.products = [
            ("Laptop Pro 15", "Electronics", 1299.99),
            ("Wireless Mouse", "Electronics", 29.99),
            ("Bluetooth Headphones", "Electronics", 199.99),
            ("Smartphone X", "Electronics", 899.99),
            ("Tablet Air", "Electronics", 599.99),
            ("Office Chair", "Furniture", 299.99),
            ("Standing Desk", "Furniture", 449.99),
            ("Monitor 27inch", "Electronics", 329.99),
            ("Keyboard Mechanical", "Electronics", 129.99),
            ("Webcam HD", "Electronics", 79.99),
            ("Coffee Maker", "Appliances", 149.99),
            ("Blender Pro", "Appliances", 99.99),
            ("Air Purifier", "Appliances", 199.99),
            ("Smart Watch", "Electronics", 399.99),
            ("Gaming Console", "Electronics", 499.99),
            ("Book - Python Programming", "Books", 49.99),
            ("Book - Data Science", "Books", 59.99),
            ("Book - Machine Learning", "Books", 69.99),
            ("Backpack Premium", "Accessories", 89.99),
            ("Water Bottle", "Accessories", 24.99)
        ]
        
        self.departments = ["Sales", "Marketing", "IT", "HR", "Finance", "Operations", "Customer Service"]
        
    def create_database_and_schema(self) -> bool:
        """Create test database and schema."""
        try:
            console.print("🏗️ Creating test database and schema...")
            
            # Create database
            snowflake_client.execute_query(
                "CREATE DATABASE IF NOT EXISTS DEMO_DATA", 
                fetch_results=False
            )
            
            # Create schema
            snowflake_client.execute_query(
                "CREATE SCHEMA IF NOT EXISTS DEMO_DATA.BUSINESS", 
                fetch_results=False
            )
            
            # Use the database and schema
            snowflake_client.execute_query(
                "USE DATABASE DEMO_DATA", 
                fetch_results=False
            )
            
            snowflake_client.execute_query(
                "USE SCHEMA BUSINESS", 
                fetch_results=False
            )
            
            console.print("✅ Database and schema created successfully")
            return True
            
        except Exception as e:
            console.print(f"❌ Error creating database/schema: {e}")
            return False
    
    def create_tables(self) -> bool:
        """Create all necessary tables."""
        try:
            console.print("📋 Creating tables...")
            
            # Customers table
            snowflake_client.execute_query("""
                CREATE OR REPLACE TABLE customers (
                    customer_id INTEGER AUTOINCREMENT PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    phone VARCHAR(15),
                    company VARCHAR(100),
                    city VARCHAR(50),
                    state VARCHAR(2),
                    registration_date DATE,
                    customer_status VARCHAR(20) DEFAULT 'Active',
                    lifetime_value DECIMAL(10,2) DEFAULT 0
                )
            """, fetch_results=False)
            
            # Products table
            snowflake_client.execute_query("""
                CREATE OR REPLACE TABLE products (
                    product_id INTEGER AUTOINCREMENT PRIMARY KEY,
                    product_name VARCHAR(100) NOT NULL,
                    category VARCHAR(50),
                    price DECIMAL(10,2) NOT NULL,
                    cost DECIMAL(10,2),
                    stock_quantity INTEGER DEFAULT 0,
                    created_date DATE
                )
            """, fetch_results=False)
            
            # Orders table
            snowflake_client.execute_query("""
                CREATE OR REPLACE TABLE orders (
                    order_id INTEGER AUTOINCREMENT PRIMARY KEY,
                    customer_id INTEGER,
                    order_date DATE NOT NULL,
                    order_status VARCHAR(20) DEFAULT 'Pending',
                    total_amount DECIMAL(10,2),
                    shipping_city VARCHAR(50),
                    shipping_state VARCHAR(2),
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
                )
            """, fetch_results=False)
            
            # Order items table
            snowflake_client.execute_query("""
                CREATE OR REPLACE TABLE order_items (
                    order_item_id INTEGER AUTOINCREMENT PRIMARY KEY,
                    order_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER NOT NULL,
                    unit_price DECIMAL(10,2) NOT NULL,
                    total_price DECIMAL(10,2),
                    FOREIGN KEY (order_id) REFERENCES orders(order_id),
                    FOREIGN KEY (product_id) REFERENCES products(product_id)
                )
            """, fetch_results=False)
            
            # Sales representatives table
            snowflake_client.execute_query("""
                CREATE OR REPLACE TABLE sales_reps (
                    rep_id INTEGER AUTOINCREMENT PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    department VARCHAR(50),
                    hire_date DATE,
                    quota DECIMAL(10,2),
                    region VARCHAR(50)
                )
            """, fetch_results=False)
            
            # Customer interactions table
            snowflake_client.execute_query("""
                CREATE OR REPLACE TABLE customer_interactions (
                    interaction_id INTEGER AUTOINCREMENT PRIMARY KEY,
                    customer_id INTEGER,
                    rep_id INTEGER,
                    interaction_type VARCHAR(50),
                    interaction_date DATE,
                    notes VARCHAR(500),
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                    FOREIGN KEY (rep_id) REFERENCES sales_reps(rep_id)
                )
            """, fetch_results=False)
            
            console.print("✅ All tables created successfully")
            return True
            
        except Exception as e:
            console.print(f"❌ Error creating tables: {e}")
            return False
    
    def generate_customers(self, count: int = 500) -> bool:
        """Generate synthetic customer data."""
        try:
            console.print(f"👥 Generating {count} customers...")
            
            customers = []
            for i in range(count):
                first_name = random.choice(self.first_names)
                last_name = random.choice(self.last_names)
                email = f"{first_name.lower()}.{last_name.lower()}{i}@email.com"
                phone = f"+1-555-{random.randint(100,999)}-{random.randint(1000,9999)}"
                company = random.choice(self.companies) if random.random() > 0.3 else None
                city, state = random.choice(self.cities)
                reg_date = datetime.now() - timedelta(days=random.randint(30, 1095))
                status = random.choices(["Active", "Inactive", "Premium"], weights=[80, 10, 10])[0]
                lifetime_value = round(random.uniform(100, 50000), 2)
                
                company_value = "NULL" if not company else f"'{company}'"
                
                customers.append(
                    f"('{first_name}', '{last_name}', '{email}', '{phone}', "
                    f"{company_value}, '{city}', '{state}', "
                    f"'{reg_date.date()}', '{status}', {lifetime_value})"
                )
            
            # Insert in batches
            batch_size = 100
            for i in range(0, len(customers), batch_size):
                batch = customers[i:i + batch_size]
                values = ",\n".join(batch)
                
                query = f"""
                    INSERT INTO customers 
                    (first_name, last_name, email, phone, company, city, state, 
                     registration_date, customer_status, lifetime_value)
                    VALUES {values}
                """
                
                snowflake_client.execute_query(query, fetch_results=False)
            
            console.print("✅ Customers generated successfully")
            return True
            
        except Exception as e:
            console.print(f"❌ Error generating customers: {e}")
            return False
    
    def generate_products(self) -> bool:
        """Generate synthetic product data."""
        try:
            console.print("📦 Generating products...")
            
            products = []
            for product_name, category, price in self.products:
                cost = round(price * random.uniform(0.4, 0.7), 2)
                stock = random.randint(10, 1000)
                created_date = datetime.now() - timedelta(days=random.randint(1, 365))
                
                products.append(
                    f"('{product_name}', '{category}', {price}, {cost}, {stock}, '{created_date.date()}')"
                )
            
            values = ",\n".join(products)
            query = f"""
                INSERT INTO products 
                (product_name, category, price, cost, stock_quantity, created_date)
                VALUES {values}
            """
            
            snowflake_client.execute_query(query, fetch_results=False)
            
            console.print("✅ Products generated successfully")
            return True
            
        except Exception as e:
            console.print(f"❌ Error generating products: {e}")
            return False
    
    def generate_sales_reps(self, count: int = 20) -> bool:
        """Generate synthetic sales rep data."""
        try:
            console.print(f"👔 Generating {count} sales representatives...")
            
            reps = []
            regions = ["North", "South", "East", "West", "Central"]
            
            for i in range(count):
                first_name = random.choice(self.first_names)
                last_name = random.choice(self.last_names)
                email = f"{first_name.lower()}.{last_name.lower()}{i}@company.com"
                department = random.choice(self.departments)
                hire_date = datetime.now() - timedelta(days=random.randint(30, 2000))
                quota = round(random.uniform(50000, 200000), 2)
                region = random.choice(regions)
                
                reps.append(
                    f"('{first_name}', '{last_name}', '{email}', '{department}', "
                    f"'{hire_date.date()}', {quota}, '{region}')"
                )
            
            values = ",\n".join(reps)
            query = f"""
                INSERT INTO sales_reps 
                (first_name, last_name, email, department, hire_date, quota, region)
                VALUES {values}
            """
            
            snowflake_client.execute_query(query, fetch_results=False)
            
            console.print("✅ Sales reps generated successfully")
            return True
            
        except Exception as e:
            console.print(f"❌ Error generating sales reps: {e}")
            return False
    
    def generate_orders_and_items(self, order_count: int = 1000) -> bool:
        """Generate synthetic orders and order items."""
        try:
            console.print(f"🛒 Generating {order_count} orders with items...")
            
            # Get customer and product IDs
            customers = snowflake_client.execute_query("SELECT customer_id FROM customers")
            products = snowflake_client.execute_query("SELECT product_id, price FROM products")
            
            customer_ids = [c['CUSTOMER_ID'] for c in customers]
            product_data = [(p['PRODUCT_ID'], float(p['PRICE'])) for p in products]
            
            orders = []
            order_items = []
            order_id_counter = 1
            
            statuses = ["Completed", "Pending", "Shipped", "Cancelled"]
            
            for _ in range(order_count):
                customer_id = random.choice(customer_ids)
                order_date = datetime.now() - timedelta(days=random.randint(1, 365))
                status = random.choices(statuses, weights=[70, 15, 10, 5])[0]
                city, state = random.choice(self.cities)
                
                # Generate 1-5 items per order
                num_items = random.randint(1, 5)
                order_total = 0
                
                for _ in range(num_items):
                    product_id, base_price = random.choice(product_data)
                    quantity = random.randint(1, 3)
                    # Add some price variation
                    unit_price = round(base_price * random.uniform(0.9, 1.1), 2)
                    total_price = round(unit_price * quantity, 2)
                    order_total += total_price
                    
                    order_items.append(
                        f"({order_id_counter}, {product_id}, {quantity}, {unit_price}, {total_price})"
                    )
                
                orders.append(
                    f"({order_id_counter}, {customer_id}, '{order_date.date()}', '{status}', "
                    f"{round(order_total, 2)}, '{city}', '{state}')"
                )
                
                order_id_counter += 1
            
            # Insert orders in batches
            batch_size = 100
            for i in range(0, len(orders), batch_size):
                batch = orders[i:i + batch_size]
                values = ",\n".join(batch)
                
                query = f"""
                    INSERT INTO orders 
                    (order_id, customer_id, order_date, order_status, total_amount, shipping_city, shipping_state)
                    VALUES {values}
                """
                
                snowflake_client.execute_query(query, fetch_results=False)
            
            # Insert order items in batches
            for i in range(0, len(order_items), batch_size):
                batch = order_items[i:i + batch_size]
                values = ",\n".join(batch)
                
                query = f"""
                    INSERT INTO order_items 
                    (order_id, product_id, quantity, unit_price, total_price)
                    VALUES {values}
                """
                
                snowflake_client.execute_query(query, fetch_results=False)
            
            console.print("✅ Orders and items generated successfully")
            return True
            
        except Exception as e:
            console.print(f"❌ Error generating orders: {e}")
            return False
    
    def generate_interactions(self, count: int = 200) -> bool:
        """Generate synthetic customer interactions."""
        try:
            console.print(f"📞 Generating {count} customer interactions...")
            
            # Get customer and rep IDs
            customers = snowflake_client.execute_query("SELECT customer_id FROM customers LIMIT 100")
            reps = snowflake_client.execute_query("SELECT rep_id FROM sales_reps")
            
            customer_ids = [c['CUSTOMER_ID'] for c in customers]
            rep_ids = [r['REP_ID'] for r in reps]
            
            interaction_types = ["Phone Call", "Email", "Meeting", "Support Ticket", "Follow-up"]
            notes_templates = [
                "Customer inquiry about product features",
                "Follow-up on recent order",
                "Technical support request",
                "Sales consultation meeting",
                "Product demonstration scheduled",
                "Customer feedback discussion",
                "Contract renewal discussion",
                "Pricing inquiry",
                "Product training session",
                "Customer satisfaction survey"
            ]
            
            interactions = []
            for _ in range(count):
                customer_id = random.choice(customer_ids)
                rep_id = random.choice(rep_ids)
                interaction_type = random.choice(interaction_types)
                interaction_date = datetime.now() - timedelta(days=random.randint(1, 180))
                notes = random.choice(notes_templates)
                
                interactions.append(
                    f"({customer_id}, {rep_id}, '{interaction_type}', "
                    f"'{interaction_date.date()}', '{notes}')"
                )
            
            # Insert in batches
            batch_size = 50
            for i in range(0, len(interactions), batch_size):
                batch = interactions[i:i + batch_size]
                values = ",\n".join(batch)
                
                query = f"""
                    INSERT INTO customer_interactions 
                    (customer_id, rep_id, interaction_type, interaction_date, notes)
                    VALUES {values}
                """
                
                snowflake_client.execute_query(query, fetch_results=False)
            
            console.print("✅ Customer interactions generated successfully")
            return True
            
        except Exception as e:
            console.print(f"❌ Error generating interactions: {e}")
            return False
    
    def create_views(self) -> bool:
        """Create useful views for analysis."""
        try:
            console.print("👁️ Creating analytical views...")
            
            # Customer summary view
            snowflake_client.execute_query("""
                CREATE OR REPLACE VIEW customer_summary AS
                SELECT 
                    c.customer_id,
                    c.first_name || ' ' || c.last_name AS full_name,
                    c.email,
                    c.company,
                    c.city,
                    c.state,
                    c.customer_status,
                    c.lifetime_value,
                    COUNT(o.order_id) AS total_orders,
                    COALESCE(SUM(o.total_amount), 0) AS total_spent,
                    MAX(o.order_date) AS last_order_date
                FROM customers c
                LEFT JOIN orders o ON c.customer_id = o.customer_id
                GROUP BY c.customer_id, c.first_name, c.last_name, c.email, 
                         c.company, c.city, c.state, c.customer_status, c.lifetime_value
            """, fetch_results=False)
            
            # Product performance view
            snowflake_client.execute_query("""
                CREATE OR REPLACE VIEW product_performance AS
                SELECT 
                    p.product_id,
                    p.product_name,
                    p.category,
                    p.price,
                    p.stock_quantity,
                    COUNT(oi.order_item_id) AS times_ordered,
                    SUM(oi.quantity) AS total_quantity_sold,
                    SUM(oi.total_price) AS total_revenue,
                    AVG(oi.unit_price) AS avg_selling_price
                FROM products p
                LEFT JOIN order_items oi ON p.product_id = oi.product_id
                GROUP BY p.product_id, p.product_name, p.category, p.price, p.stock_quantity
            """, fetch_results=False)
            
            # Monthly sales view
            snowflake_client.execute_query("""
                CREATE OR REPLACE VIEW monthly_sales AS
                SELECT 
                    DATE_TRUNC('MONTH', order_date) AS sales_month,
                    COUNT(order_id) AS total_orders,
                    SUM(total_amount) AS total_revenue,
                    AVG(total_amount) AS avg_order_value,
                    COUNT(DISTINCT customer_id) AS unique_customers
                FROM orders
                WHERE order_status = 'Completed'
                GROUP BY DATE_TRUNC('MONTH', order_date)
                ORDER BY sales_month
            """, fetch_results=False)
            
            console.print("✅ Views created successfully")
            return True
            
        except Exception as e:
            console.print(f"❌ Error creating views: {e}")
            return False
    
    def show_summary(self) -> None:
        """Show summary of generated data."""
        try:
            console.print("\n📊 Data Generation Summary:")
            
            # Get counts from each table
            tables = ["customers", "products", "sales_reps", "orders", "order_items", "customer_interactions"]
            
            for table in tables:
                result = snowflake_client.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                count = result[0]['COUNT'] if result else 0
                console.print(f"   • {table.replace('_', ' ').title()}: {count:,} records")
            
            console.print("\n📋 Available Views:")
            console.print("   • customer_summary - Customer overview with order statistics")
            console.print("   • product_performance - Product sales performance metrics")
            console.print("   • monthly_sales - Monthly sales trends and metrics")
            
            console.print("\n💡 Example queries to try with the AI agent:")
            example_queries = [
                "Show me the top 10 customers by total spending",
                "What are our best-selling products?",
                "How many orders do we have this year?",
                "Which sales rep has the highest quota?",
                "Show me monthly sales trends",
                "What's the average order value?",
                "Which product category generates the most revenue?",
                "Show me customers from California",
                "What's our customer retention rate?",
                "Which products are running low on stock?"
            ]
            
            for i, query in enumerate(example_queries, 1):
                console.print(f"   {i:2d}. \"{query}\"")
                
        except Exception as e:
            console.print(f"❌ Error showing summary: {e}")


def main():
    """Main function to generate all synthetic data."""
    generator = SyntheticDataGenerator()
    
    console.print("🎯 Synthetic Data Generation for Snowflake AI Agent")
    console.print("=" * 60)
    
    try:
        # Connect to Snowflake
        console.print("🔌 Connecting to Snowflake...")
        snowflake_client.connect()
        
        # Generate all data
        steps = [
            ("Creating database and schema", generator.create_database_and_schema),
            ("Creating tables", generator.create_tables),
            ("Generating customers", lambda: generator.generate_customers(500)),
            ("Generating products", generator.generate_products),
            ("Generating sales reps", lambda: generator.generate_sales_reps(20)),
            ("Generating orders and items", lambda: generator.generate_orders_and_items(1000)),
            ("Generating customer interactions", lambda: generator.generate_interactions(200)),
            ("Creating analytical views", generator.create_views),
        ]
        
        with Progress() as progress:
            task = progress.add_task("[green]Generating data...", total=len(steps))
            
            for step_name, step_func in steps:
                progress.update(task, description=f"[green]{step_name}...")
                success = step_func()
                
                if not success:
                    console.print(f"❌ Failed at step: {step_name}")
                    return False
                
                progress.advance(task)
        
        # Show summary
        generator.show_summary()
        
        console.print("\n🎉 Data generation completed successfully!")
        console.print("\nYou can now test your AI agent with commands like:")
        console.print("   python -m src.main interactive")
        
        return True
        
    except Exception as e:
        console.print(f"❌ Error during data generation: {e}")
        return False
    
    finally:
        snowflake_client.disconnect()


if __name__ == "__main__":
    main()
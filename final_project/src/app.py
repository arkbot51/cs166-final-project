import sys
import random
from psycopg2 import extras, connect

# --- DATABASE CONNECTION HELPER ---
def run_query(query, params=None, is_select=True):
    try:
        conn = connect(
            dbname="akim461_Project_DB",
            user="akim461",
            password="Noahyoung02!",
            host="localhost",
            port="36253"
        )
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)
        cur.execute(query, params)

        if is_select:
            result = cur.fetchall()
            return result
        else:
            conn.commit()
            return True
    except Exception as e:
        print(f"\nAn error occurred:\n{e}\n")
        return None
    finally:
        if 'cur' in locals(): cur.close()
        if 'conn' in locals(): conn.close()

# --- SYSTEM SYSTEM WORKFLOWS ---

class AuctionCLI:
    def __init__(self):
        self.current_user = None
        self.current_role = None
    
    def login(self):
        print("\n--- LOGIN ---")
        username = input("Username: ").strip()
        password = input("Password: ").strip()
        login_sql = """
            SELECT login, role
            FROM users
            WHERE login = %s AND password = %s
        """

        result = run_query(login_sql, (username, password), fetch = True)

        if result:
            self.current_user = result[0]["login"]
            self.current_role = result[0]["role"]
            print(f"\nLogin successful as {self.current_role}")
            return True
            
        print("Invalid username or password. Please try again.")
        return False

    def main_menu(self):
        if not self.login():
            return
        
        while True:
            print("\n" + "="*45)
            print("AUCTION MARKETPLACE")
            print("="*45)
            print(f" Current User: {self.current_user} | View: {self.current_role}")
            print("-"*45)
            print("1. Switch User / System View")
            print("2. Enter Buyer Dashboard")
            print("3. Enter Seller Hub")
            print("4. Enter Admin Panel")
            print("5. Exit Application")
            print("="*45)
            
            choice = input("Select an option (1-5): ").strip()
            
            if choice == "1":
                self.switch_user()
            elif choice == "2":
                self.buyer_dashboard()
            elif choice == "3":
                self.seller_dashboard()
            elif choice == "4":
                self.admin_dashboard()
            elif choice == "5":
                print("\nExiting application. Goodbye!")
                sys.exit(0)
            else:
                print("\nPlease enter a number from 1 to 5.")

    def switch_user(self):
        print("\n--- switching account view ---")
        new_user = input("Enter Username ID (e.g., buyer_jack, seller_jill): ").strip()
        print("Select System View:")
        print("1. Buyer\n2. Seller\n3. Admin")
        role_choice = input("Choice (1-3): ").strip()
        
        if role_choice == "1":
            self.current_role = "Buyer"
        elif role_choice == "2":
            self.current_role = "Seller"
        elif role_choice == "3":
            self.current_role = "Admin"
        else:
            print("\nerror: Invalid role chosen. Keeping original settings.")
            return
            
        if new_user:
            self.current_user = new_user
        print(f"\nsuccess: Switched to user '{self.current_user}' with '{self.current_role}' view.")

    # -------------------------------------------------------------
    # 1. BUYER DASHBOARD
    # -------------------------------------------------------------
    def buyer_dashboard(self):
        while True:
            print("\n" + "-"*40)
            print("BUYER DASHBOARD")
            print("-"*40)
            print("1. Browse Active Public Auctions")
            print("2. Place a Competitive Bid")
            print("3. View Won Auction")
            print("4. Make Payment")
            print("5. Return to Main Menu")
            print("-"*40)
            
            choice = input("Select choice (1-4): ").strip()
            
            if choice == "1":
                self.view_active_auctions()
            elif choice == "2":
                self.place_bid()
            elif choice == "3":
                self.view_won_auctions()
            elif choice == "4":
                self.make_payment()
            elif choice == "5":
                break

    def view_active_auctions(self):
        query = """
            SELECT a.auction_id, i.item_name, i.category, a.current_highest_bid 
            FROM auction a 
            JOIN item i ON a.item_id = i.item_id 
            WHERE a.auction_status = 'Active'
        """
        rows = run_query(query)
        print("\n=== active auctions ===")
        if rows:
            print(f"{'Auction ID':<12} | {'Item Name':<20} | {'Category':<15} | {'Highest Bid':<12}")
            print("-" * 68)
            for r in rows:
                print(f"{r['auction_id']:<12} | {r['item_name']:<20} | {r['category']:<15} | ${r['current_highest_bid']:<11.2f}")
        else:
            print("No active auctions found in the database system.")

    def place_bid(self):
        print("\n--- place bid ---")
        auc_id = input("Target Auction ID: ").strip()
        amount = input("Your Bid Amount ($): ").strip()
        
        if not auc_id or not amount:
            print("\n All fields are mandatory.")
            return
            
        import random
        random_bid_id = random.randint(10000, 99999)
        
        bid_sql = """
            INSERT INTO bid (bid_id, auction_id, buyer_login, buyer_role, bid_amount) 
            VALUES (%s, %s, %s, 'Buyer', %s)
        """
        success = run_query(bid_sql, (random_bid_id, auc_id, self.current_user, amount), is_select=False)
        
        if success:
            update_sql = "UPDATE auction SET current_highest_bid = %s WHERE auction_id = %s"
            run_query(update_sql, (amount, auc_id), is_select=False)
            print(f"\nsuccess: Your bid was processed! Saved Bid ID: {random_bid_id}")

    def view_won_auctions(self):
        won_auction_sql = """
            SELECT auction_id, current_highest_bid, auction_status
            FROM auction
            WHERE winner_login = %s AND auction_status = "Closed"
        """

        result = run_query(won_auction_sql, (self.current_user,))
        
        print("\n--- YOUR WON AUCTIONS ---")
        if not result:
            print("You have not won any auctions yet.")
            return
        
        for r in result:
            print(r)

    def make_payment(self):
        auction_id = input("Enter Auction ID to pay for: ")
        payment_sql = """
            SELECT auction_id, winner_login, auction_status, current_highest_bid
            FROM auction
            WHERE auction_id = %s
        """
        
        result = run_query(payment_sql, (auction_id,))

        if not result:
            print("Auction not found!")
            return
        
        auction = result[0]

        if auction["winner_login"] != self.current_user:
            print("You are not the winner of this auction.")
            return
        
        if auction["auction_status"] != "Closed":
            print("Auction is not closed yet")
            return
        
        payment_id = random.randint(1000,9999)

        run_query("""
            INSERT INTO payment (payment_id, auction_id, buyer_login, amount, payment_status)
            VALUES (%s, %s, %s, %s, "Completed")
        """, (payment_id, auction_id, self.current_user, auction["current_highest_bid"]), fetch = False
        )

        print("Payment is successful!")
    # -------------------------------------------------------------
    # 2. SELLER HUB
    # -------------------------------------------------------------
    def seller_dashboard(self):
        while True:
            print("\n" + "-"*40)
            print("SELLER HUB DASHBOARD")
            print("-"*40)
            print("1. Launch a New Public Auction Listing")
            print("2. View my Auction")
            print("3. Close Auction")
            print("4. Create Shipment")
            print("5. Return to Main Menu")
            print("-"*40)
            
            choice = input("Select choice (1-2): ").strip()
            
            if choice == "1":
                self.create_listing()
            elif choice == "2":
                self.view_my_auctions()
            elif choice == "3":
                self.close_auction()
            elif choice == "4": 
                self.create_shipment()
            elif choice == "5":
                break

    def create_listing(self):
        print("\n--- launch new auction item ---")
        item_id = input("Item ID Number: ").strip()
        name = input("Item Trade Name: ").strip()
        cat = input("Category: ").strip()
        price = input("Starting Price ($): ").strip()
        cond = input("Condition (New/Used): ").strip()
        
        if not item_id or not name or not price:
            print("\nItem ID, Name, and Initial Price are completely mandatory.")
            return
            
        item_sql = """
            INSERT INTO item (item_id, item_name, category, starting_price, item_condition, seller_login, seller_role) 
            VALUES (%s, %s, %s, %s, %s, %s, 'Seller')
        """
        item_success = run_query(item_sql, (item_id, name, cat, price, cond, self.current_user), is_select=False)
        
        if item_success:
            import random
            auc_id = random.randint(10000, 99999)
            auc_sql = """
                INSERT INTO auction (auction_id, item_id, seller_login, seller_role, current_highest_bid, auction_status) 
                VALUES (%s, %s, %s, 'Seller', %s, 'Active')
            """
            run_query(auc_sql, (auc_id, item_id, self.current_user, price), is_select=False)
            print(f"\nSuccess: Item inventory loaded! Auction is live at ID: {auc_id}")

    def view_my_auctions(self):
        result = run_query("""
            SELECT *
            FROM auction
            WHERE seller_login = %s
        """, (self.current_user,))

        for r in result:
            print(r)
    
    def close_auction(self):
        auction_id = input("Auction ID for closing: ")

        winner = run_query("""
            SELECT buyer_login
            FROM bid
            WHERE auction_id = %s
            ORDER BY bid_amount DESC LIMIT 1
        """, (auction_id,))

        if winner:
            winner_login = winner[0]["buyer_login"]
        else:
            winner_login = None

        run_query("""
            UPDATE auction
            SET auction_status = "Closed", winner_login = %s
            WHERE auction_id = %s
        """, (winner_login, auction_id), fetch = False)

        print("Auction closed!")
    
    def create_shipment(self):
        shipment_id = random.randint(10000,99999)
        auction_id = input("Auction ID: ")
        address = input("Shipping Address: ")

        run_query("""
            INSERT INTO shipment(shipment_id, auction_id, address, shipment_status)
            VALUES(%s, %s, %s, "Pending")
        """, (shipment_id, auction_id, address), fetch = False)

        print("Shipment Created!")
    # -------------------------------------------------------------
    # 3. ADMIN ANALYTICS CONTROL PANEL
    # -------------------------------------------------------------
    def admin_dashboard(self):
        while True:
            print("\n" + "-"*40)
            print("ADMIN SYSTEM ANALYTICS")
            print("-"*40)
            print("1. View System Aggregates & Statistics")
            print("2. Print Global User Account Matrix")
            print("3. Return to Main Menu")
            print("-"*40)
            
            choice = input("Select choice (1-3): ").strip()
            
            if choice == "1":
                self.view_system_stats()
            elif choice == "2":
                self.view_user_matrix()
            elif choice == "3":
                break

    def view_system_stats(self):
        users_count = run_query("SELECT COUNT(*) as c FROM users")[0]['c']
        items_count = run_query("SELECT COUNT(*) as c FROM item")[0]['c']
        bids_count = run_query("SELECT COUNT(*) as c FROM bid")[0]['c']
        
        print("\n=== SYSTEM OVERVIEW AGGREGATES ===")
        print(f"Users Enrolled:  {users_count}")
        print(f"Active Inventory: {items_count}")
        print(f"Bids Logged:     {bids_count}")

    def view_user_matrix(self):
        users_list = run_query("SELECT login, phone_num, role, address FROM users")
        print("\n=== global user account audit matrix ===")
        if users_list:
            print(f"{'Username ID':<15} | {'Phone Field':<12} | {'Security Role':<13} | {'Delivery Address'}")
            print("-" * 75)
            for u in users_list:
                print(f"{u['login']:<15} | {u['phone_num']:<12} | {u['role']:<13} | {u['address']}")
        else:
            print("No users found inside the system database registry.")

# --- APPLICATION ENTRY POINT ---
if __name__ == "__main__":
    app = AuctionCLI()
    app.main_menu()
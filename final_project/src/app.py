import sys
from psycopg2 import extras, connect

# helper
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



class AuctionCLI:
    def __init__(self):
        self.current_user = None
        self.current_role = None

    def login(self):
        while True:
            print("\n=== Login ===")
            username = input("Username: ").strip()
            password = input("Password: ").strip()
            user = run_query("""
                SELECT login, role
                FROM users
                WHERE login=%s
                AND password=%s
            """, (username, password))
            if user:
                self.current_user = user[0]["login"]
                self.current_role = user[0]["role"]
                print(f"\nWelcome {self.current_user}")
                return
            print("Invalid login.")
    
    #helper
    def next_id(self, table, column):
        result = run_query(
            f"SELECT COALESCE(MAX({column}),0)+1 AS id FROM {table}"
        )

        return result[0]["id"]

    def main_menu(self):

        while True:
            print("Auction Marketplace")

            print(f"User: {self.current_user}")
            print(f"Role: {self.current_role}")

            print("\n1. Buyer Menu")
            print("2. Seller Menu")
            print("3. Admin Menu")
            print("4. Logout")
            print("5. Exit")

            choice = input("Choice: ")

            if choice == "1":
                self.buyer_menu()

            elif choice == "2":
                self.seller_menu()

            elif choice == "3":
                self.admin_menu()

            elif choice == "4":
                self.login()

            elif choice == "5":
                sys.exit()

    #buyer dashboard
    def buyer_menu(self):
        if self.current_role != "Buyer":
            print("Access denied.")
            return
        while True:
            print("\nBuyer Menu")
            print("1. Browse Auctions")
            print("2. Place Bid")
            print("3. View Won Auctions")
            print("4. Make Payment")
            print("5. Track Shipment")
            print("6. Back")
            choice = input("Choice: ")
            if choice == "1":
                self.browse_auctions()
            elif choice == "2":
                self.place_bid()
            elif choice == "3":
                self.view_won_auctions()
            elif choice == "4":
                self.make_payment()
            elif choice == "5":
                self.track_shipments()
            elif choice == "6":
                break

    def browse_auctions(self):
        rows = run_query("""
            SELECT
                a.auction_id,
                i.item_name,
                i.category,
                a.current_highest_bid
            FROM auction a
            JOIN item i
                ON a.item_id = i.item_id
            WHERE a.auction_status='Active'
        """)
        print("\nActive Auctions")
        for row in rows:
            print(
                row["auction_id"],
                row["item_name"],
                row["category"],
                row["current_highest_bid"]
            )

    def place_bid(self):
        auction_id = input("Auction ID: ")
        auction = run_query("""
            SELECT current_highest_bid,
                auction_status
            FROM auction
            WHERE auction_id=%s
        """, (auction_id,))
        if not auction:
            print("Auction not found.")
            return
        auction = auction[0]
        if auction["auction_status"] != "Active":
            print("Auction closed.")
            return
        amount = float(input("Bid Amount: "))
        if amount <= float(auction["current_highest_bid"]):
            print("Bid too low.")
            return
        bid_id = self.next_id("bid", "bid_id")
        run_query("""
            INSERT INTO bid(
                bid_id,
                auction_id,
                buyer_login,
                buyer_role,
                bid_amount
            )
            VALUES (%s,%s,%s,'Buyer',%s)
        """,
        (
            bid_id,
            auction_id,
            self.current_user,
            amount
        ),
        False)
        run_query("""
            UPDATE auction
            SET current_highest_bid=%s
            WHERE auction_id=%s
        """,
        (
            amount,
            auction_id
        ),
        False)
        print("Bid placed")

    def view_won_auctions(self):
        rows = run_query("""
            SELECT
                auction_id,
                current_highest_bid
            FROM auction
            WHERE winner_login=%s
        """, (self.current_user,))
        print("\nWon auctions")
        for row in rows:
            print(
                row["auction_id"],
                row["current_highest_bid"]
            )
    
    def make_payment(self):
        rows = run_query("""
            SELECT *
            FROM payment
            WHERE buyer_login=%s
            AND payment_status='Pending'
        """, (self.current_user,))
        if not rows:
            print("No needed payments.")
            return
        for row in rows:
            print(
                row["payment_id"],
                row["auction_id"],
                row["amount"]
            )
        payment_id = input("Payment ID: ")
        payment = run_query("""
            SELECT *
            FROM payment
            WHERE payment_id=%s
        """, (payment_id,))
        if not payment:
            return
        payment = payment[0]
        run_query("""
            UPDATE payment
            SET payment_status='Completed'
            WHERE payment_id=%s
        """,
        (payment_id,),
        False)
        shipment_id = self.next_id(
            "shipment",
            "shipment_id"
        )
        address = run_query("""
            SELECT address
            FROM users
            WHERE login=%s
        """,
        (self.current_user,))[0]["address"]
        run_query("""
            INSERT INTO shipment(
                shipment_id,
                auction_id,
                address,
                shipment_status
            )
            VALUES(%s,%s,%s,'Pending')
        """,
        (
            shipment_id,
            payment["auction_id"],
            address
        ),
        False)
        print("Payment completed.")

    def track_shipments(self):
        rows = run_query("""
            SELECT s.*
            FROM shipment s
            JOIN payment p
                ON s.auction_id = p.auction_id
            WHERE p.buyer_login=%s
        """, (self.current_user,))
        for row in rows:
            print(
                row["shipment_id"],
                row["shipment_status"],
                row["tracking_number"]
            )

    #seller dashboard
    def seller_menu(self):
        if self.current_role != "Seller":
            print("Access denied.")
            return
        while True:
            print("\nSeller menu")
            print("1. Create Item")
            print("2. Create Auction")
            print("3. Close Auction")
            print("4. View Payments")
            print("5. Ship Item")
            print("6. Back")
            choice = input("Choice: ")
            if choice == "1":
                self.create_item()
            elif choice == "2":
                self.create_auction()
            elif choice == "3":
                self.close_auction()
            elif choice == "4":
                self.view_payments()
            elif choice == "5":
                self.ship_item()
            elif choice == "6":
                break

    def create_item(self):
        item_id = self.next_id("item", "item_id")
        name = input("Item Name: ")
        category = input("Category: ")
        price = input("Starting Price: ")
        condition = input("Condition: ")
        description = input("Description: ")
        image_url = input("Image URL: ")
        run_query("""
            INSERT INTO item(
                item_id,
                item_name,
                category,
                starting_price,
                image_url,
                item_condition,
                description,
                seller_login,
                seller_role
            )
            VALUES(
                %s,%s,%s,%s,%s,%s,%s,%s,'Seller'
            )
        """,
        (
            item_id,
            name,
            category,
            price,
            image_url,
            condition,
            description,
            self.current_user
        ),
        False)
        print("Item created.")

    def create_auction(self):
        item_id = input("Item ID: ")
        item = run_query("""
            SELECT *
            FROM item
            WHERE item_id=%s
            AND seller_login=%s
        """,
        (
            item_id,
            self.current_user
        ))
        if not item:
            print("Invalid item.")
            return
        auction_id = self.next_id(
            "auction",
            "auction_id"
        )
        run_query("""
            INSERT INTO auction(
                auction_id,
                item_id,
                seller_login,
                seller_role,
                current_highest_bid,
                auction_status
            )
            VALUES(
                %s,%s,%s,'Seller',%s,'Active'
            )
        """,
        (
            auction_id,
            item_id,
            self.current_user,
            item[0]["starting_price"]
        ),
        False)
        print("Auction created.")
    
    def close_auction(self):
        auction_id = input("Auction ID: ")
        winner = run_query("""
            SELECT buyer_login,
                bid_amount
            FROM bid
            WHERE auction_id=%s
            ORDER BY bid_amount DESC
            LIMIT 1
        """, (auction_id,))
        if not winner:
            run_query("""
                UPDATE auction
                SET auction_status='Closed'
                WHERE auction_id=%s
            """,
            (auction_id,),
            False)

            print("Closed with no bids.")
            return
        winner = winner[0]
        run_query("""
            UPDATE auction
            SET auction_status='Closed',
                winner_login=%s,
                winner_role='Buyer'
            WHERE auction_id=%s
        """,
        (
            winner["buyer_login"],
            auction_id
        ),
        False)
        payment_id = self.next_id(
            "payment",
            "payment_id"
        )
        run_query("""
            INSERT INTO payment(
                payment_id,
                auction_id,
                buyer_login,
                buyer_role,
                amount,
                payment_status
            )
            VALUES(
                %s,%s,%s,'Buyer',%s,'Pending'
            )
        """,
        (
            payment_id,
            auction_id,
            winner["buyer_login"],
            winner["bid_amount"]
        ),
        False)
        print("Auction closed.")
    
    def view_payments(self):
        rows = run_query("""
            SELECT *
            FROM payment
        """)
        for row in rows:
            print(
                row["payment_id"],
                row["auction_id"],
                row["amount"],
                row["payment_status"]
            )
    
    def ship_item(self):
        shipment_id = input("Shipment ID: ")
        tracking = input("Tracking Number: ")
        run_query("""
            UPDATE shipment
            SET shipment_status='Shipped',
                tracking_number=%s
            WHERE shipment_id=%s
        """,
        (
            tracking,
            shipment_id
        ),
        False)
        print("Shipment updated.")

    # admin panel
    def admin_menu(self):
        if self.current_role != "Admin":
            print("Access denied.")
            return
        while True:
            print("\nAdmin menu")
            print("1. Users")
            print("2. Auctions")
            print("3. Bids")
            print("4. Payments")
            print("5. Shipments")
            print("6. Statistics")
            print("7. Back")
            choice = input("Choice: ")
            if choice == "1":
                print(run_query("SELECT * FROM users"))
            elif choice == "2":
                print(run_query("SELECT * FROM auction"))
            elif choice == "3":
                print(run_query("SELECT * FROM bid"))
            elif choice == "4":
                print(run_query("SELECT * FROM payment"))
            elif choice == "5":
                print(run_query("SELECT * FROM shipment"))
            elif choice == "6":
                self.system_stats()
            elif choice == "7":
                break

    def system_stats(self):
        users = run_query(
            "SELECT COUNT(*) AS c FROM users"
        )[0]["c"]
        items = run_query(
            "SELECT COUNT(*) AS c FROM item"
        )[0]["c"]
        auctions = run_query(
            "SELECT COUNT(*) AS c FROM auction"
        )[0]["c"]
        bids = run_query(
            "SELECT COUNT(*) AS c FROM bid"
        )[0]["c"]
        payments = run_query(
            "SELECT COUNT(*) AS c FROM payment"
        )[0]["c"]
        shipments = run_query(
            "SELECT COUNT(*) AS c FROM shipment"
        )[0]["c"]
        print("\nStats")
        print("Users:", users)
        print("Items:", items)
        print("Auctions:", auctions)
        print("Bids:", bids)
        print("Payments:", payments)
        print("Shipments:", shipments)

# main
if __name__ == "__main__":
    app = AuctionCLI()
    app.login()
    app.main_menu()
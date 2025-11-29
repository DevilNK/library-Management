from datetime import datetime, timedelta
class BorrowManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS borrow(
            borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id INTEGER,
            book_id INTEGER,
            borrow_date VARCHAR(20),
            due_date VARCHAR(20),
            return_date VARCHAR(20),
            fine_amount REAL DEFAULT 0.0,
            borrow_status VARCHAR(15), 
            FOREIGN KEY(member_id) REFERENCES member(member_id),
            FOREIGN KEY(book_id) REFERENCES book(book_id)
        );
        """
        self.db.execute_query(query)

    def issue_book(self, member_id, book_id, days_to_return=14):
        check_query = "SELECT quantity_available, title FROM book WHERE book_id = ?"
        book_data = self.db.fetch_all(check_query, (book_id,))
        
        if not book_data:
            print("Error: Book ID not found.")
            return
        qty, title = book_data[0]
        if qty <= 0:
            print(f"Sorry, '{title}' is out of stock.")
            return

        today = datetime.now().strftime("%Y-%m-%d")
        due = (datetime.now() + timedelta(days=days_to_return)).strftime("%Y-%m-%d")

        try:
            # Issue Book
            self.db.execute_query("INSERT INTO borrow(member_id, book_id, borrow_date, due_date, borrow_status) VALUES(?, ?, ?, ?, 'Issued')", 
                                  (member_id, book_id, today, due))
            # Decrease Stock
            self.db.execute_query("UPDATE book SET quantity_available = quantity_available - 1 WHERE book_id = ?", (book_id,))
            self.db.commit()
            print(f"SUCCESS: '{title}' issued to Member ID {member_id}. Due: {due}")
        except Exception as e:
            print(f"Transaction Failed: {e}")

    def return_book(self, borrow_id):
        record = self.db.fetch_all("SELECT book_id, due_date, borrow_status FROM borrow WHERE borrow_id = ?", (borrow_id,))
        if not record:
            print("Transaction ID not found.")
            return
        book_id, due_date_str, status = record[0]
        
        if status == 'Returned':
            print("Book already returned.")
            return

        today_obj = datetime.now()
        due_obj = datetime.strptime(due_date_str, "%Y-%m-%d")
        fine = max(0, (today_obj - due_obj).days * 10.0) # 10 currency units fine per day

        try:
            # Update Return
            self.db.execute_query("UPDATE borrow SET return_date = ?, borrow_status = 'Returned', fine_amount = ? WHERE borrow_id = ?", 
                                  (today_obj.strftime("%Y-%m-%d"), fine, borrow_id))
            # Increase Stock
            self.db.execute_query("UPDATE book SET quantity_available = quantity_available + 1 WHERE book_id = ?", (book_id,))
            self.db.commit()
            print(f"Book returned. Fine: {fine}")
        except Exception as e:
            print(f"Error: {e}")

    def show_active_borrows(self):
        query = """
        SELECT br.borrow_id, m.name, b.title, br.borrow_date, br.due_date
        FROM borrow br
        JOIN member m ON br.member_id = m.member_id
        JOIN book b ON br.book_id = b.book_id
        WHERE br.borrow_status = 'Issued'
        """
        records = self.db.fetch_all(query)
        if not records:
            print("No books currently issued.")
            return
        print("\n" + "="*90)
        print(f"{'ID':<5} {'Member Name':<20} {'Book Title':<30} {'Issued':<15} {'Due':<15}")
        print("-" * 90)
        for r in records:
            print(f"{r[0]:<5} {r[1][:18]:<20} {r[2][:28]:<30} {r[3]:<15} {r[4]:<15}")
        print("="*90 + "\n")
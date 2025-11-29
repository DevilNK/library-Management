
import sys
from datetime import datetime
from database import DatabaseManager
from scripts.employee import EmployeeManager
from scripts.book import BookManager, Book
from scripts.member import MemberManager, Member
from scripts.borrow import BorrowManager

def main():
    db = DatabaseManager("library.db")
    
    try:
        db.connect()
        # Initialize
        emp_mgr = EmployeeManager(db)
        book_mgr = BookManager(db)
        mem_mgr = MemberManager(db)
        borrow_mgr = BorrowManager(db)
        
        # Setup Tables
        emp_mgr.create_table()
        book_mgr.create_tables()
        mem_mgr.create_table()
        borrow_mgr.create_table()

        while True:
            print("\n=== LIBRARY MANAGEMENT SYSTEM ===")
            print("1. Employee Module")
            print("2. Book Module")
            print("3. Member Module")
            print("4. Circulation (Issue/Return)")
            print("5. Exit")
            
            choice = input("\nEnter choice: ")

            if choice == "1":
                print("\n[Employee Menu]\n1. Import CSV\n2. View All")
                if input("Choice: ") == "1": emp_mgr.import_from_csv("emp.csv")
                else: emp_mgr.show_all_employees()

            elif choice == "2":
                print("\n[Book Menu]")
                print("1. Import CSV")
                print("2. Add Manual Book")
                print("3. View/Search Books")
                print("4. CATEGORY MANAGEMENT")
                c = input("Choice: ")
                if c == "1": book_mgr.import_books_from_csv("books.csv")
                elif c == "2":
                    t = input("Title: ")
                    a= input("Author: ")
                    if not t and not a:
                        print("Title and Author cannot be empty.")
                        continue
                    else:
                        fields = [
                                    ("Category ID: ", 1),
                                    ("ISBN: ", "N/A"),
                                    ("Publisher: ", "Self"),
                                    ("Year: ", 2024),
                                    ("Language: ", "Eng"),
                                    ("Pages: ", 100),
                                    ("Copies: ", 5),
                                    ("Location: ", "Desk")]
                        # book_mgr.add_book(Book(t, input("Author: "), 1, "N/A", "Self", 2024, "Eng", 100, 5, "Desk"))
                        book_mgr.add_book(Book(t,a,*[(i := input(p)) and type(d)(i) or d for p, d in fields]))
                elif c == "3": 
                    print("\n1. View All (Paged)")
                    print("2. Search by Keyword")
                    sc = input("Choice: ")
                    if sc == "1": book_mgr.show_all_books()
                    elif sc == "2": book_mgr.search_books(input("Enter Keyword: "))
                elif c == "4":
                    print("\n[Category Manager]")
                    print("1. View Categories")
                    print("2. Add New Category")
                    print("3. Rename Category")
                    print("4. Move Book to Category")
                    print("5. View Books in Category")
                    
                    cc = input("Choice: ")
                    
                    if cc == "1":
                        cats = book_mgr.get_all_categories()
                        print("\nID | Name")
                        print("---|-----")
                        for cat in cats: print(f"{cat[0]}  | {cat[1]}")
                        
                    elif cc == "2":
                        name = input("New Category Name: ")
                        book_mgr.add_category(name)
                        
                    elif cc == "3":
                        try:
                            cid = int(input("Enter Category ID to Rename: "))
                            new_name = input("New Name: ")
                            book_mgr.update_category(cid, new_name)
                        except ValueError: print("Invalid ID")
                        
                    elif cc == "4":
                        try:
                            bid = int(input("Enter Book ID: "))
                            cid = int(input("Enter NEW Category ID: "))
                            book_mgr.assign_book_to_category(bid, cid)
                        except ValueError: print("Invalid ID")

                    elif cc == "5":
                        try:
                            cid = int(input("Enter Category ID to view books: "))
                            book_mgr.show_books_by_category(cid)
                        except ValueError:
                            print("Invalid ID")

            elif choice == "3":
                # print("\n[Member Menu]\n1. Add Member\n2. View Members")
                # if input("Choice: ") == "1":
                #     mem_mgr.add_member(Member(input("Name: "), "Address", input("Phone: "), "email@test.com", "ID", "000", datetime.now().strftime("%Y-%m-%d")))
                # else: mem_mgr.show_all_members()
                print("\n[Member Menu]")
                print("1. Add New Member (Full Details)")
                print("2. Update Member Details")
                print("3. Deactivate Member")
                print("4. View All Members")
                c = input("Choice: ")
                
                if c == "1":
                    print("\n--- Register New Member ---")
                    name = input("Full Name: ")
                    address = input("Address: ")
                    phone = input("Contact Number: ")
                    email = input("Email ID: ")
                    id_type = input("ID Proof Type (e.g., Student ID/Aadhaar): ")
                    id_num = input("ID Proof Number: ")
                    join_date = datetime.now().strftime("%Y-%m-%d")
                    
                    new_mem = Member(name, address, phone, email, id_type, id_num, join_date)
                    mem_mgr.add_member(new_mem)
                
                elif c == "2":
                    try:
                        mid = int(input("Enter Member ID to Update: "))
                        # Fetch existing to show user what they are changing
                        old_data = mem_mgr.get_member_by_id(mid)
                        if old_data:
                            print(f"Editing Member: {old_data[1]}")
                            # Ask for new values, press Enter to keep old ones
                            n_name = input(f"Name ({old_data[1]}): ") or old_data[1]
                            n_addr = input(f"Address ({old_data[2]}): ") or old_data[2]
                            n_phone = input(f"Phone ({old_data[3]}): ") or old_data[3]
                            n_email = input(f"Email ({old_data[4]}): ") or old_data[4]
                            n_status = input(f"Status ({old_data[8]}): ") or old_data[8]
                            
                            mem_mgr.update_member(mid, n_name, n_phone, n_email, n_addr, n_status)
                        else:
                            print("Member ID not found.")
                    except ValueError:
                        print("Invalid ID.")

                elif c == "3":
                    try:
                        mid = int(input("Enter Member ID to Deactivate: "))
                        confirm = input(f"Are you sure you want to block ID {mid}? (y/n): ")
                        if confirm.lower() == 'y':
                            mem_mgr.deactivate_member(mid)
                    except ValueError:
                        print("Invalid ID.")

                elif c == "4":
                    mem_mgr.show_all_members()
            elif choice == "4":
                print("\n[Circulation]\n1. Issue Book\n2. Return Book\n3. View Active")
                c = input("Choice: ")
                try:
                    if c == "1": borrow_mgr.issue_book(int(input("Member ID: ")), int(input("Book ID: ")))
                    elif c == "2": borrow_mgr.return_book(int(input("Borrow ID: ")))
                    elif c == "3": borrow_mgr.show_active_borrows()
                except ValueError: print("Invalid Input.")

            elif choice == "5":
                break

    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
    finally:
        if db.connection:
            db.close()

if __name__ == "__main__":
    main()
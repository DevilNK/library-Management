
import csv

class Book:
    def __init__(self, title, author, category_id, isbn, publisher, 
                 publication_year, language, pages, quantity_total, 
                 shelf_location, quantity_available=None):
        self.title = title
        self.author = author
        self.category_id = category_id
        self.isbn = isbn
        self.publisher = publisher
        self.publication_year = publication_year
        self.language = language
        self.pages = pages
        self.quantity_total = quantity_total
        self.shelf_location = shelf_location
        
        if quantity_available is None:
            self.quantity_available = quantity_total
        else:
            self.quantity_available = quantity_available

class BookManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def create_tables(self):
        query_cat = """
        CREATE TABLE IF NOT EXISTS category(
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            category_name VARCHAR(50) NOT NULL UNIQUE,
            description TEXT
        );
        """
        self.db.execute_query(query_cat)

        query_book = """
        CREATE TABLE IF NOT EXISTS book(
            book_id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(100) NOT NULL,
            author VARCHAR(100) NOT NULL,
            category_id INTEGER,
            isbn VARCHAR(20) UNIQUE,
            publisher VARCHAR(100),
            publication_year INTEGER,
            language VARCHAR(20),
            pages INTEGER,
            quantity_total INTEGER NOT NULL,
            quantity_available INTEGER NOT NULL,
            shelf_location VARCHAR(20),
            FOREIGN KEY (category_id) REFERENCES category(category_id)
        );
        """
        self.db.execute_query(query_book)
        self.add_category("General", "Default category")
    
    def get_all_categories(self):
        return self.db.fetch_all("SELECT category_id, category_name, description FROM category")
    def add_category(self, name, description=""):
        try:
            exists = self.db.fetch_all("SELECT category_id FROM category WHERE category_name = ?", (name,))
            if not exists:
                query = "INSERT INTO category(category_name, description) VALUES (?, ?)"
                self.db.execute_query(query, (name, description))
                self.db.commit()
        except Exception as e:
            print(f"Error adding category: {e}")

    def get_default_category_id(self):
        res = self.db.fetch_all("SELECT category_id FROM category WHERE category_name = 'General'")
        return res[0][0] if res else 1

    def add_book(self, book, auto_commit=True):
        query = """
        INSERT INTO book(title, author, category_id, isbn, publisher, 
                         publication_year, language, pages, quantity_total, 
                         quantity_available, shelf_location)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (book.title, book.author, book.category_id, book.isbn, 
                  book.publisher, book.publication_year, book.language, 
                  book.pages, book.quantity_total, book.quantity_available, 
                  book.shelf_location)
        try:
            self.db.execute_query(query, values)
            if auto_commit:
                self.db.commit()
                print(f"Book '{book.title}' added.")
        except Exception as e:
            if "UNIQUE constraint" not in str(e):
                print(f"Error adding book {book.title}: {e}")

    def import_books_from_csv(self, filename):
        
        print("Starting Book Import... Please wait.")
        default_cat_id = self.get_default_category_id()
        
        try:
            # detect delimiter
            with open(filename, "r", encoding="latin-1", errors="replace") as f_check:
                first_line = f_check.readline()
                delimiter = ';' if ';' in first_line else ','
            
            with open(filename, "r", encoding="latin-1", errors="replace") as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                count = 0
                for row in reader:
                    raw_year = row.get("Year-Of-Publication", "") or row.get("Publication-Year", "") or row.get("Year", "")
                    try:
                        year = int(raw_year)
                    except (ValueError, TypeError):
                        year = 0

                    # Determine category name from common headers if present
                    category_name = ""
                    for key in ("Category", "Book-Category", "Genre"):
                        if row.get(key):
                            category_name = row.get(key).strip()
                            break

                    # If category provided, ensure it exists and get id
                    if category_name:
                        cat_res = self.db.fetch_all("SELECT category_id FROM category WHERE category_name = ?", (category_name,))
                        if not cat_res:
                            # create category
                            try:
                                self.add_category(category_name)
                            except Exception:
                                pass
                            cat_res = self.db.fetch_all("SELECT category_id FROM category WHERE category_name = ?", (category_name,))
                        category_id = cat_res[0][0] if cat_res else default_cat_id
                    else:
                        category_id = default_cat_id

                    new_book = Book(
                        title=(row.get("Book-Title") or row.get("Title") or "Unknown")[:99],
                        author=(row.get("Book-Author") or row.get("Author") or "Unknown")[:99],
                        category_id=category_id,
                        isbn=(row.get("ISBN") or row.get("Isbn") or "")[:19],
                        publisher=(row.get("Publisher") or "Unknown")[:49],
                        publication_year=year,
                        language=(row.get("Language") or "English"),
                        pages=0,
                        quantity_total=int(row.get("Quantity", 5) or 5),
                        shelf_location=(row.get("Shelf", "Stack A") or "Stack A")
                    )
                    self.add_book(new_book, auto_commit=False)
                    count += 1
                    if count % 1000 == 0:
                        print(f"Processed {count} books...")

            self.db.commit()
            print(f"SUCCESS: Imported {count} books!")
        except FileNotFoundError:
            print("Error: File not found.")
        except Exception as e:
            print(f"Error importing books: {e}")

    def show_all_books(self):
        limit = 100  # <--- CHANGED TO 100 PER PAGE
        offset = 0
        
        while True:
            # Fetch batch of 100
            query = """
            SELECT b.book_id, b.title, b.author, c.category_name, b.quantity_available, b.shelf_location
            FROM book b
            LEFT JOIN category c ON b.category_id = c.category_id
            LIMIT ? OFFSET ?
            """
            books = self.db.fetch_all(query, (limit, offset))
            
            if not books:
                if offset == 0:
                    print("No books found.")
                else:
                    print("\n--- End of List ---")
                break

            header_fmt = "{:<5} {:<30} {:<20} {:<15} {:<8} {:<10}"
            print("\n" + "="*100)
            print(header_fmt.format("ID", "Title", "Author", "Category", "Avail", "Loc"))
            print("-" * 100)

            for b in books:
                b_id, title, author, cat, avail, loc = b
                cat_name = str(cat) if cat else "N/A"
                print(header_fmt.format(b_id, str(title).strip()[:28], str(author).strip()[:18], 
                                        cat_name[:14], avail, loc))
            print("="*100)
            
            # Show current range
            print(f"\nDisplaying rows {offset + 1} - {offset + len(books)}")
            
            # Check if we reached the end
            if len(books) < limit:
                print("--- End of List ---")
                break

            # Navigation
            cont = input("Press [Enter] for next 100, or 'q' to Quit: ")
            if cont.lower() == 'q':
                break
            
            # Move offset forward
            offset += limit

    def show_books_by_category(self, category_id):
        """
        Print books for a given category_id.
        """
        # Get category name for header
        cat_res = self.db.fetch_all("SELECT category_name FROM category WHERE category_id = ?", (category_id,))
        cat_name = cat_res[0][0] if cat_res else f"ID {category_id}"

        query = """
        SELECT book_id, title, author, quantity_available, shelf_location
        FROM book
        WHERE category_id = ?
        ORDER BY title
        LIMIT 1000
        """
        books = self.db.fetch_all(query, (category_id,))

        if not books:
            print(f"No books found for category: {cat_name}")
            return

        header_fmt = "{:<6} {:<40} {:<25} {:<7} {:<10}"
        print("\n" + "="*100)
        print(f"Category: {cat_name}")
        print(header_fmt.format("ID", "Title", "Author", "Avail", "Loc"))
        print("-" * 100)

        for b in books:
            b_id, title, author, avail, loc = b
            print(header_fmt.format(b_id, str(title).strip()[:38], str(author).strip()[:23], avail, loc))
        print("="*100 + "\n")

    def search_books(self, keyword):
        keyword = f"%{keyword}%"
        query = """
        SELECT b.book_id, b.title, b.author, c.category_name, b.quantity_available
        FROM book b
        LEFT JOIN category c ON b.category_id = c.category_id
        WHERE b.title LIKE ? OR b.author LIKE ?
        LIMIT 20
        """
        books = self.db.fetch_all(query, (keyword, keyword))
        
        if not books:
            print("No matching books found.")
            return

        print(f"\nFound {len(books)} matches:")
        print("-" * 80)
        print(f"{'ID':<5} {'Title':<40} {'Author':<20} {'Avail':<5}")
        print("-" * 80)
        for b in books:
            print(f"{b[0]:<5} {b[1][:38]:<40} {b[2][:18]:<20} {b[4]:<5}")
        print("-" * 80 + "\n")

    def update_category(self, category_id, new_name):
        try:
            self.db.execute_query(
                "UPDATE category SET category_name = ? WHERE category_id = ?",
                (new_name, category_id)
            )
            self.db.commit()
            print(f"Category {category_id} updated to '{new_name}'.")
        except Exception as e:
            print(f"Error updating category: {e}")

    def assign_book_to_category(self, book_id, category_id):
        try:
            self.db.execute_query(
                "UPDATE book SET category_id = ? WHERE book_id = ?",
                (category_id, book_id)
            )
            self.db.commit()
            print(f"Book {book_id} moved to category {category_id}.")
        except Exception as e:
            print(f"Error assigning book to category: {e}")
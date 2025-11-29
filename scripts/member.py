from datetime import datetime

class Member:
    def __init__(self, name, address, contact_number, email, id_proof_type, 
                 id_proof_number, membership_date, active_status="Active"):
        self.name = name
        self.address = address
        self.contact_number = contact_number
        self.email = email
        self.id_proof_type = id_proof_type
        self.id_proof_number = id_proof_number
        self.membership_date = membership_date
        self.active_status = active_status

class MemberManager:
    def __init__(self, db_manager):
        self.db = db_manager

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS member(
            member_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(50) NOT NULL,
            address TEXT,
            contact_number VARCHAR(20) NOT NULL,
            email VARCHAR(50),
            id_proof_type VARCHAR(20),
            id_proof_number VARCHAR(30) UNIQUE,
            membership_date VARCHAR(20),
            active_status VARCHAR(10) DEFAULT 'Active'
        );
        """
        self.db.execute_query(query)

    def add_member(self, member):
        query = """
        INSERT INTO member(name, address, contact_number, email, id_proof_type, 
                           id_proof_number, membership_date, active_status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        values = (member.name, member.address, member.contact_number, member.email,
                  member.id_proof_type, member.id_proof_number, member.membership_date,
                  member.active_status)
        try:
            self.db.execute_query(query, values)
            self.db.commit()
            print(f"Success: Member '{member.name}' registered.")
        except Exception as e:
            print(f"Error registering member: {e}")

    def update_member(self, m_id, name, phone, email, address, status):
        query = """
        UPDATE member 
        SET name=?, contact_number=?, email=?, address=?, active_status=?
        WHERE member_id=?
        """
        try:
            self.db.execute_query(query, (name, phone, email, address, status, m_id))
            self.db.commit()
            print(f"Member {m_id} updated successfully.")
        except Exception as e:
            print(f"Error updating: {e}")

    def deactivate_member(self, m_id):
        query = "UPDATE member SET active_status='Deactivated' WHERE member_id=?"
        try:
            self.db.execute_query(query, (m_id,))
            self.db.commit()
            print(f"Member {m_id} has been Deactivated.")
        except Exception as e:
            print(f"Error: {e}")

    def get_member_by_id(self, m_id):
        # Helper to fetch current details before updating
        res = self.db.fetch_all("SELECT * FROM member WHERE member_id=?", (m_id,))
        return res[0] if res else None

    def show_all_members(self):
        members = self.db.fetch_all("SELECT * FROM member")
        
        if not members:
            print("No members found.")
            return

        # Added Address and ID Proof to the view
        header_fmt = "{:<5} {:<20} {:<15} {:<25} {:<15} {:<10}"
        print("\n" + "="*100)
        print(header_fmt.format("ID", "Name", "Phone", "Email", "ID Proof", "Status"))
        print("-" * 100)
        # print(f"\n{'='*100}\n{'ID':<5} {'Name':<20} {'Phone':<15} {'Email':<25} {'ID Proof':<15} {'Status':<10}\n{'-'*100}")

        for m in members:
            # m = (id, name, address, phone, email, id_type, id_num, date, status)
            m_id, name, _, phone, email, _, id_num, _, status = m
            
            # Clean data
            name = str(name).strip()[:18]
            phone = str(phone).strip()[:14]
            email = str(email).strip()[:24]
            id_num = str(id_num).strip()[:14]
            
            print(header_fmt.format(m_id, name, phone, email, id_num, status))
        print("="*100 + "\n")
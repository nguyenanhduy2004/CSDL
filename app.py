import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date, timedelta

# Kết nối và khởi tạo cơ sở dữ liệu SQLite
def init_db():
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    
    # Tạo bảng books
    c.execute('''CREATE TABLE IF NOT EXISTS books (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 title TEXT NOT NULL,
                 author TEXT NOT NULL,
                 year INTEGER,
                 genre TEXT,
                 status TEXT DEFAULT 'Available',
                 borrower_id INTEGER,
                 borrow_date TEXT,
                 return_date TEXT)''')
    
    # Tạo bảng borrowers
    c.execute('''CREATE TABLE IF NOT EXISTS borrowers (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 email TEXT,
                 phone TEXT)''')
    
    # Thêm dữ liệu mẫu cho books nếu bảng rỗng
    c.execute("SELECT COUNT(*) FROM books")
    if c.fetchone()[0] == 0:
        sample_books = [
            ("To Kill a Mockingbird", "Harper Lee", 1960, "Fiction", "Available", None, None, None),
            ("1984", "George Orwell", 1949, "Dystopian", "Available", None, None, None),
            ("Pride and Prejudice", "Jane Austen", 1813, "Romance", "Available", None, None, None),
            ("The Great Gatsby", "F. Scott Fitzgerald", 1925, "Fiction", "Available", None, None, None),
            ("The Catcher in the Rye", "J.D. Salinger", 1951, "Fiction", "Available", None, None, None)
        ]
        c.executemany("INSERT INTO books (title, author, year, genre, status, borrower_id, borrow_date, return_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", sample_books)
    
    # Thêm dữ liệu mẫu cho borrowers nếu bảng rỗng
    c.execute("SELECT COUNT(*) FROM borrowers")
    if c.fetchone()[0] == 0:
        sample_borrowers = [
            ("Nguyễn Văn A", "nguyenvana@example.com", "0123456789"),
            ("Trần Thị B", "tranthib@example.com", "0987654321"),
            ("Lê Văn C", "levanc@example.com", "0912345678")
        ]
        c.executemany("INSERT INTO borrowers (name, email, phone) VALUES (?, ?, ?)", sample_borrowers)
    
    conn.commit()
    conn.close()

# Gọi hàm khởi tạo cơ sở dữ liệu
init_db()

# Hàm lấy tất cả sách
def get_all_books():
    conn = sqlite3.connect('library.db')
    query = '''SELECT b.id, b.title, b.author, b.year, b.genre, b.status, 
                     br.name as borrowed_by, b.borrow_date, b.return_date 
              FROM books b 
              LEFT JOIN borrowers br ON b.borrower_id = br.id'''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Hàm lấy tất cả người mượn
def get_all_borrowers():
    conn = sqlite3.connect('library.db')
    query = "SELECT id, name, email, phone FROM borrowers"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Hàm thêm sách mới
def add_book(title, author, year, genre):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("INSERT INTO books (title, author, year, genre, status) VALUES (?, ?, ?, ?, 'Available')", 
              (title, author, year, genre))
    conn.commit()
    conn.close()

# Hàm thêm người mượn mới
def add_borrower(name, email, phone):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("INSERT INTO borrowers (name, email, phone) VALUES (?, ?, ?)", 
              (name, email, phone))
    conn.commit()
    conn.close()

# Hàm cập nhật sách
def update_book(book_id, title, author, year, genre):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("UPDATE books SET title = ?, author = ?, year = ?, genre = ? WHERE id = ?", 
              (title, author, year, genre, book_id))
    conn.commit()
    conn.close()

# Hàm xóa sách
def delete_book(book_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("DELETE FROM books WHERE id = ?", (book_id,))
    conn.commit()
    conn.close()

# Hàm xóa người mượn
def delete_borrower(borrower_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("DELETE FROM borrowers WHERE id = ?", (borrower_id,))
    conn.commit()
    conn.close()

# Hàm mượn sách
def borrow_book(book_id, borrower_id, return_date):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    borrow_date = datetime.now().strftime("%Y-%m-%d")
    c.execute("UPDATE books SET status = 'Borrowed', borrower_id = ?, borrow_date = ?, return_date = ? WHERE id = ?", 
              (borrower_id, borrow_date, return_date, book_id))
    conn.commit()
    conn.close()

# Hàm trả sách
def return_book(book_id):
    conn = sqlite3.connect('library.db')
    c = conn.cursor()
    c.execute("UPDATE books SET status = 'Available', borrower_id = NULL, borrow_date = NULL, return_date = NULL WHERE id = ?", 
              (book_id,))
    conn.commit()
    conn.close()

# Giao diện Streamlit
st.title("Ứng Dụng Quản Lý Thư Viện Sách")

# Tabs để quản lý các chức năng
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Danh Sách Sách", "Thêm Sách", "Cập Nhật Sách", "Mượn/Trả Sách", "Quản Lý Người Mượn"])

# Tab 1: Hiển thị danh sách sách
with tab1:
    st.header("Danh Sách Sách")
    search_term = st.text_input("Tìm kiếm sách (theo tiêu đề hoặc tác giả):")
    books_df = get_all_books()
    
    if search_term:
        books_df = books_df[books_df['title'].str.contains(search_term, case=False, na=False) | 
                           books_df['author'].str.contains(search_term, case=False, na=False)]
    
    st.dataframe(books_df, use_container_width=True)

# Tab 2: Thêm sách mới
with tab2:
    st.header("Thêm Sách Mới")
    with st.form("add_book_form"):
        title = st.text_input("Tiêu đề sách")
        author = st.text_input("Tác giả")
        year = st.number_input("Năm xuất bản", min_value=1500, max_value=2025, step=1)
        genre = st.text_input("Thể loại")
        submitted = st.form_submit_button("Thêm Sách")
        
        if submitted:
            if title and author:
                add_book(title, author, year, genre)
                st.success("Đã thêm sách thành công!")
            else:
                st.error("Vui lòng nhập tiêu đề và tác giả!")

# Tab 3: Cập nhật sách
with tab3:
    st.header("Cập Nhật Sách")
    books_df = get_all_books()
    book_ids = books_df['id'].tolist()
    selected_book_id = st.selectbox("Chọn ID sách để cập nhật", book_ids)
    
    if selected_book_id:
        book = books_df[books_df['id'] == selected_book_id].iloc[0]
        with st.form("update_book_form"):
            title = st.text_input("Tiêu đề sách", value=book['title'])
            author = st.text_input("Tác giả", value=book['author'])
            year = st.number_input("Năm xuất bản", min_value=1500, max_value=2025, step=1, value=int(book['year']))
            genre = st.text_input("Thể loại", value=book['genre'])
            submitted = st.form_submit_button("Cập Nhật Sách")
            
            if submitted:
                if title and author:
                    update_book(selected_book_id, title, author, year, genre)
                    st.success("Đã cập nhật sách thành công!")
                else:
                    st.error("Vui lòng nhập tiêu đề và tác giả!")
        
        if st.button("Xóa Sách", key=f"delete_book_{selected_book_id}"):
            delete_book(selected_book_id)
            st.success("Đã xóa sách thành công!")
            st.experimental_rerun()

# Tab 4: Mượn/Trả sách
with tab4:
    st.header("Mượn/Trả Sách")
    books_df = get_all_books()
    book_ids = books_df['id'].tolist()
    selected_book_id = st.selectbox("Chọn ID sách để mượn/trả", book_ids, key="borrow_book_select")
    
    if selected_book_id:
        book = books_df[books_df['id'] == selected_book_id].iloc[0]
        st.write(f"**Trạng thái hiện tại**: {book['status']}")
        if book['status'] == 'Borrowed':
            st.write(f"**Người mượn**: {book['borrowed_by']}")
            st.write(f"**Ngày mượn**: {book['borrow_date']}")
            st.write(f"**Ngày trả**: {book['return_date']}")
        
        if book['status'] == 'Available':
            with st.form("borrow_book_form"):
                borrowers_df = get_all_borrowers()
                borrower_options = {row['name']: row['id'] for row in borrowers_df.to_dict('records')}
                borrower_name = st.selectbox("Chọn người mượn", list(borrower_options.keys()))
                max_return_date = date.today() + timedelta(days=15)
                return_date = st.date_input("Ngày trả dự kiến", min_value=date.today(), max_value=max_return_date)
                submitted = st.form_submit_button("Mượn Sách")
                
                if submitted:
                    if borrower_name:
                        borrower_id = borrower_options[borrower_name]
                        borrow_book(selected_book_id, borrower_id, return_date.strftime("%Y-%m-%d"))
                        st.success("Đã ghi nhận mượn sách!")
                        st.experimental_rerun()
                    else:
                        st.error("Vui lòng chọn người mượn!")
        
        if book['status'] == 'Borrowed':
            if st.button("Trả Sách", key=f"return_{selected_book_id}"):
                return_book(selected_book_id)
                st.success("Đã ghi nhận trả sách!")
                st.experimental_rerun()

# Tab 5: Quản lý người mượn
with tab5:
    st.header("Quản Lý Người Mượn")
    borrowers_df = get_all_borrowers()
    st.subheader("Danh Sách Người Mượn")
    st.dataframe(borrowers_df, use_container_width=True)
    
    # Thêm người mượn mới
    st.subheader("Thêm Người Mượn Mới")
    with st.form("add_borrower_form"):
        name = st.text_input("Tên người mượn")
        email = st.text_input("Email")
        phone = st.text_input("Số điện thoại")
        submitted = st.form_submit_button("Thêm Người Mượn")
        
        if submitted:
            if name:
                add_borrower(name, email, phone)
                st.success("Đã thêm người mượn thành công!")
            else:
                st.error("Vui lòng nhập tên người mượn!")
    
    # Xóa người mượn
    st.subheader("Xóa Người Mượn")
    borrower_ids = borrowers_df['id'].tolist()
    selected_borrower_id = st.selectbox("Chọn ID người mượn để xóa", borrower_ids, key="delete_borrower_select")
    
    if selected_borrower_id:
        if st.button("Xóa Người Mượn", key=f"delete_borrower_{selected_borrower_id}"):
            # Kiểm tra xem người mượn có đang mượn sách không
            books_df = get_all_books()
            if selected_borrower_id in books_df['borrower_id'].values:
                st.error("Không thể xóa! Người mượn đang mượn sách.")
            else:
                delete_borrower(selected_borrower_id)
                st.success("Đã xóa người mượn thành công!")
                st.experimental_rerun()
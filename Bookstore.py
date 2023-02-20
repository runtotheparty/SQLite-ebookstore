import sqlite3
import pandas as pd

#Create book object to input into database
class Book:

    def __init__(self, ident, title, author, qty):
        self.ident = ident
        self.title = title
        self.author = author
        self.qty = qty

    # if looking at specific objects is needed
    def __str__(self):
        return (f"""This {self.title}, there are {self.qty} remaining. The product code is by {self.author}. The
        ID is {self.ident}\n""")

def new_book():
    try:
        temp_ident = int(input("Please enter the new or updated book's identity number: "))
    except ValueError:
        print("Oops, looks like that input was invalid. Make sure you input only numbers into identity")
        return
    temp_title = input("Please enter the new or updated book's title: ")
    temp_author = input("Please enter the new or updated book's author: ")

    try:
        temp_qty = int(input("Please enter the new or updated book's quantity: "))
    except ValueError:
        print("Oops, looks like that input was invalid. Make sure you input only numbers into quantity")
        return
    new_book = Book(temp_ident, temp_title, temp_author, temp_qty)
    return new_book

def add_book(add_book):
    # Connect to the database
    db = sqlite3.connect("bookstore.db")
    cursor = db.cursor()

    add_book_list = [add_book]
    # Loop through the list of books and insert each one into the database
    try:
        for i in add_book_list:
            cursor.execute("""
                    INSERT INTO books (id, title, author, qty)
                    VALUES (?,?,?,?)""", (i.ident, i.title, i.author, i.qty))
        # Commit the changes to the database
        db.commit()
        print("Books successfully added")

    except:
        db.rollback()
        print("Error adding books")


    finally:
        # Close the cursor and the connection to the database
        cursor.close()
        db.close()
        return

def update_book():
    print("We are taking you to the search function to search for the book you would like to update.\n")
    id_num = search_book()
    if id_num == "":
        return
    db = sqlite3.connect("bookstore.db")
    cursor = db.cursor()
    up_book = new_book()

    try:
        cursor.execute("""UPDATE books SET id = ?, title = ?, author = ?, qty = ? WHERE id = ?
        """, (up_book.ident, up_book.title, up_book.author, up_book.qty, id_num))
        db.commit()
        print(f"The book with original id {id_num} has been updated to the following:")
        print(f"New ID: {up_book.ident}")
        print(f"Title: {up_book.title}")
        print(f"Author: {up_book.author}")
        print(f"Quantity: {up_book.qty}")
    except:
        db.rollback()
        print("Error updating book database. Please make sure your original identity number matched a book in the system")

    finally:
        db.close()
        return


def delete_book():
    db = sqlite3.connect("bookstore.db")
    cursor = db.cursor()
    print("We are taking you to the search function to search for the book you would like to delete.\n")
    id_num = search_book()
    if id_num is None:
        db.rollback()
        print("Returning to menu")
        db.close()
        return
    else:
        y_or_n = input("Are you sure you want to delete this book? y/n: ")
        y_or_n = y_or_n.casefold()
        if y_or_n == "y":
            try:
                cursor.execute("DELETE FROM books WHERE id = ?", (id_num,))
                db.commit()
                print(f"Book with id {id_num} has been deleted from the database.")

            except:
                db.rollback()
                print("Error deleting book. Please check the id number and try again.")

            finally:
                db.close()
                return
        elif y_or_n == "n":
            db.rollback()
            print("Returning to menu")
            db.close()
        else:
            db.rollback()
            print("Unrecognised input. Returning to menu")
            db.close()


def search_book():
    # Prompt the user for the search criteria
    search = input("Enter the author, title, or id of the book you want to search for: ")


    try:
        # Connect to the database
        db = sqlite3.connect("bookstore.db")
        cursor = db.cursor()

        # LIKE functionality from https://www.sqlitetutorial.net/sqlite-like/
        cursor.execute(f"SELECT * FROM books WHERE author LIKE '%{search}%' OR title LIKE '%{search}%' OR id = '{search}'")

        # Fetch all the results
        results = cursor.fetchall()


        if len(results) == 0:
            print("No results found or invalid search")
        # Print the results
        else:
            for result in results:
                id, title, author, qty = result
                print(f"ID: {id}\nAuthor: {author}\nTitle: {title}\nQuantity: {qty}\n")
                cursor.close()
                db.close()
                return id
    except:
        db.rollback()
        print ("No results found or invalid search")
        cursor.close()
        db.close()






# Start of Program

# Connect to the database
db = sqlite3.connect("bookstore.db")
cursor = db.cursor()


# Create the table (if it doesn't already exist)
cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER NOT NULL PRIMARY KEY,
            title TEXT,
            author TEXT,
            qty INTEGER NOT NULL
        )""")
db.commit()

# read list from external sheet if applicable
while True:
    y_or_n = input("Would you like to populate the database from a spreadsheet? "
                   "(recommended if database first time set up) y/n: ")
    y_or_n = y_or_n.casefold()
    if y_or_n == "y":
        spreadsheet = input("Please enter the name of the spreadsheet you would like to add books from: ")
        try:
            df = pd.read_excel(f'{spreadsheet}.xlsx')

            books = []

            # Iterate through the rows of the Excel sheet
            for i, row in df.iterrows():
                # Create a Book object for each row, using the values from the Excel sheet removing any whitespace
                title = row['title'].strip().replace('\n', ' ')
                author = row['author'].strip().replace('\n', ' ')
                ident = row['id']
                qty = row['qty']
                book = Book(ident, title, author, qty)
                # Add the "Book" object to the list of books
                books.append(book)

        except FileNotFoundError:
            print(f"No spreadsheet found called {spreadsheet}")


        try:
            # Loop through the list of books and insert each one into the database
            for book in books:
                cursor.execute("""
                   INSERT INTO books (id, title, author, qty)
                   VALUES (?,?,?,?)""", (book.ident, book.title, book.author, book.qty))

            # Commit the changes to the database
            db.commit()
            print("Books successfully added")
        except sqlite3.Error as e:
            db.rollback()
            print("Error adding books")
            break

        finally:
            #Close the cursor and the connection to the database
            cursor.close()
            db.close()
            break
    elif y_or_n == "n":
        print("You have chosen not to use a spreadsheet.")
        break
# Menu
while True:
    menu = input("""Please select from the following menu:
    'a' - Add a book to the database.
    'u' - Update an entry in the database. 
    's' - Search the database for a book.
    'd' - Delete a book from the database.
    '0' - To exit:
    """)


    menu = menu.casefold()

    if menu == 'a':
        nb = new_book()
        add_book(nb)
        continue


    elif menu == 'u':
        update_book()


    elif menu == 's':
        # search_type = input("Please enter a search query: 'author', the 'id' number, or 'title': ")
        # search_query = input("Thanks, now enter what you're looking for: ")
        search_book()

    elif menu == 'd':
        delete_book()

    elif menu == '0':
        break

    else:
        print("Oops, your input was not recognised. Please try again.")

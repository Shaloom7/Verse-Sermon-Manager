import tkinter as tk
from tkinter import scrolledtext, messagebox, font, simpledialog
import sqlite3
import datetime

DATABASE_FILE = 'bible.sqlite'
NOTES_DATABASE_FILE = 'user_notes.sqlite'


# List of books in the Bible (Standard order - 66 books)
BOOK_NAMES = [
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy", "Joshua", "Judges", "Ruth",
    "1 Samuel", "2 Samuel", "1 Kings", "2 Kings", "1 Chronicles", "2 Chronicles", "Ezra", "Nehemiah",
    "Esther", "Job", "Psalms", "Proverbs", "Ecclesiastes", "Song of Solomon", "Isaiah", "Jeremiah",
    "Lamentations", "Ezekiel", "Daniel", "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah", "Nahum",
    "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi", "Matthew", "Mark", "Luke", "John", "Acts",
    "Romans", "1 Corinthians", "2 Corinthians", "Galatians", "Ephesians", "Philippians", "Colossians",
    "1 Thessalonians", "2 Thessalonians", "1 Timothy", "2 Timothy", "Titus", "Philemon", "Hebrews", "James",
    "1 Peter", "2 Peter", "1 John", "2 John", "3 John", "Jude", "Revelation"
]


def initialize_notes_database():
    """
    Initializes the user notes database and recreates the 'notes' table
    with 'note_id' column as primary key.
    WARNING: This will DELETE all existing notes in the 'notes' table!
    """
    conn = None
    try:
        conn = sqlite3.connect(NOTES_DATABASE_FILE)
        cursor = conn.cursor()

        
        cursor.execute("DROP TABLE IF EXISTS notes;")
        conn.commit()
        print("Existing 'notes' table dropped (if it existed).")

        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                note_id INTEGER PRIMARY KEY AUTOINCREMENT, -- note_id as PRIMARY KEY AUTOINCREMENT now in CREATE TABLE
                book_number INTEGER NOT NULL,
                chapter_number INTEGER NOT NULL,
                verse_number INTEGER NOT NULL,
                note_text TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        print("Notes database initialized with 'notes' table (note_id as primary key).")


    except sqlite3.Error as e:
        print(f"Error initializing/recreating notes database: {e}")
    finally:
        if conn:
            conn.close()



def connect_to_bible_db():
    """Connects to the bible.sqlite database and returns a connection object."""
    connection = None  
    try:
        connection = sqlite3.connect(DATABASE_FILE)
        return connection
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None  


def get_verse_text(connection, book_number, chapter_number, verse_number):
    """
    Retrieves the text of a Bible verse from the database.

    Args:
        connection: SQLite database connection object.
        book_number: Integer representing the book of the Bible.
        chapter_number: Integer representing the chapter number.
        verse_number: Integer representing the verse number.

    Returns:
        str: The text of the Bible verse, or None if not found or error.
    """
    cursor = None  
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT text FROM verses WHERE book = ? AND chapter = ? AND verse = ?",
            (book_number, chapter_number, verse_number),
        )
        result = cursor.fetchone()  
        if result:
            
            return result[0]
        else:
            return None  
    except sqlite3.Error as e:
        print(f"Database query error: {e}")
        return None
    finally:
        if cursor:  
            cursor.close()


# Adding Notes funtion
def add_note(book_number, chapter_number, verse_number, note_text):
    """
    Adds a user note to the notes database for a specific Bible verse.
    Modified to work with auto-incrementing note_id.

    Args:
        book_number: Book number of the verse.
        chapter_number: Chapter number of the verse.
        verse_number: Verse number of the verse.
        note_text: The text content of the note.

    Returns:
        bool: True if note was added successfully, False otherwise.
    """
    conn = None
    try:
        conn = sqlite3.connect(NOTES_DATABASE_FILE)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO notes (book_number, chapter_number, verse_number, note_text) VALUES (?, ?, ?, ?)",
            (book_number, chapter_number, verse_number, note_text),
        )
        conn.commit()
        return True 
    except sqlite3.Error as e:
        print(f"Error adding note to database: {e}")
        return False 
    finally:
        if conn:
            conn.close()


# Updating notes function
def update_note(book_number, chapter_number, verse_number):
    """
    Allows the user to update a *specific* note for a Bible verse, selected from a list of existing notes.
    Uses note_id to update the chosen note.

    Args:
        book_number: Book number of the verse.
        chapter_number: Chapter number of the verse.
        verse_number: Verse number of the verse.

    Returns:
        bool: True if a note was updated successfully, False otherwise.
    """
    conn = None
    try:
        conn = sqlite3.connect(NOTES_DATABASE_FILE)
        cursor = conn.cursor()

        # 1. Retrieve existing notes for the verse (including note_id)
        cursor.execute(
            "SELECT note_id, note_text, created_at FROM notes WHERE book_number = ? AND chapter_number = ? AND verse_number = ?",
            (book_number, chapter_number, verse_number),
        )
        notes_data = cursor.fetchall()
        print(f"DEBUG: Notes Data Retrieved: {notes_data}") 

        if not notes_data: 
            return False, "No notes found for this verse to update." 

        # 2. Format notes for user selection and display in dialog
        note_choices_text = "Select a note to update (enter number):\n"
        note_choices_dict = {} 
        for index, note_info in enumerate(notes_data):
            note_id, note_text, created_at = note_info
            choice_number = index + 1 
            note_choices_text += f"{choice_number}. {note_text} (Created: {created_at})\n"
            note_choices_dict[str(choice_number)] = note_id 
            print(f"DEBUG: Note Choices Text:\n{note_choices_text}") 
            print(f"DEBUG: Note Choices Dict: {note_choices_dict}") 

        # 3. Prompt user to choose a note to update
        print("DEBUG: About to show note selection dialog...") 
        chosen_note_choice_str = simpledialog.askstring("Update Note", note_choices_text, parent=root)
        print(f"DEBUG: User Note Choice: {chosen_note_choice_str}") 

        if not chosen_note_choice_str: 
            return False, "Note update cancelled."

        if chosen_note_choice_str not in note_choices_dict: 
            return False, "Invalid note choice selected."

        selected_note_id = note_choices_dict[chosen_note_choice_str] 

        # 4. Prompt user for new note text for the *selected* note
        new_note_text = simpledialog.askstring("Update Note", "Enter new text for the selected note:", parent=root)

        if not new_note_text: 
            return False, "Note update cancelled (no new text entered)."

        # 5. Update the *specific* note using note_id in WHERE clause
        cursor.execute(
            "UPDATE notes SET note_text = ?, created_at = CURRENT_TIMESTAMP WHERE note_id = ?",
            (new_note_text, selected_note_id), 
        )
        conn.commit()
        return True, "Note updated successfully!" 


    except sqlite3.Error as e:
        print(f"Database error in update_note: {e}")
        return False, f"Database error: {e}" 
    except Exception as e:
        print(f"Error in update_note: {e}")
        return False, f"Error: {e}" 
    finally:
        if conn:
            conn.close()


# Deleting Notes
def delete_notes_for_verse(book_number, chapter_number, verse_number):
    """
    Allows the user to delete *specific* notes for a Bible verse, selected from a list of existing notes.
    Uses note_id to delete the chosen note(s).

    Args:
        book_number: Book number of the verse.
        chapter_number: Chapter number of the verse.
        verse_number: Verse number of the verse.

    Returns:
        bool: True if note(s) were deleted successfully, False otherwise.
    """
    conn = None
    try:
        conn = sqlite3.connect(NOTES_DATABASE_FILE)
        cursor = conn.cursor()

        # 1. Retrieve existing notes for the verse (including note_id)
        cursor.execute(
            "SELECT note_id, note_text, created_at FROM notes WHERE book_number = ? AND chapter_number = ? AND verse_number = ?",
            (book_number, chapter_number, verse_number),
        )
        notes_data = cursor.fetchall()

        if not notes_data:
            return False, "No notes found for this verse to delete."

        # 2. Format notes for user selection and display in dialog
        note_choices_text = "Select note(s) to delete (enter numbers separated by commas, e.g., 1,3):\n"
        note_choices_dict = {}
        for index, note_info in enumerate(notes_data):
            note_id, note_text, created_at = note_info
            choice_number = index + 1
            note_choices_text += f"{choice_number}. {note_text} (Created: {created_at})\n"
            note_choices_dict[str(choice_number)] = note_id

        # 3. Prompt user to choose note(s) to delete (allow multiple selection with commas)
        chosen_note_choices_str = simpledialog.askstring("Delete Notes", note_choices_text, parent=root)

        if not chosen_note_choices_str:
            return False, "Note deletion cancelled."

        chosen_note_choice_list = [choice.strip() for choice in chosen_note_choices_str.split(',')]
        selected_note_ids_to_delete = []

        for choice_str in chosen_note_choice_list:
            if choice_str not in note_choices_dict:
                return False, f"Invalid note choice: {choice_str}. Please enter valid numbers from the list." 
            selected_note_ids_to_delete.append(note_choices_dict[choice_str])

        if not selected_note_ids_to_delete:
            return False, "No valid notes selected for deletion."

        # 4. Perform Deletion of *specific* notes using note_ids in WHERE clause (using IN operator)
        placeholders = ','.join(['?'] * len(selected_note_ids_to_delete)) 
        cursor.execute(
            f"DELETE FROM notes WHERE note_id IN ({placeholders})",
            selected_note_ids_to_delete,
        )
        conn.commit()
        return True, f"{cursor.rowcount} note(s) deleted successfully!"


    except sqlite3.Error as e:
        print(f"Database error in delete_notes_for_verse: {e}")
        return False, f"Database error: {e}"
    except Exception as e:
        print(f"Error in delete_notes_for_verse: {e}")
        return False, f"Error: {e}"
    finally:
        if conn:
            conn.close()



def view_notes_for_verse(book_number, chapter_number, verse_number):
    """
    Retrieves and prints user notes for a specific Bible verse from the notes database.

    Args:
        book_number: Book number of the verse.
        chapter_number: Chapter number of the verse.
        verse_number: Verse number of the verse.
    """
    conn = None
    try:
        conn = sqlite3.connect(NOTES_DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT note_text, created_at FROM notes WHERE book_number = ? AND chapter_number = ? AND verse_number = ?",
            (book_number, chapter_number, verse_number),
        )
        notes = cursor.fetchall() 

        if notes:
            print("\n--- Notes for this verse ---")
            for note in notes:
                note_text, created_at = note
                print(f"- {note_text} (Created at: {created_at})")
            print("--- End of Notes ---\n")
        else:
            print("\nNo notes found for this verse.\n")

    except sqlite3.Error as e:
        print(f"Error retrieving notes from database: {e}")
    finally:
        if conn:
            conn.close()



def get_verse_button_click():
    """
    Handles the event when the "Get Verse" button is clicked.
    Retrieves and displays the Bible verse and associated notes in the GUI.
    """
    book_name = book_var.get() 
    chapter_str = chapter_var.get() 
    verse_str = verse_var.get()     

    try:
        chapter_num = int(chapter_str) 
        verse_num = int(verse_str)     

        if not (1 <= chapter_num <= 176 and 1 <= verse_num <= 176): 
            messagebox.showerror("Input Error", "Please enter valid chapter and verse numbers.")
            return 

        book_number = BOOK_NAMES.index(book_name) + 1 

        verse_text = get_verse_text(db_connection, book_number, chapter_num, verse_num) 
        notes = view_notes_for_verse_gui(book_number, chapter_num, verse_num) 

        verse_text_area.config(state=tk.NORMAL) 
        verse_text_area.delete("1.0", tk.END)   
        if verse_text:
            verse_text_area.insert(tk.END, verse_text) 
        else:
            verse_text_area.insert(tk.END, "Verse not found.") 
        verse_text_area.config(state=tk.DISABLED) 

        notes_text_area.config(state=tk.NORMAL) 
        notes_text_area.delete("1.0", tk.END) 
        if notes: 
            notes_text_area.insert(tk.END, notes) 
        else:
            notes_text_area.insert(tk.END, "No notes for this verse.") 
        notes_text_area.config(state=tk.DISABLED) 


    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integer values for Chapter and Verse.")
    except Exception as e: 
        messagebox.showerror("Error", f"An error occurred: {e}") 



def view_notes_for_verse_gui(book_number, chapter_number, verse_number):
    """
    Retrieves user notes for a specific Bible verse from the notes database and formats them as a single string for GUI display.

    Args:
        book_number: Book number of the verse.
        chapter_number: Chapter number of the verse.
        verse_number: Verse number of the verse.

    Returns:
        str: A formatted string containing all notes for the verse, or None if no notes found or error.
    """
    conn = None
    try:
        conn = sqlite3.connect(NOTES_DATABASE_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT note_text, created_at FROM notes WHERE book_number = ? AND chapter_number = ? AND verse_number = ?",
            (book_number, chapter_number, verse_number),
        )
        notes_data = cursor.fetchall() 

        if notes_data:
            notes_string = "--- Notes for this verse ---\n" 
            for note_text, created_at in notes_data:
                notes_string += f"- {note_text} (Created at: {created_at})\n" 
            notes_string += "--- End of Notes ---\n"
            return notes_string 
        else:
            return None

    except sqlite3.Error as e:
        print(f"Error retrieving notes from database: {e}")
        return None
    finally:
        if conn:
            conn.close()


def add_note_button_click():
    """
    Handles the event when the "Add Note" button is clicked.
    Adds a new user note to the database for the currently selected Bible verse.
    """
    book_name = book_var.get()
    chapter_str = chapter_var.get()
    verse_str = verse_var.get()

    try:
        chapter_num = int(chapter_str)
        verse_num = int(verse_str)

        if not (1 <= chapter_num <= 176 and 1 <= verse_num <= 176): 
            messagebox.showerror("Input Error", "Please enter valid chapter and verse numbers before adding a note.")
            return

        book_number = BOOK_NAMES.index(book_name) + 1

        # Get note text from user
        note_text = simpledialog.askstring("Add Note", f"Enter your note for {book_name} {chapter_num}:{verse_num}:", parent=root)

        if note_text: 
            if add_note(book_number, chapter_num, verse_num, note_text): 
                messagebox.showinfo("Success", "Note added successfully!")
                notes = view_notes_for_verse_gui(book_number, chapter_num, verse_num) 
                notes_text_area.config(state=tk.NORMAL)
                notes_text_area.delete("1.0", tk.END)
                notes_text_area.insert(tk.END, notes or "No notes for this verse.") 
                notes_text_area.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Error", "Failed to add note to database.")
        else: 
            messagebox.showinfo("Info", "Note addition cancelled or no note text entered.")


    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integer values for Chapter and Verse.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")



def update_note_button_click():
    """
    Handles the event when the "Update Note" button is clicked.
    Updates the user note(s) in the database for the currently selected Bible verse.
    Prompts the user for new note text to replace the existing note(s).
    """
    book_name = book_var.get()
    chapter_str = chapter_var.get()
    verse_str = verse_var.get()

    try:
        chapter_num = int(chapter_str)
        verse_num = int(verse_str)

        if not (1 <= chapter_num <= 176 and 1 <= verse_num <= 176): 
            messagebox.showerror("Input Error", "Please enter valid chapter and verse numbers before updating notes.")
            return

        book_number = BOOK_NAMES.index(book_name) + 1

        
        new_note_text = tk.simpledialog.askstring("Update Note", f"Enter new note text to REPLACE existing note(s) for {book_name} {chapter_num}:{verse_num}:", parent=root)

        if new_note_text: 
            if update_note(book_number, chapter_num, verse_num): 
                messagebox.showinfo("Success", "Note(s) updated successfully!")
                notes = view_notes_for_verse_gui(book_number, chapter_num, verse_num) 
                notes_text_area.config(state=tk.NORMAL)
                notes_text_area.delete("1.0", tk.END)
                notes_text_area.insert(tk.END, notes or "No notes for this verse.") 
                notes_text_area.config(state=tk.DISABLED)
            else:
                messagebox.showerror("Error", "Failed to update note(s) in database (or no notes found to update).") 
        else: 
            messagebox.showinfo("Info", "Note update cancelled or no new note text entered.")


    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integer values for Chapter and Verse.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")





def delete_notes_button_click():
    """
    Handles the event when the "Delete Notes" button is clicked.
    Deletes specific user notes for the currently selected Bible verse, 
    selected from a list, after confirmation.
    Modified to handle return tuple from delete_notes_for_verse and for individual note deletion.
    """
    book_name = book_var.get()
    chapter_str = chapter_var.get()
    verse_str = verse_var.get()

    try:
        chapter_num = int(chapter_str)
        verse_num = int(verse_str)

        if not (1 <= chapter_num <= 176 and 1 <= verse_num <= 176): 
            messagebox.showerror("Input Error", "Please enter valid chapter and verse numbers before deleting notes.")
            return

        book_number = BOOK_NAMES.index(book_name) + 1

        # Call the rewritten delete_notes_for_verse function
        success, message = delete_notes_for_verse(book_number, chapter_num, verse_num) 

        if success: # Deletion was successful
            messagebox.showinfo("Success", message) 
            notes = view_notes_for_verse_gui(book_number, chapter_num, verse_num) 
            notes_text_area.config(state=tk.NORMAL)
            notes_text_area.delete("1.0", tk.END)
            notes_text_area.insert(tk.END, notes or "No notes for this verse.") 
            notes_text_area.config(state=tk.DISABLED)
        else: 
            messagebox.showerror("Error", message) 


    except ValueError:
        messagebox.showerror("Input Error", "Please enter valid integer values for Chapter and Verse.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")




if __name__ == "__main__":
    db_connection = connect_to_bible_db()
    initialize_notes_database()
    if db_connection:
        try:
            # --- GUI Setup ---
            root = tk.Tk() 
            root.title("Python Bible App") 

            main_font = font.Font(family="Helvetica", size=12) 

            # --- Book Selection ---
            book_label = tk.Label(root, text="Book:", font=main_font)
            book_label.grid(row=0, column=0, padx=5, pady=5, sticky="e") 

            book_var = tk.StringVar(root) 
            book_var.set(BOOK_NAMES[0]) 
            book_dropdown = tk.OptionMenu(root, book_var, *BOOK_NAMES) 
            book_dropdown.config(font=main_font)
            book_dropdown.grid(row=0, column=1, padx=5, pady=5, sticky="w") 

            # --- Chapter Selection ---
            chapter_label = tk.Label(root, text="Chapter:", font=main_font)
            chapter_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")

            chapter_var = tk.StringVar(root)
            chapter_entry = tk.Entry(root, textvariable=chapter_var, width=5, font=main_font) 
            chapter_entry.grid(row=0, column=3, padx=5, pady=5, sticky="w")

            # --- Verse Selection ---
            verse_label = tk.Label(root, text="Verse:", font=main_font)
            verse_label.grid(row=0, column=4, padx=5, pady=5, sticky="e")

            verse_var = tk.StringVar(root)
            verse_entry = tk.Entry(root, textvariable=verse_var, width=5, font=main_font) 
            verse_entry.grid(row=0, column=5, padx=5, pady=5, sticky="w")

            # --- Get Verse Button ---
            get_verse_button = tk.Button(root, text="Get Verse", font=main_font, command=get_verse_button_click) 
            get_verse_button.grid(row=0, column=6, padx=10, pady=5)

            # --- Verse Text Display ---
            verse_text_label = tk.Label(root, text="Verse Text:", font=main_font)
            verse_text_label.grid(row=1, column=0, padx=5, pady=5, sticky="nw") 

            verse_text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=10, font=main_font) 
            verse_text_area.grid(row=2, column=0, columnspan=7, padx=10, pady=5, sticky="nsew") 
            verse_text_area.config(state=tk.DISABLED) 

            # --- Notes Display ---
            notes_label = tk.Label(root, text="Notes:", font=main_font)
            notes_label.grid(row=3, column=0, padx=5, pady=5, sticky="nw")

            notes_text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=5, font=main_font) 
            notes_text_area.grid(row=4, column=0, columnspan=7, padx=10, pady=5, sticky="nsew")
            notes_text_area.config(state=tk.DISABLED) 

            # --- Note Action Buttons ---
            add_note_button = tk.Button(root, text="Add Note", font=main_font, command=add_note_button_click) 
            add_note_button.grid(row=5, column=0, padx=5, pady=5, sticky="w")

            update_note_button = tk.Button(root, text="Update Note", font=main_font, command=update_note_button_click)
            update_note_button.grid(row=5, column=1, padx=5, pady=5, sticky="w")

            delete_note_button = tk.Button(root, text="Delete Notes", font=main_font, command=delete_notes_button_click) 
            delete_note_button.grid(row=5, column=2, padx=5, pady=5, sticky="w")


            # Configure grid to make area expand when window is resized
            root.grid_columnconfigure(6, weight=1) 
            root.grid_rowconfigure(2, weight=1) 
            root.grid_rowconfigure(4, weight=1) 


            root.mainloop() 

        finally:
            db_connection.close()
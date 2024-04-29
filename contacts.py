from tkinter import Tk, Button, PhotoImage, Label, LabelFrame, W, E,N,S,CENTER, Entry, END,StringVar ,Scrollbar,Toplevel
from tkinter import ttk
import sqlite3

class Contacts:
    db_filename = 'contacts.db'
    def __init__(self, root):
        self.root = root
        self.create_gui()
        ttk.style = ttk.Style()
        ttk.style.configure("Treeview", font=('helvetica',10))
        ttk.style.configure("Treeview.Heading", font=('helvetica',12, 'bold'))

    def execute_db_query(self, query, parameters=()):
        with sqlite3.connect(self.db_filename) as conn:
            print(conn)
            print('You have successfully connected to the Database')
            cursor = conn.cursor()
            query_result = cursor.execute(query, parameters)
            conn.commit()
        return query_result


    def create_gui(self):
        self.create_left_icon()
        self.create_label_frame()
        self.create_message_area()
        self.create_tree_view()
        self.create_scrollbar()
        self.create_bottom_buttons()
        self.view_contacts()
        

    def create_left_icon(self):
        photo = PhotoImage(file='icons/logo.gif')
        label = Label(image=photo)
        label.image = photo
        label.grid(row=0, column=0)
    
    def create_label_frame(self):
        labelframe = LabelFrame(self.root, text='Create New Contact',bg="sky blue",font="helvetica 10")
        labelframe.grid(row=0, column=1, padx=8, pady=8, sticky='ew')
        Label(labelframe, text='Name:',bg="green",fg="white").grid(row=1, column=1, sticky=W, pady=2,padx=15)
        self.namefield = Entry(labelframe)
        self.namefield.grid(row=1, column=2, sticky=W, padx=5, pady=2)
        Label(labelframe, text='Email:',bg="brown",fg="white").grid(row=2, column=1, sticky=W,  pady=2,padx=15)
        self.emailfield = Entry(labelframe)
        self.emailfield.grid(row=2, column=2, sticky=W, padx=5, pady=2)
        Label(labelframe, text='Number:',bg="black",fg="white").grid(row=3,column=1, sticky=W,  pady=2,padx=15)
        self.numfield = Entry(labelframe)
        self.numfield.grid(row=3, column=2, sticky=W, padx=5, pady=2)
        Button(labelframe, text='Add Contact', command= self.add_new_contact,bg="blue",fg="white").grid(row=4, column=2, sticky=E, padx=5, pady=5)
    
    def create_message_area(self):
        self.message = Label(text='', fg='red')
        self.message.grid(row=3, column=1, sticky=W)

    def create_tree_view(self):
        self.tree = ttk.Treeview(height=10, columns=("email","number"), style='Treeview')
        self.tree.grid(row=6, column=0, columnspan=3)
        self.tree.heading('#0', text='Name', anchor=W)
        self.tree.heading("email", text='Email Address', anchor=W)
        self.tree.heading("number", text='Contact Number', anchor=W)

    def create_scrollbar(self):
        self.scrollbar = Scrollbar(orient='vertical',command=self.tree.yview)
        self.scrollbar.grid(row=6,column=3,rowspan=10,sticky='sn') 

    def create_bottom_buttons(self):
        Button(text='Delete Selected', command=self.on_delete_selected_button_click, bg="red", fg="white").grid(row=8, column=0, sticky=W,pady=10,padx=20)
        Button(text='Modify Selected', command=self.on_modify_selected_button_click,bg="purple",fg="white").grid(row=8, column=2, sticky=W)
        
    def add_new_contact(self):
        if self.new_contacts_validated():
            query = 'INSERT INTO contacts_list VALUES(NULL,?, ?,?)'
            parameters = (self.namefield.get(),self.emailfield.get(), self.numfield.get())
            self.execute_db_query(query, parameters)
            self.message['text'] = 'New Contact {} Added'.format(self.namefield.get())
            self.namefield.delete(0, END)
            self.emailfield.delete(0, END)
            self.numfield.delete(0, END)
            self.view_contacts()
        else:
            self.message['text'] = 'Name,Email and Number cannot be blank'
            self.view_contacts()

    def on_delete_selected_button_click(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'No item selected to delete.'
            return
        self.delete_contacts()
    
    def on_modify_selected_button_click(self):
        self.message['text'] = ''
        try:
            self.tree.item(self.tree.selection())['values'][0]
        except IndexError as e:
            self.message['text'] = 'No item selected to modify.'
            return
        self.open_modify_window()
    
    def new_contacts_validated(self):
        return len(self.namefield.get()) != 0 and len(self.emailfield.get()) != 0 and len(self.numfield.get()) != 0

    def view_contacts(self):
        items = self.tree.get_children()
        for item in items:
            self.tree.delete(item)
        query = 'SELECT * FROM contacts_list ORDER BY name desc'
        contact_entries = self.execute_db_query(query)
        for row in contact_entries:
                self.tree.insert('', 0, text=row[1], values=(row[2],row[3]))

    def delete_contacts(self):
        self.message["text"] = ''
        name = self.tree.item(self.tree.selection())['text']
        query = 'delete from contacts_list where name= ?'
        self.execute_db_query(query, (name,))
        self.message['text'] = 'Contacts for {} deleted'.format(name)
        self.view_contacts()

    def open_modify_window(self):
        self.transient = Toplevel()
        self.transient.geometry("260x115")
        self.transient.resizable(width=False, height=False)
        self.transient.title('Update Contact')
        Button(self.transient, text='Modify Name', command=self.update_name).grid(row=2, column=1)
        Button(self.transient, text='Modify Email Address', command=self.update_email).grid(row=3, column=1)
        Button(self.transient, text='Modify number', command=self.update_number).grid(row=4, column=1)
        
    # for update name
    def update_name(self):
        for i in self.transient.winfo_children():
            i.destroy()
        old_name = self.tree.item(self.tree.selection())['text']
        email = self.tree.item(self.tree.selection())['values'][0]
        number= self.tree.item(self.tree.selection())['values'][1]
        Label(self.transient, text='Old name:').grid(row=0, column=1)
        Entry(self.transient, textvariable=StringVar(self.transient, value=old_name), state='readonly').grid(row=0, column=2)
        Label(self.transient, text='Email-Address: ').grid(row=1, column=1)
        Entry(self.transient, textvariable=StringVar(self.transient, value=email), state='readonly').grid(row=1, column=2)
        Label(self.transient, text='Contact Number: ').grid(row=2, column=1)
        Entry(self.transient, textvariable=StringVar(self.transient, value=number), state='readonly').grid(row=2, column=2)
        Label(self.transient, text='New Name:').grid(row=3, column=1)
        new_name_entry_widget = Entry(self.transient)
        new_name_entry_widget.grid(row=3, column=2)
        Button(self.transient, text='Update Contact', command=lambda: self.update_contacts_for_name(new_name_entry_widget.get(), number, old_name)).grid(row=4, column=2, sticky=E)
        self.transient.mainloop()
    def update_contacts_for_name(self,newname, number, oldname):
        query = 'update contacts_list set name = ? where number = ? and name = ?'
        parameters = (newname, number, oldname)
        self.execute_db_query(query, parameters)
        self.transient.destroy()
        self.message['text'] = 'Name of {} modified'.format(newname)
        self.view_contacts()

    # for update email 
    def update_email(self):
        for i in self.transient.winfo_children():
            i.destroy()
        name = self.tree.item(self.tree.selection())['text']
        old_email = self.tree.item(self.tree.selection())['values'][0]
        number= self.tree.item(self.tree.selection())['values'][1]
        Label(self.transient, text='Name:').grid(row=0, column=1)
        Entry(self.transient, textvariable=StringVar(self.transient, value=name), state='readonly').grid(row=0, column=2)
        Label(self.transient, text='Old Email-Address: ').grid(row=1, column=1)
        Entry(self.transient, textvariable=StringVar(self.transient, value=old_email), state='readonly').grid(row=1, column=2)
        Label(self.transient, text='Contact Number: ').grid(row=2, column=1)
        Entry(self.transient, textvariable=StringVar(self.transient, value=number), state='readonly').grid(row=2, column=2)

        Label(self.transient, text='New Email-Address: ').grid(row=3, column=1)
        new_email_address_entry_widget= Entry(self.transient)
        new_email_address_entry_widget.grid(row=3, column=2)
        Button(self.transient, text='Update Contact', command=lambda: self.update_contacts_for_email(new_email_address_entry_widget.get(), number, name)).grid(row=4, column=2, sticky=E)
        self.transient.mainloop()
    
    def update_contacts_for_email(self, new_email, number, name):
        query = 'update contacts_list set email= ? where number = ? and name = ?'
        parameters = (new_email, number, name)
        self.execute_db_query(query, parameters)
        self.transient.destroy()
        self.message['text'] = 'Phone number of {} modified'.format(name)
        self.view_contacts()

    # for update number
    def update_number(self):
        for i in self.transient.winfo_children():
            i.destroy()
        name = self.tree.item(self.tree.selection())['text']
        email = self.tree.item(self.tree.selection())['values'][0]
        old_number= self.tree.item(self.tree.selection())['values'][1]
        Label(self.transient, text='Name:').grid(row=0, column=1)
        Entry(self.transient, textvariable=StringVar(self.transient, value=name), state='readonly').grid(row=0, column=2)
        Label(self.transient, text='Email-Address: ').grid(row=1, column=1)
        Entry(self.transient, textvariable=StringVar(self.transient, value=email), state='readonly').grid(row=1, column=2)
        Label(self.transient, text='Old Number: ').grid(row=2, column=1)
        Entry(self.transient, textvariable=StringVar(self.transient, value=old_number), state='readonly').grid(row=2, column=2)

        Label(self.transient, text='New Contact Number: ').grid(row=3, column=1)
        new_phone_number_entry_widget= Entry(self.transient)
        new_phone_number_entry_widget.grid(row=3, column=2)
        Button(self.transient, text='Update Contact', command=lambda: self.update_contacts_for_number(new_phone_number_entry_widget.get(), old_number, name)).grid(row=4, column=2, sticky=E)
        self.transient.mainloop()
    
    def update_contacts_for_number(self, new_number, old_number, name):
        query = 'update contacts_list set number= ? where number = ? and name = ?'
        parameters = (new_number, old_number, name)
        self.execute_db_query(query, parameters)
        self.transient.destroy()
        self.message['text'] = 'Phone number of {} modified'.format(name)
        self.view_contacts() 


if __name__ == '__main__':
    root = Tk()
    root.title('My Contacts List')
    root.geometry("650x450")
    root.resizable(width=False, height=False)
    application = Contacts(root)
    root.mainloop()
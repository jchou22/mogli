import os
import urllib.request
import tkinter as tk
from tkinter import *
from tkinter import ttk

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mogli.settings')
django.setup()

from .pages import MainPage

from mogli.models import User as UserModel, Product, TransactionHistory, UserCard


times = 3
session = []
session2 = {}
LARGE_FONT = ("Verdana", 12)

def getipaddress():
    try:
        ip_address = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    except:
        import socket
        ip_address = socket.gethostbyname(socket.gethostname())
    return ip_address

# Base Login
class Login(Frame):

    def __init__(self, parent, controller, kind, model, register_view, return_view):
        tk.Frame.__init__(self, parent)
        
        
        self.username = StringVar()
        self.password = StringVar()
        self.controller = controller
        self.kind = kind
        self.model = model
        self.register_view = register_view
        self.return_view = return_view

        label = Label(self, text=f"Login {self.kind}", font=LARGE_FONT)
        label.pack(pady=10, padx=10)
        username_label = Label(self, text="Username *", width="20")
        username_label.pack()

        self.username_entry = Entry(self, textvariable=self.username,
            width="20")
        self.username_entry.pack()

        password_label = Label(self, text="Password *", width="20")
        password_label.pack()

        self.password_entry = Entry(self, textvariable=self.password, 
            show="*", width="20")
        self.password_entry.pack()

        self.info_label = Label(self, text="")
        self.info_label.pack()

        login_btn = Button(self, text="Login", height="1", width="17", 
            command=self.login)
        login_btn.pack()

        self.menu_bar = MenuBar(parent, controller)

        mainPage_btn = Button(self, text="Back to Home",
            command=lambda: controller.show_frame(MainPage))
        mainPage_btn.pack(side=tk.RIGHT, padx=5, pady=5)

        register_btn = Button(self, text="Register",
            command=lambda: controller.show_frame(self.register_view))
        register_btn.pack(side=tk.RIGHT)
        self.controller = controller

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username:
            try:
                target = self.model.objects.get(username=username)
                if target.password == password:
                    print("Login")
                    
                    self.menu_bar.show()
                    self.controller.show_frame(self.return_view)
                    session.append((username, target.email_id, 1))
                    session2['user'] = target
                else:
                    print("Password incorrect")

            except Exception as e:
                print(f"Admin doesn't exist: {e}")
        else:
            print(f"Field username empty")

        self.username_entry.delete(0, END)
        self.password_entry.delete(0, END)
        print(f"Login: {username} - {password}")


class PopUp(tk.Toplevel):

    def __init__(self, message):
        width, height = (400, 200)
        super().__init__()
        self.title("Message")
        self.geometry(f"{width}x{height}")
        self.attributes("-topmost", True)

        space = Label(self, text='', height='5')
        space.pack()

        label = Label(self, text=message)
        label.pack()

        self.lift()



# The Menubar
class MenuBar(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

    def show(self):
        menubar = Menu(self)
        mainmenu = Menu(menubar, tearoff=0)
        productmenu = Menu(menubar, tearoff=0)
        historymenu = Menu(menubar, tearoff=0)

        productmenu.add_command(label="View products", command=self.view_products)

        historymenu.add_command(label="View transaction history", 
            command=self.view_transaction_history)

        mainmenu.add_command(label="Logout", command=self.do_nothing)

        menubar.add_cascade(label="Products", menu=productmenu)
        menubar.add_cascade(label="History", menu=historymenu)

        # Label(self, text="Hello").pack()

        self.controller.config(menu=menubar)

    def do_nothing(self):
        create_product_screen = tk.Toplevel(self.controller)
        create_product_screen.title("New Product")
        create_product_screen.geometry("300x250")
        button = Button(create_product_screen, text="Hello, world!")
        button.pack()

    def view_transaction_history(self):
        width, height = (1200, 256)

        window = tk.Toplevel(self.controller)
        window.title("Transaction history")
        window.geometry(f"{width}x{height}")

        cols = ('Username', 'Email', 'Product Name', 'Cost', 'IP Address', 'DATE')

        listBox = ttk.Treeview(window, columns=cols, show='headings')

        for col in cols:
            listBox.heading(col, text=col)
        listBox.grid(row=2, column=5, columnspan=2)

        for history in TransactionHistory.objects.filter(user=session2['user']):
            listBox.insert("", "end", values=(
                history.user.username, history.user.email_id,
                history.product.product_name, history.cost,
                history.ip_address, history.created_at
            ))

    def view_products(self):

        width, height = (810, 300)

        window = tk.Toplevel(self.controller)
        window.title("Products")
        window.geometry(f"{width}x{height}")

        cols = ('Product ID', 'Product', 'Cost', 'IMAGE')

        self.listBox = ttk.Treeview(window, columns=cols, show='headings')
        self.listBox.bind('<ButtonRelease-1>', self.selectItem)

        for col in cols:
            self.listBox.heading(col, text=col)
        self.listBox.grid(row=2, column=5, columnspan=2)

        for product in Product.objects.all():
            self.listBox.insert("", "end", values=(
                product.id_product, product.product_name,
                str(product.cost), product.image
            ))
    
    def selectItem(self, a):

        selected = self.listBox.focus()
        item = self.listBox.item(selected)
        print(item)
        self.buy_product(item)

    def buy_product(self, item):

        width, height = (610, 450)

        buywin = tk.Toplevel()
        buywin.title("Buy product")
        buywin.geometry(f"{width}x{height}")
        buywin.attributes("-topmost", True)

        product_id = item['values'][0]
        product_name = item['values'][1]
        product_price = item['values'][2]
        product_image = item['values'][3]
        self.product_id = product_id

        wintitle_label = Label(buywin, text="Buy product", font=LARGE_FONT, bg='gray', width='70', height='2')
        wintitle_label.pack()

        separator1 = Label(buywin, text='', height='2')
        separator1.pack()

        product_id_label = Label(buywin, text=f'Product ID: {product_id}')
        product_id_label.pack()

        product_name_label = Label(buywin, text=f'Product name: {product_name}')
        product_name_label.pack()

        product_price_label = Label(buywin, text=f'Product price: {product_price}')
        product_price_label.pack()

        product_image_label = Label(buywin, text=f'Product image: {product_image}')
        product_image_label.pack()

        separator2 = Label(buywin, text='', height='2')
        separator2.pack()

        credit_card_label = Label(buywin, text="Credit card number *", width="20")
        credit_card_label.pack()

        self.credit_card = StringVar()
        self.credit_card_entry = Entry(buywin, textvariable=self.credit_card,
            width="20")
        self.credit_card_entry.pack()

        separator3 = Label(buywin, text='', height='5')
        separator3.pack()

        buy_button = Button(buywin, text="Buy", command=self.finish_buying)
        buy_button.pack()

        buywin.lift()

    def finish_buying(self):
        global times
        product_id = self.product_id
        product = Product.objects.get(id_product=product_id)
        user = session2['user']
        credit_card = self.credit_card_entry.get()
        ip_address = getipaddress()
        userCard = UserCard.objects.get(user=user)
        
        if userCard.status == 0:
            PopUp(f"User {user.username} has been blocked")
        else:
            if userCard.credit_card_number == credit_card and times > 0:
                transaction = TransactionHistory(
                    product=product,
                    cost=product.cost,
                    ip_address=ip_address,
                    user=user
                )
                try:
                    transaction.save()
                    print(f"{user} buy product with id {product} using credit card {credit_card}")
                    PopUp("Transaction completed correctly.")
                except Exception:
                    PopUp("Transaction failed. Verify your data and try again.")
            else:
                if times == 0:
                    PopUp(f"User {user.username} has been blocked")
                    userCard.status = 0
                    userCard.save()
                    times = 3
                else:
                    times -= 1
                    PopUp(f"Credit card number wrong, you have {times} intents")

        self.credit_card_entry.delete(0, END)
        
# User views
class UserLogin(Login):

    def __init__(self, parent, controller):

        super().__init__(parent, controller, "User", UserModel, UserRegister, UserHome)

class EntryWithPlaceholder(Entry):
    def __init__(self, master=None, placeholder="PLACEHOLDER", color='grey'):
        super().__init__(master)

        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['fg']

        self.bind("<FocusIn>", self.foc_in)
        self.bind("<FocusOut>", self.foc_out)

        self.put_placeholder()

    def put_placeholder(self):
        self.insert(0, self.placeholder)
        self['fg'] = self.placeholder_color

    def foc_in(self, *args):
        if self['fg'] == self.placeholder_color:
            self.delete('0', 'end')
            self['fg'] = self.default_fg_color

    def foc_out(self, *args):
        if not self.get():
            self.put_placeholder()


class UserRegister(Frame):

    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        label = Label(self, text="Register user", font=LARGE_FONT)
        label.grid(row=0, column=1, pady=15, padx=20)
        
        username = StringVar()
        password = StringVar()
        phone = StringVar()
        email = StringVar()
        amount_limit = StringVar()
        ip_address = StringVar()

        # Username
        username_label = Label(self, text="Username: ", width="10")
        username_label.grid(row=1, column=0, pady=10, padx=0)

        self.username_entry = Entry(self, textvariable=username)
        self.username_entry.grid(row=1, column=1, pady=10, sticky=W)

        # Password
        password_label = Label(self, text="Password: ", width="10")
        password_label.grid(row=2, column=0, pady=10, padx=0)

        self.password_entry = Entry(self, textvariable=password, show="*")
        self.password_entry.grid(row=2, column=1, pady=10)

        # Phone number
        phone_label = Label(self, text="Phone: ", width="30")
        phone_label.grid(row=3, column=0, pady=10)

        self.phone_entry = Entry(self, textvariable=phone)
        self.phone_entry.grid(row=3, column=1, pady=10)

        # Email
        email_label = Label(self, text="Email: ", width="30")
        email_label.grid(row=4, column=0, pady=10)

        self.email_entry = Entry(self, textvariable=email)
        self.email_entry.grid(row=4, column=1, pady=10)

        # Amount limit
        amount_limit_label = Label(self, text="Amount limit: ", width="30")
        amount_limit_label.grid(row=5, column=0, pady=10)

        self.amount_limit_entry = Entry(self, textvariable=amount_limit)
        self.amount_limit_entry.grid(row=5, column=1, pady=10)
        
        Label(self, text="").grid(row=6, column=2, pady=10)

        # Card number

        self.card_entry = EntryWithPlaceholder(self, placeholder="CARD NUMBER")
        self.card_entry.grid(row=1, column=2, pady=10, padx=15)

        # Exp month
        self.month_entry = EntryWithPlaceholder(self, placeholder="EXP MONTH")
        self.month_entry.grid(row=2, column=2, pady=10, padx=15)

        # EXP YEAR
        self.year_entry = EntryWithPlaceholder(self, placeholder="EXP YEAR")
        self.year_entry.grid(row=3, column=2, pady=10, padx=15)

        # CVV
        self.cvv_entry = EntryWithPlaceholder(self, placeholder="CVV")
        self.cvv_entry.grid(row=4, column=2, pady=10, padx=15)


        login_btn = Button(self, text="Sign in", height="1", 
            command=self.register)
        login_btn.grid(row=7, column=0, pady=10)

        register_btn = Button(self, text="Back to Login",
            command=lambda: controller.show_frame(UserLogin))
        register_btn.grid(row=7, column=2, padx=0, pady=10)
    
    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        phone = self.phone_entry.get()
        email = self.email_entry.get()
        amount_limit = self.amount_limit_entry.get()
        ip_address = getipaddress()

        # Credit card number
        card_number = self.card_entry.get()
        month = self.month_entry.get()
        year = self.year_entry.get()
        cvv = self.cvv_entry.get()

        if username and password and phone and email and amount_limit and ip_address:
            if len(card_number) == 16 and month and year and cvv:
                try:
                    user = UserModel(
                        username=username,
                        password=password,
                        phone_number=phone,
                        email_id=email,
                        amount_limit=amount_limit,
                        ip_address=ip_address)
                    user.save()
                    ucard = UserCard(
                        user=user,
                        credit_card_number=card_number,
                        exp_month=int(month),
                        exp_year=int(year),
                        cvv=cvv
                    )
                    ucard.save()

                    self.username_entry.delete(0, END)
                    self.password_entry.delete(0, END)
                    self.phone_entry.delete(0, END)
                    self.email_entry.delete(0, END)
                    self.amount_limit_entry.delete(0, END)
                    self.card_entry.delete(0, END)
                    self.year_entry.delete(0, END)
                    self.month_entry.delete(0, END)
                    self.cvv_entry.delete(0, END)

                except Exception as e:
                    print("Some fields could't be totally validated or...")
                    print(f"{username} already exist: {e}")
            else:
                print("Empty card fields")
        else:
            print("Empty fields*")

        print(f"{username} - {password}")


class UserHome(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        label = Label(self, text="Welcome User!", font=LARGE_FONT)
        label.pack(pady=10, padx=10)

        self.menu_bar = MenuBar(parent, controller)


# Application Name

This webapp contains the menu database of <a class="index" href="http://www.pinocchiospizza.net/menu.html"> Pinocchio’s Pizza & Subs </a>. Here you can place an order.


## Getting Started

`pip install -r requirements.txt` to install requirements (I think), next set up the `FLASK_APP`, `DATABASE_URL` and `SECRET_KEY` envoirment variables


app:
  * adminviews.py:
      AdminUserIndexView    - defines the index page of the admin part of the website
      AdminView             - defines the ModelView used for the User class
      MenuView              - defines the ModelView used for the menu items (Pizza, NonPizza, Toppings)
      ProductView           - defines the ModelView used for the Product class
      OrderView             - defines the ModelView used for the Order items and Order classes
  * models.py:
      User          - defines the users table
      AnonymousUser - defines an user who is not logged on
      toppings      - is the association table for toppings and products
      Pizza         - defines the pizzas table
      Topping       - defines the toppings table
      NonPizza      - defines the non-pizzas table
      Product       - defines the products table
      OrderItem     - defines the order-items table
      Order         - defines the orders table
  * security.py:
      defines 2 functions, a function to hash a password (salt embedded) and a function to compare a hashed password (from the hash function in the same file) and a password

migrations:
    here are all the files neccesary for the migration located

static:
  * css:
      all the style related files are located here
  * img:
      contains the site icon, source: https://www.google.com/url?sa=i&url=https%3A%2F%2Fminecraftfanon.fandom.com%2Fwiki%2FPizza&psig=AOvVaw3W-R-wzBS8rlsjOo74RYIz&ust=1584285460050000&source=images&cd=vfe&ved=0CAIQjRxqFwoTCNiZmbWhmugCFQAAAAAdAAAAABAD
  * js:
      in the javascript file the form validation listeners and the toggle listeners are defined

templates:
  * admin:
      index.html:
        this is the home page for the admin part of the application
    cart.html:
      this is the cart page where all the items in the cart are shown, extends from layout.html
    error.html:
      this is the error page where the error message will be shown, extends from layout.html
    history.html:
      this is the history page where all recent orders are shown (new to old), extends from layout.html
    index.html:
      this is the home page of the application, extends from layout.html
    layout.html:
      this is the framework/layout of the application
    menu.html:
      this is the menu page where all the menu items will be shown and you can choose the item you want to buy, extends from layout.html
    register.html:
      this is the register page where you can register, extends from layout.html

application.py:
  * load_user()
      loads the user, returns none if not in database
  * setup_urls()
      setups all the url enpoints and titles for the navbar. It gets all "GET" registered routes from the app and filters the log/static/register/api/book endpoints out and defines the search for login only. Finally it adds the url_list to the session

      ***REMARK:** I used the nav items this way because here I only need to add/remove stuff in the forbidden and login_req lists to get the correct items in the navbar. The TA told me it was maybe easier if I did it different but since there was not much time left I could leave it like this*
  * index()
      renders the homepage (depending on login status)
  * register()
      renders the register form. If posted, it adds the user to the database
  * login()
      only if posted, it checks with database if user login details are correct. If so logs user in
  * logout()
      logout if logged in, log user out ***LOGIN REQUIRED***
  * menu()
      shows menu ***LOGIN REQUIRED***
  * add_pizza()
      returns the pizza product (Product class) for given item_id and request, if not in database it creates a new product
  * add_nonpizza()
      returns the pizza product (Product class) for given item_id and request, if not in database it creates a new product
  * shoppingcart()
      shows cart if request is a "GET" request, adds products to cart if request is "POST" request ***LOGIN REQUIRED***
  * pay_now()
      checks out all items in cart ***LOGIN REQUIRED***
  * recent()
      show the recent order history ***LOGIN REQUIRED***
  * errorhandler()
      renders error page when HTTPException is catched

requirements.txt:
  contains all modules required for app

Personal Touch:
  * My personal touch in this project is probably the way I've made sure some of the admin functions work correctly.
    Such as:
    * Only admins can reach the admin part of the website
    * If a password is changed it automatically gets hashed
    * In the products table extra cheese can only go with a non-pizza and toppings can only go with a pizza. Also a product can't have a pizza and a non-pizza at the same time.

  * I've also carefully thought through the models for this.
  An order is structured like this:

  ExampleOrder1<br>
  | OrderItem1<br>
  |...| Product1<br>
  |...|...| Pizza1<br>
  |...|...| Topping (1,2)<br>
  | OrderItem2<br>
  |...| Product2<br>
  |...|...| Non-Pizza1<br>
  |...|...| Extra cheese<br>
  | OrderItem3<br>
  |...| Product3<br>
  |...|...| Pizza1<br>
  |...|...| Topping (5,4)<br>
# Keep all 15 products in one list so they are easy to display.
# Each dictionary stores a product's ID, name and price.
# IDs let customers choose products without typing long names.
products = [
    {"id": 1, "name": "Playstation 4", "price": 499},
    {"id": 2, "name": "Xbox One", "price": 399},
    {"id": 3, "name": "Nintendo Switch", "price": 499},
    {"id": 4, "name": "Dualshock 4 Wireless Controller", "price": 89},
    {"id": 5, "name": "Xbox One Wireless Controller", "price": 89},
    {"id": 6, "name": "Joycon Controller ", "price": 69},
    {"id": 7, "name": " FIFA 19", "price": 99},
    {"id": 8, "name": "Madden 19", "price": 99},
    {"id": 9, "name": "NBA 2K19", "price": 99},
    {"id": 10, "name": "Horizon Zero Dawn", "price": 49},
    {"id": 11, "name": "Sea of Thieves", "price": 99},
    {"id": 12, "name": "No Man's Sky ", "price": 49},
    {"id": 13, "name": "Breath of the Wild", "price": 89},
    {"id": 14, "name": "Super Mario Odyssey", "price": 79},
    {"id": 15, "name": "Mario Tennis Aces", "price": 79},
]

# Start with an empty cart and no reward points for this visit.
# These values will be used when the shopping features are added.
cart = []
rewards_points = 0

# Store the rates and item limit here so they are easy to find and change.
# Decimal values allow the rates to be used in later calculations.
discount_rate = 0.40
gst_rate = 0.11
max_item = 3

# Repeat the menu so customers can make more than one choice.
# The loop will stop when the customer selects option 6.
while True:
    # Show all six options to match the plan in Part 1.
    print("Welcome to the Game Store!")
    print("1. View Products")
    print("2. Add Product to Cart")
    print("3. View / Edit Cart")
    print("4. Checkout")
    print("5. View Reward Points")
    print("6. Exit")

    # input() returns text, so compare the choice with text such as "1".
    # There is no need to turn it into a number for these menu checks.
    choice = input("Please select an option (1-6): ")

    if choice == "1":
        print("\nAvailable Products:")
        # Read each product from the list and show its details on one line.
        # This avoids writing a separate print statement for every product.
        for product in products:
            print(f"{product['id']}. {product['name']} - ${product['price']}")
        # Add a blank line to separate the product list from the next menu.
        print()

    elif choice == "2":
        try:
            if len(cart) >= max_item:
                print(f"You can only add up to {max_item} items to your cart.")
                continue
            product_id = int(input("Enter the product ID to add to cart: "))
            # Use a list comprehension to find the product with the matching ID.
            selected_product = next((product for product in products if product["id"] == product_id), None)
            if selected_product:
                cart.append(selected_product)
                print(f"{selected_product['name']} has been added to your cart.")
            else:
                print("Invalid product ID. Please try again.")
        except ValueError:
            print("Invalid input. Please enter a valid product ID.")

    elif choice == "3":
        if not cart:
            print("Your cart is empty.")
        else:
            print("\nYour Cart:")
            for i, item in enumerate(cart, start=1):
                print(f"{i}. {item['name']} - ${item['price']}")
            print(f"Total price: ${sum(item['price'] for item in cart)}")
            # Allow the customer to remove items from the cart.
            remove_id = input("Enter the cart item ID to remove from cart (or press Enter to skip): ").strip()  
            if remove_id:
                try:
                    remove_id = int(remove_id)
                    if 1 <= remove_id <= len(cart):
                        removed_item = cart.pop(remove_id - 1)
                        print(f"{removed_item['name']} has been removed from your cart.")
                    else:
                        print("This item ID is not in your cart. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a whole number.")




    # These two features are not ready at this stage.
    # Show a message so customers know why the selected feature does not open.
    elif choice == "4" or choice == "5":
        print("This feature is not implemented yet.")

    elif choice == "6":
        print("Thank you for shopping!")
        # Leave the loop to end the program after the goodbye message.
        break

    else:
        print("Invalid option. Please select a number between 1 and 6.")
    
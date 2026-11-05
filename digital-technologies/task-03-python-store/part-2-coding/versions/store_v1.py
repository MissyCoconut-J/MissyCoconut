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

    # These four features are not ready at this stage.
    # Show a message so customers know why the selected feature does not open.
    if choice == "2" or choice == "3" or choice == "4" or choice == "5":
        print("This feature is not implemented yet.")

    if choice == "6":
        print("Thank you for shopping!")
        # Leave the loop to end the program after the goodbye message.
        break

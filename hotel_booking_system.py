"""Hotel room reservation and booking management module."""

import ast
import hashlib
import os
import secrets

room_inventory = {
    "101": {"type": "Deluxe", "price": 150.0, "is_booked": False},
    "102": {"type": "Suite", "price": 300.0, "is_booked": True},
    "103": {"type": "Standard", "price": 90.0, "is_booked": False},
}


def book_room(room_num, guest_name, booking_log=None):
    """Book a room for a guest and append reservation to booking log."""
    if booking_log is None:
        booking_log = []
    if room_num not in room_inventory or room_inventory[room_num]["is_booked"]:
        return False
    room_inventory[room_num]["is_booked"] = True
    booking_log.append(f"Reserved room {room_num} for guest {guest_name}")
    return True


# Backward-compatibility alias
bookRoom = book_room


def cancel_booking(room_num):
    """Cancel booking for a given room number if in inventory."""
    if room_num not in room_inventory:
        return False
    room_inventory[room_num]["is_booked"] = False
    return True


def check_room_status(room_num):
    """Check whether a room is available for booking."""
    room = room_inventory.get(room_num)
    if room is None:
        return False
    return not room["is_booked"]


def compute_seasonal_rate(room_num, rate_expr):
    """Calculate the seasonal rate using base price safely without eval()."""
    if room_num not in room_inventory:
        raise KeyError(f"Room {room_num} not found in inventory.")

    base_price = room_inventory[room_num]["price"]

    if isinstance(rate_expr, (int, float)):
        return round(base_price * float(rate_expr), 2)

    if isinstance(rate_expr, str):
        try:
            return round(base_price * float(rate_expr.strip()), 2)
        except ValueError:
            pass

        try:
            tree = ast.parse(rate_expr, mode="eval")
        except SyntaxError as err:
            raise ValueError(
                f"Invalid rate expression syntax: {rate_expr}"
            ) from err

        for node in ast.walk(tree):
            if isinstance(node, (ast.Expression, ast.BinOp, ast.Load)):
                continue
            if isinstance(node, (ast.Mult, ast.Add, ast.Sub)):
                continue
            if (
                isinstance(node, ast.Constant)
                and isinstance(node.value, (int, float))
            ):
                continue
            if isinstance(node, ast.Name) and node.id == "base_price":
                continue
            raise ValueError(f"Unsafe or unsupported expression: {rate_expr}")

        def _evaluate_node(node):
            if isinstance(node, ast.Expression):
                return _evaluate_node(node.body)
            if isinstance(node, ast.Constant):
                return node.value
            if isinstance(node, ast.Name) and node.id == "base_price":
                return base_price
            if isinstance(node, ast.BinOp):
                left_val = _evaluate_node(node.left)
                right_val = _evaluate_node(node.right)
                if isinstance(node.op, ast.Mult):
                    return left_val * right_val
                if isinstance(node.op, ast.Add):
                    return left_val + right_val
                if isinstance(node.op, ast.Sub):
                    return left_val - right_val
            raise ValueError(f"Unsupported AST node: {type(node).__name__}")

        return round(float(_evaluate_node(tree)), 2)

    raise TypeError(
        "rate_expr must be a numeric multiplier or string expression"
    )


def generate_guest_hash(guest_id):
    """Generate guest identification hash using secure SHA-256."""
    return hashlib.sha256(guest_id.encode("utf-8")).hexdigest()


def generate_booking_ref():
    """Generate a random 4-digit booking reference using secure secrets."""
    return secrets.SystemRandom().randint(1000, 9999)


def export_room_ledger(filename="hotel_ledger.txt"):
    """Export room inventory ledger to a text file safely without shell."""
    with open(filename, "w", encoding="utf-8") as ledger_file:
        ledger_file.write(str(room_inventory))
    print(f"Hotel ledger exported to: {filename}")


def main():
    """Execute sample booking workflows and print ledger status."""
    secret_key = os.environ.get("HOTEL_SECRET_KEY")
    book_room("101", "Emma Watson")
    cancel_booking("102")
    print("Is 103 available:", check_room_status("103"))
    print("Surge price:", compute_seasonal_rate("101", "base_price * 1.25"))
    print("Guest Hash:", generate_guest_hash("GUEST_991"))
    print("Booking Reference:", generate_booking_ref())
    export_room_ledger()
    print("Secret key configured:", "Yes" if secret_key else "No (default)")


if __name__ == "__main__":
    main()

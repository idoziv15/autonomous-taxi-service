def calculate_movement(current, destination, speed, interval_time):
    """
    Calculate the new position along a single axis.
    """
    direction = 1 if destination > current else -1
    new_position = current + direction * speed * interval_time
    
    if direction == 1 and new_position > destination or direction == -1 and new_position < destination:
        new_position = destination
    return new_position

def update_taxi_state(taxi, speed, interval_time):
    """
    Updates the taxi's location and availability based on its current state.
    """
    current_x = float(taxi[b'location_x'])
    current_y = float(taxi[b'location_y'])
    dest_x = float(taxi[b'destination_x'])
    dest_y = float(taxi[b'destination_y'])

    # Move taxi on X axis
    if current_x != dest_x:
        new_x = calculate_movement(current_x, dest_x, speed, interval_time)
        return {"location_x": new_x, "location_y": current_y, "available": "False"}

    # Move taxi on Y axis
    elif current_y != dest_y:
        new_y = calculate_movement(current_y, dest_y, speed, interval_time)
        return {"location_x": current_x, "location_y": new_y, "available": "False"}

    # Taxi has reached its destination
    return {"location_x": current_x, "location_y": current_y, "available": "True"}

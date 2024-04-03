import requests

def get_distance_matrix(api_key, origins, destinations, travel_mode, start_time, time_unit):
    url = f"https://dev.virtualearth.net/REST/v1/Routes/DistanceMatrix?key={api_key}"
    headers = {"Content-Type": "application/json"}

    data = {
        "origins": origins,
        "destinations": destinations,
        "travelMode": travel_mode,
        "startTime": start_time,
        "timeUnit": time_unit
    }

    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    
    return response_data

# Example usage
api_key = "Arqv7qEYQddR1P_UsOxb9JD80QfZdRQSWmIyYZuBETFsZWmS2tjHVSxhl9cnRhqi"
origins = [{"latitude":  13.0011956, "longitude": 77.5963159}]
destinations = [{"latitude": 12.9712, "longitude": 77.6041}]
travel_mode = "driving"
start_time = "2022-04-01T08:00:00-08:00"
time_unit = "minute"

response_data = get_distance_matrix(api_key, origins, destinations, travel_mode, start_time, time_unit)
print(response_data)

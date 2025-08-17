import pandas as pd

def get_matching_cars(user_input, predicted_price_range, dataset, predicted_price):
    fuel_type = user_input['Fuel Type']
    transmission = user_input['Transmission']
    owner = user_input['Owner']
    location = user_input['Location']
    seating = int(user_input['Seating Capacity'])
    car_age = int(user_input['Car Age'])

    buffer = 0.15
    predicted_center = predicted_price
    min_price = predicted_center * (1 - buffer)
    max_price = predicted_center * (1 + buffer)

    fuel_col = f'Fuel_{fuel_type}'
    if fuel_col in dataset.columns:
        fuel_match = dataset[fuel_col] == 1
    else:
        fuel_match = pd.Series([True] * len(dataset))

    def filter_dataset(df, seating_tolerance, age_tolerance, allow_owner=False, allow_transmission=False, allow_location=False):
        condition = (
            fuel_match &
            (abs(df['Seating Capacity'] - seating) <= seating_tolerance) &
            (abs(df['Car Age'] - car_age) <= age_tolerance) &
            (df['Price'].between(min_price, max_price))
        )
        if not allow_owner:
            condition &= (df['Owner'] == owner)
        if not allow_transmission:
            condition &= (df['Transmission'] == transmission)
        if not allow_location:
            condition &= (df['Location'] == location)

        results = df[condition].copy()
        if not results.empty:
            results['Price Diff'] = abs(results['Price'] - predicted_center)
            results = results.sort_values(by='Price Diff')
        return results

    strict_matches = filter_dataset(dataset, seating_tolerance=0, age_tolerance=1)
    if not strict_matches.empty:
        return strict_matches.head(10), "Exact matches found"

    relaxed_seating_age = filter_dataset(dataset, seating_tolerance=2, age_tolerance=5)
    if not relaxed_seating_age.empty:
        return relaxed_seating_age.head(10), "Relaxed match (Seating & Age)"

    owner_relaxed = filter_dataset(dataset, seating_tolerance=2, age_tolerance=5, allow_owner=True)
    if not owner_relaxed.empty:
        return owner_relaxed.head(10), "Relaxed match (Owner mismatch allowed)"

    transmission_relaxed = filter_dataset(dataset, seating_tolerance=2, age_tolerance=5, allow_owner=True, allow_transmission=True)
    if not transmission_relaxed.empty:
        return transmission_relaxed.head(10), "Relaxed match (Transmission & Owner mismatch allowed)"

    location_relaxed = filter_dataset(dataset, seating_tolerance=2, age_tolerance=5, allow_owner=True, allow_transmission=True, allow_location=True)
    if not location_relaxed.empty:
        return location_relaxed.head(10), "Relaxed match (Location mismatch allowed)"

    return pd.DataFrame(), "No close matches found within your price range"

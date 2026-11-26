
from data.load_vendors_data import load_vendors_data


def filter_eligible_vendors(category, city, guest_count, wedding_days):
    vendors = load_vendors_data()
    eligible_vendors = []

    for vendor in vendors:
        if (
            vendor["category"].lower() == category.lower()
            and vendor["city"].lower() == city.lower()
        ):
            capacity = vendor.get("max_guest_capacity")
            max_days = vendor.get("max_service_days")

            capacity_valid = (
                capacity is None or capacity >= guest_count
            )

            days_valid = (
                max_days is None or max_days >= wedding_days
            )

            if capacity_valid and days_valid:
                eligible_vendors.append(vendor)

    return eligible_vendors


def calculate_vendor_cost(vendor, wedding_request):
    category = vendor["category"]

    if category == "catering":
        return (
            wedding_request.guest_count
            * wedding_request.wedding_days
            * vendor["price_per_plate"]
        )

    elif category == "venue":
        return (
            wedding_request.wedding_days
            * vendor["price_per_day"]
        )

    elif category == "photography":
        return vendor["package_price"]

    elif category == "decoration":
        return (
            wedding_request.wedding_days
            * vendor["price_per_event"]
        )

    elif category == "entertainment":
        return (
            wedding_request.wedding_days
            * vendor["price_per_performance"]
        )

    else:
        raise ValueError(
            f"Unsupported vendor category: {category}"
        )


def calculate_baseline_costs(wedding_request):

    categories = [
        "venue",
        "catering",
        "decoration",
        "photography",
        "entertainment"
    ]

    baseline_data = {}

    for category in categories:

        eligible_vendors = filter_eligible_vendors(
            category=category,
            city=wedding_request.city,
            guest_count=wedding_request.guest_count,
            wedding_days=wedding_request.wedding_days
        )

        vendors_with_cost = []

        for vendor in eligible_vendors:

            estimated_cost = calculate_vendor_cost(
                vendor,
                wedding_request
            )

            vendors_with_cost.append({
                **vendor,
                "estimated_cost": estimated_cost
            })

        vendors_with_cost.sort(
            key=lambda vendor: vendor["estimated_cost"]
        )

        if not vendors_with_cost:
            raise ValueError(
                f"No eligible vendors found for category: {category}"
            )

        baseline_vendor = vendors_with_cost[0]

        baseline_data[category] = {
            "eligible_vendors": vendors_with_cost,
            "baseline_vendor": baseline_vendor,
            "baseline_cost": baseline_vendor["estimated_cost"]
        }

    return baseline_data

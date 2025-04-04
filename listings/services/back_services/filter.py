def format_filter_values(request):
    listing_type = request.GET.get('listing_type', '')
    fields = (
        "listing_type",
        "apartment_series",
        "rooms",
        "heating",
        "condition",
        "furniture",
        "region",
        "city",
        "developer",
        "wall_material",
        "price_min",
        "price_max",
        "area_min",
        "area_max",
        "floor_min",
        "floor_max",
        "has_photo",
        "urgent",
    )

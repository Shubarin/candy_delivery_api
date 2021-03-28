from api.models import Assign, Courier, Order


def get_rating(courier: Courier) -> float:
    regions_times = {int(region): [] for region in courier.regions}
    orders = Order.objects.filter(
        assign_courier=courier,
        is_complete=True).order_by('complete_time')
    prev_complete = None
    for order in orders:
        if prev_complete is None:
            time_delivery = order.complete_time - order.assign_time
        else:
            time_delivery = order.complete_time - prev_complete
        prev_complete = order.complete_time
        regions_times[order.region].append(time_delivery.seconds)
    average_times = []
    for region, values in regions_times.items():
        if values:
            average_difference = sum(values) / len(values)
            average_times.append(average_difference)
    t = min(average_times) if average_times else 60 * 60
    return round((60 * 60 - min(t, 60 * 60)) / (60 * 60) * 5, 2)


def get_earning(courier: Courier) -> int:
    coefficient = {'foot': 2, 'bike': 5, 'car': 9}
    assigns = Assign.objects.filter(is_complete=True,
                                    courier_id=courier.courier_id)
    total = sum(
        map(lambda assign: 500 * coefficient[assign.courier_type], assigns))
    return int(total)

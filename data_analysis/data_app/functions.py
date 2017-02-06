from django.db.models import Sum

def calc_net_input(object_set):
    if object_set.exists():
        net_input = object_set.aggregate(sum=Sum('net_input'))
        net_input_sum = net_input['sum']
    else:
        net_input_sum = 0
    return net_input_sum


def get_net_inputs(object_set):
    if object_set.exists():
        net_input_cache = object_set.values_list('net_input', flat=True)
        net_inputs = []
        for item in net_input_cache:
            net_inputs.append(item)
    else:
        net_inputs = [0]
    return net_inputs


def get_month_name(integer):
    month_dict = {
        1 : 'January',
        2 : 'Febuary',
        3 : 'March',
        4 : 'April',
        5 : 'May',
        6 : 'June',
        7 : 'July',
        8 : 'August',
        9 : 'September',
        10 : 'October',
        11 : 'November',
        12 : 'December'
    }
    month_name = month_dict[integer]
    return month_name

from django.db.models import Sum

def calc_net_input(object_set):
    if object_set.exists():
        net_input = object_set.aggregate(sum=Sum('net_input'))
        net_input_sum = net_input['sum']
    else:
        net_input_sum = 0
    return net_input_sum
    # Note: calc_net_input could be combined with an if statement to save databse hits,
    # e.g., calc_net_input = month.calc_net_input(transaction_set)
    #       if month.net_input == calc_net_input:
    #           pass
    #       else:
    #           month.net_input = calc_net_input

def get_net_inputs(object_set):
    if object_set.exists():
        net_inputs = object_set.values_list('net_input', flat=True)
    else:
        net_inputs = []
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

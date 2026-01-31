from django import template

register = template.Library()

@register.filter
def machine_sort(machine_dict):
    """Sort machines by numerical order (M1, M2, M3, etc.)"""
    def get_machine_number(machine_name):
        try:
            # Extract number from machine name (e.g., "M1" -> 1, "M10" -> 10)
            return int(machine_name.replace('M', ''))
        except:
            return float('inf')  # Put non-standard names at the end
    
    # Convert dict items to list and sort by machine number
    sorted_items = sorted(machine_dict.items(), key=lambda x: get_machine_number(x[0]))
    return sorted_items
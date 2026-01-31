from django.shortcuts import render, redirect 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
import os, json
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponse
from analysis.scheduler import load_all_orders, analyze_orders, flatten_all_orders
from env_parser.machine_parser import parse_and_display_machine_env
from tabulate import tabulate



# Signup
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose another.")
            return redirect('front_page')

        user = User.objects.create_user(username=username, password=password, is_staff=False)
        login(request, user)
        return redirect('front_page')

    return redirect('front_page')

# Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return redirect('front_page')
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('front_page')
    return redirect('front_page')

# Logout
def logout_view(request):
    logout(request)
    return redirect('front_page')

# Front page view
def front_page(request):
    return render(request, 'accounts/front_page.html')

# Dashboard
@login_required
def dashboard_view(request):
    if request.user.is_staff:
        return render(request, 'accounts/admin_dashboard.html')
    return render(request, 'accounts/user_dashboard.html')

# Product Demand Submission
@csrf_exempt
@login_required
def save_product_demand(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = request.user.username

            # Ensure folder exists
            folder_path = os.path.join(settings.BASE_DIR, 'backend_data', 'user_orders')
            os.makedirs(folder_path, exist_ok=True)

            # Create timestamped filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(folder_path, f"{username}_{timestamp}.json")

            # Save to file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)

            return JsonResponse({'status': 'success', 'submitted_data': data})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# User History View
@login_required
def view_history(request):
    username = request.user.username
    folder_path = os.path.join(settings.BASE_DIR, 'backend_data', 'user_orders')
    history = []

    if os.path.exists(folder_path):
        for filename in sorted(os.listdir(folder_path)):
            if filename.startswith(username + "_") and filename.endswith(".json"):
                timestamp = filename.replace(username + "_", "").replace(".json", "")
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r') as f:
                    orders = json.load(f)
                    try:
                        readable_time = datetime.strptime(timestamp, "%Y%m%d_%H%M%S").strftime("%B %d, %Y at %I:%M %p")
                    except:
                        readable_time = timestamp
                    history.append({
                        "timestamp": readable_time,
                        "orders": orders
                    })

    return render(request, 'accounts/user_history.html', {'history': history})      


# Admin view for all orders
# import datetime

@staff_member_required
def admin_dashboard(request):
    folder_path = os.path.join(settings.BASE_DIR, 'backend_data', 'user_orders')
    user_orders = {}
    users = set()

    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                base = filename.replace(".json", "")
                parts = base.rsplit("_", 2)  # splits at last 2 underscores
                if len(parts) == 3:
                    username, date_part, time_part = parts
                    try:
                        timestamp = datetime.strptime(date_part + time_part, "%Y%m%d%H%M%S")
                        formatted_time = timestamp.strftime("%B %d, %Y at %I:%M %p")
                    except Exception as e:
                        formatted_time = "Unknown"
                else:
                    username = parts[0]
                    formatted_time = "Unknown"

                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r') as f:
                    orders = json.load(f)

                users.add(username)
                user_orders.setdefault(username, []).append({
                    'filename': filename,
                    'formatted_time': formatted_time,
                    'orders': orders
                })

    return render(request, 'accounts/admin_dashboard.html', {
        'users': sorted(users),
        'user_orders': user_orders
    })





@staff_member_required
def admin_all_orders_overview(request):
    folder_path = os.path.join(settings.BASE_DIR, 'backend_data', 'user_orders')
    all_orders = []

    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            if filename.endswith(".json"):
                username = filename.split("_")[0]
                file_path = os.path.join(folder_path, filename)
                with open(file_path, 'r') as f:
                    try:
                        orders = json.load(f)
                        for order in orders:
                            all_orders.append({
                                "username": username,
                                "product": order.get("product", "Unknown"),
                                "quantity": order.get("quantity", 0)
                            })
                    except Exception as e:
                        print(f"Error reading {filename}: {e}")

    return render(request, 'accounts/admin_all_orders_overview.html', {"all_orders": all_orders})

@staff_member_required
def admin_summary(request):
    folder_path = folder_path = os.path.join(settings.BASE_DIR, 'backend_data', 'user_orders')
    all_data = load_all_orders(folder_path)
    summary = analyze_orders(all_data)

    context = {
        'analysis': summary,
        'summary': summary,
    }

    return render(request, 'accounts/admin_summary.html', context)


@staff_member_required

def admin_machine_env(request):
    try:
        path = os.path.join(settings.BASE_DIR, 'backend_data/factory_env/machineENV01.txt')
        table_html = parse_and_display_machine_env(path)
        return render(request, 'accounts/admin_machineENV.html', {'table_html': table_html})
    except Exception as e:
        return render(request, 'accounts/admin_machineENV.html', {'error': f"Failed to load machine environment: {str(e)}"})



@staff_member_required
def admin_fjsp1_view(request):
    try:
        # Import the hybrid scheduler and utilities
        from flexible_scheduling.hybrid_ga_vns_scheduler import run_hybrid_ga_vns_scheduling
        from flexible_scheduling.utils import format_schedule_data_for_template, get_machine_utilization, get_job_statistics
        
        # Set up file paths
        machine_env_file = os.path.join(settings.BASE_DIR, 'backend_data', 'factory_env', 'machineENV01.txt')
        user_orders_folder = os.path.join(settings.BASE_DIR, 'backend_data', 'user_orders')
        
        # Get algorithm choice from request (default to hybrid)
        algorithm = request.GET.get('algorithm', 'hybrid')
        
        if algorithm == 'greedy':
            # Use original greedy scheduler for comparison
            from flexible_scheduling.fjsp_scheduler import run_fjsp_scheduling
            schedule_data = run_fjsp_scheduling(machine_env_file, user_orders_folder)
        else:
            # Use hybrid GA-VNS scheduler (default) with reduced parameters for web use
            from flexible_scheduling.hybrid_ga_vns_scheduler import HybridGAVNSScheduler
            scheduler = HybridGAVNSScheduler(machine_env_file, user_orders_folder)
            # Reduce parameters for faster web response
            scheduler.population_size = 20
            scheduler.generations = 20
            scheduler.vns_iterations = 5
            schedule_data = scheduler.run_scheduling()
        
        if 'error' in schedule_data:
            return render(request, 'accounts/admin_fjsp1.html', {
                'error': schedule_data['error'],
                'has_data': False,
                'algorithm_used': algorithm
            })
        
        # Format data for template
        formatted_schedule_data = format_schedule_data_for_template(schedule_data)
        machine_utilization = get_machine_utilization(schedule_data)
        
        # Sort machine utilization by machine number (M1, M2, M3, etc.)
        def get_machine_number(machine_name):
            try:
                return int(machine_name.replace('M', ''))
            except:
                return float('inf')
        
        sorted_machine_utilization = dict(sorted(
            machine_utilization.items(), 
            key=lambda x: get_machine_number(x[0])
        ))
        
        job_statistics = get_job_statistics(schedule_data)
        
        return render(request, 'accounts/admin_fjsp1.html', {
            'schedule_data': schedule_data,
            'schedule_data_json': formatted_schedule_data,
            'machine_utilization': sorted_machine_utilization,
            'job_statistics': job_statistics,
            'has_data': len(schedule_data.get('tasks', [])) > 0,
            'algorithm_used': algorithm
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return render(request, 'accounts/admin_fjsp1.html', {
            'error': f"Scheduling failed: {str(e)}",
            'has_data': False,
            'algorithm_used': 'unknown'
        })





def password_reset_placeholder(request):
    return HttpResponse("Password reset coming soon.")
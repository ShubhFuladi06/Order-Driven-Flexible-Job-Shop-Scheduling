"""
Flexible Job Shop Scheduling Problem (FJSP) Scheduler
This module handles the scheduling of multiple orders across flexible manufacturing resources.
"""

import os
import json
import heapq
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from collections import defaultdict
import random

@dataclass
class Job:
    """Represents a job type with its operations and processing times"""
    name: str
    operations: List[Dict]  # List of operations with machine groups and processing times
    
@dataclass
class Order:
    """Represents an order for a specific job with quantity"""
    job_name: str
    quantity: int
    user: str
    order_id: str
    
@dataclass
class Task:
    """Represents a single task (one unit of an order for one operation)"""
    order_id: str
    job_name: str
    operation_idx: int
    task_id: str
    quantity: int = 1
    
    def __lt__(self, other):
        """For heap comparison"""
        return self.task_id < other.task_id
    
@dataclass
class ScheduledTask:
    """Represents a scheduled task with timing information"""
    task: Task
    machine_id: str
    start_time: int
    end_time: int
    processing_time: int

class MachineState:
    """Tracks the state of a machine"""
    def __init__(self, machine_id: str):
        self.machine_id = machine_id
        self.available_time = 0
        self.scheduled_tasks = []
        
    def schedule_task(self, task: Task, processing_time: int, start_time: int = None) -> ScheduledTask:
        """Schedule a task on this machine"""
        if start_time is None:
            start_time = self.available_time
        else:
            start_time = max(start_time, self.available_time)
            
        end_time = start_time + processing_time
        self.available_time = end_time
        
        scheduled_task = ScheduledTask(
            task=task,
            machine_id=self.machine_id,
            start_time=start_time,
            end_time=end_time,
            processing_time=processing_time
        )
        
        self.scheduled_tasks.append(scheduled_task)
        return scheduled_task

class FJSPScheduler:
    """Main scheduler for Flexible Job Shop Scheduling Problem"""
    
    def __init__(self, machine_env_file: str, user_orders_folder: str):
        self.machine_env_file = machine_env_file
        self.user_orders_folder = user_orders_folder
        self.jobs = {}
        self.orders = []
        self.machines = {}
        self.job_operation_mapping = {
            'pants': 'Job1',
            'pant': 'Job1', 
            'shirt': 'Job2',
            'curtain': 'Job3',
            'towel': 'Job4',
            't-shirt': 'Job5',
            't-shirts': 'Job5'
        }
        self.scheduled_tasks = []
        
    def load_machine_environment(self):
        """Load machine environment from file"""
        print(f"Loading machine environment from {self.machine_env_file}")
        
        # Job definitions based on the factory environment image
        job_definitions = {
            'Job1': {  # Pants
                'name': 'Pants',
                'operations': [
                    {'operation': 'Fabric Inspection', 'machines': ['M1', 'M2', 'M3', 'M4']},
                    {'operation': 'Cutting', 'machines': ['M5', 'M6']},
                    {'operation': 'Sewing', 'machines': ['M7', 'M8']},
                    {'operation': 'Dyeing', 'machines': ['M9', 'M10', 'M11']},
                    {'operation': 'Printing', 'machines': ['M12', 'M13', 'M14', 'M15']},
                    {'operation': 'Quality Control', 'machines': ['M16', 'M17', 'M18']}
                ]
            },
            'Job2': {  # Shirt
                'name': 'Shirt',
                'operations': [
                    {'operation': 'Fabric Inspection', 'machines': ['M1', 'M2', 'M3', 'M4']},
                    {'operation': 'Cutting', 'machines': ['M5', 'M6']},
                    {'operation': 'Sewing', 'machines': ['M7', 'M8']},
                    {'operation': 'Dyeing', 'machines': ['M9', 'M10', 'M11']},
                    {'operation': 'Printing', 'machines': ['M12', 'M13', 'M14', 'M15']},
                    {'operation': 'Quality Control', 'machines': ['M16', 'M17', 'M18']}
                ]
            },
            'Job3': {  # Curtain
                'name': 'Curtain',
                'operations': [
                    {'operation': 'Fabric Inspection', 'machines': ['M1', 'M2', 'M3', 'M4']},
                    {'operation': 'Cutting', 'machines': ['M5', 'M6']},
                    {'operation': 'Sewing', 'machines': ['M7', 'M8']},
                    {'operation': 'Dyeing', 'machines': ['M9', 'M10', 'M11']},
                    {'operation': 'Printing', 'machines': ['M12', 'M13', 'M14', 'M15']},
                    {'operation': 'Quality Control', 'machines': ['M16', 'M17', 'M18']}
                ]
            },
            'Job4': {  # Towel
                'name': 'Towel',
                'operations': [
                    {'operation': 'Fabric Inspection', 'machines': ['M1', 'M2', 'M3', 'M4']},
                    {'operation': 'Cutting', 'machines': ['M5', 'M6']},
                    {'operation': 'Sewing', 'machines': ['M7', 'M8']},
                    {'operation': 'Dyeing', 'machines': ['M9', 'M10', 'M11']},
                    {'operation': 'Printing', 'machines': ['M12', 'M13', 'M14', 'M15']},
                    {'operation': 'Quality Control', 'machines': ['M16', 'M17', 'M18']}
                ]
            },
            'Job5': {  # T-shirt
                'name': 'T-shirt',
                'operations': [
                    {'operation': 'Fabric Inspection', 'machines': ['M1', 'M2', 'M3', 'M4']},
                    {'operation': 'Cutting', 'machines': ['M5', 'M6']},
                    {'operation': 'Sewing', 'machines': ['M7', 'M8']},
                    {'operation': 'Dyeing', 'machines': ['M9', 'M10', 'M11']},
                    {'operation': 'Printing', 'machines': ['M12', 'M13', 'M14', 'M15']},
                    {'operation': 'Quality Control', 'machines': ['M16', 'M17', 'M18']}
                ]
            }
        }
        
        # Load processing times from file
        processing_times = {}
        try:
            with open(self.machine_env_file, 'r') as f:
                lines = f.readlines()
                
            # Parse first line to get job count and total machines
            first_line = list(map(int, lines[0].strip().split()))
            num_jobs = first_line[0]
            total_machines = first_line[1]
            
            print(f"Found {num_jobs} jobs and {total_machines} machines")
                
            # Parse each job's data (starting from line 1)
            for i in range(num_jobs):
                if i + 1 < len(lines):
                    parts = list(map(int, lines[i + 1].strip().split()))
                    job_id = f'Job{i+1}'
                    
                    if job_id in job_definitions:
                        num_operations = parts[0]
                        processing_times[job_id] = {}
                        
                        idx = 1
                        for op in range(num_operations):
                            if idx >= len(parts):
                                break
                            num_machines = parts[idx]
                            idx += 1
                            operation_times = {}
                            
                            for m in range(num_machines):
                                if idx + 1 < len(parts):
                                    machine_id = f'M{parts[idx]}'
                                    processing_time = parts[idx + 1]
                                    operation_times[machine_id] = processing_time
                                    idx += 2
                                else:
                                    break
                                    
                            processing_times[job_id][op] = operation_times
                        
        except Exception as e:
            print(f"Error loading machine environment: {e}")
            # Create default processing times if file parsing fails
            for job_id in job_definitions:
                processing_times[job_id] = {}
                for op_idx in range(6):  # 6 operations
                    processing_times[job_id][op_idx] = {}
                    # Default processing times based on image data
                    if op_idx == 0:  # Fabric Inspection
                        processing_times[job_id][op_idx] = {'M1': 12, 'M2': 15, 'M3': 13, 'M4': 11}
                    elif op_idx == 1:  # Cutting  
                        processing_times[job_id][op_idx] = {'M5': 18, 'M6': 22}
                    elif op_idx == 2:  # Sewing
                        processing_times[job_id][op_idx] = {'M7': 20, 'M8': 25}
                    elif op_idx == 3:  # Dyeing
                        processing_times[job_id][op_idx] = {'M9': 35, 'M10': 30, 'M11': 40}
                    elif op_idx == 4:  # Printing
                        processing_times[job_id][op_idx] = {'M12': 20, 'M13': 18, 'M14': 15, 'M15': 22}
                    elif op_idx == 5:  # Quality Control
                        processing_times[job_id][op_idx] = {'M16': 15, 'M17': 12, 'M18': 10}
            
        # Create job objects with processing times
        for job_id, job_def in job_definitions.items():
            operations = []
            for i, op_def in enumerate(job_def['operations']):
                operation = {
                    'operation': op_def['operation'],
                    'machines': op_def['machines'],
                    'processing_times': processing_times.get(job_id, {}).get(i, {})
                }
                operations.append(operation)
                
            self.jobs[job_id] = Job(name=job_def['name'], operations=operations)
            
        # Initialize all machines
        all_machine_ids = set()
        for job in self.jobs.values():
            for op in job.operations:
                all_machine_ids.update(op['machines'])
                
        for machine_id in all_machine_ids:
            self.machines[machine_id] = MachineState(machine_id)
            
        print(f"Loaded {len(self.jobs)} jobs and {len(self.machines)} machines")
        
    def load_user_orders(self):
        """Load all user orders from the orders folder"""
        print(f"Loading user orders from {self.user_orders_folder}")
        
        self.orders = []
        for filename in os.listdir(self.user_orders_folder):
            if filename.endswith('.json'):
                username = filename.split('_')[0]
                timestamp = filename.replace('.json', '').replace(f'{username}_', '')
                
                filepath = os.path.join(self.user_orders_folder, filename)
                with open(filepath, 'r') as f:
                    orders_data = json.load(f)
                    
                for order_data in orders_data:
                    product = order_data.get('product', '').lower()
                    quantity = int(order_data.get('quantity', 0))
                    
                    if product in self.job_operation_mapping:
                        job_name = self.job_operation_mapping[product]
                        order_id = f"{username}_{timestamp}_{product}"
                        
                        order = Order(
                            job_name=job_name,
                            quantity=quantity,
                            user=username,
                            order_id=order_id
                        )
                        self.orders.append(order)
                        
        print(f"Loaded {len(self.orders)} orders")
        
    def get_best_machine_for_task(self, task: Task, operation: Dict) -> Tuple[str, int]:
        """Find the best machine for a task based on earliest completion time"""
        best_machine = None
        best_completion_time = float('inf')
        best_processing_time = 0
        
        available_machines = operation['machines']
        processing_times = operation['processing_times']
        
        for machine_id in available_machines:
            if machine_id in processing_times and machine_id in self.machines:
                processing_time = processing_times[machine_id]
                machine = self.machines[machine_id]
                completion_time = machine.available_time + processing_time
                
                if completion_time < best_completion_time:
                    best_completion_time = completion_time
                    best_machine = machine_id
                    best_processing_time = processing_time
                    
        return best_machine, best_processing_time
        
    def schedule_orders(self):
        """Main scheduling algorithm using priority-based approach"""
        print("Starting scheduling process...")
        
        # Create tasks for all orders
        all_tasks = []
        task_predecessors = {}  # Track task dependencies
        
        for order in self.orders:
            job = self.jobs[order.job_name]
            order_tasks = []
            
            # Create tasks for each unit of the order
            for unit in range(order.quantity):
                unit_tasks = []
                for op_idx in range(len(job.operations)):
                    task_id = f"{order.order_id}_unit{unit}_op{op_idx}"
                    task = Task(
                        order_id=order.order_id,
                        job_name=order.job_name,
                        operation_idx=op_idx,
                        task_id=task_id
                    )
                    unit_tasks.append(task)
                    all_tasks.append(task)
                    
                    # Set predecessor constraints (operations must be sequential)
                    if op_idx > 0:
                        predecessor_task_id = f"{order.order_id}_unit{unit}_op{op_idx-1}"
                        task_predecessors[task_id] = predecessor_task_id
                        
        # Priority queue for scheduling (earliest start time first)
        ready_tasks = []
        scheduled_task_ids = set()
        task_completion_times = {}
        task_counter = 0  # For tie-breaking in heap
        
        # Add initial tasks (first operation of each unit)
        for task in all_tasks:
            if task.operation_idx == 0:
                heapq.heappush(ready_tasks, (0, task_counter, task))  # (priority, counter, task)
                task_counter += 1
                
        # Schedule tasks
        while ready_tasks:
            _, _, current_task = heapq.heappop(ready_tasks)
            
            if current_task.task_id in scheduled_task_ids:
                continue
                
            # Get job and operation info
            job = self.jobs[current_task.job_name]
            operation = job.operations[current_task.operation_idx]
            
            # Find best machine
            best_machine_id, processing_time = self.get_best_machine_for_task(current_task, operation)
            
            if best_machine_id is None:
                print(f"Warning: No suitable machine found for task {current_task.task_id}")
                continue
                
            # Calculate start time (considering predecessor constraints)
            start_time = self.machines[best_machine_id].available_time
            if current_task.task_id in task_predecessors:
                predecessor_id = task_predecessors[current_task.task_id]
                if predecessor_id in task_completion_times:
                    start_time = max(start_time, task_completion_times[predecessor_id])
                    
            # Schedule the task
            scheduled_task = self.machines[best_machine_id].schedule_task(
                current_task, processing_time, start_time
            )
            self.scheduled_tasks.append(scheduled_task)
            scheduled_task_ids.add(current_task.task_id)
            task_completion_times[current_task.task_id] = scheduled_task.end_time
            
            # Add next operation to ready queue if available
            if current_task.operation_idx < len(job.operations) - 1:
                next_task_id = current_task.task_id.replace(
                    f"_op{current_task.operation_idx}", 
                    f"_op{current_task.operation_idx + 1}"
                )
                
                # Find the next task
                for task in all_tasks:
                    if task.task_id == next_task_id:
                        heapq.heappush(ready_tasks, (scheduled_task.end_time, task_counter, task))
                        task_counter += 1
                        break
                        
        print(f"Scheduling completed. {len(self.scheduled_tasks)} tasks scheduled.")
        
    def get_schedule_data(self) -> Dict:
        """Return schedule data in format suitable for Gantt chart"""
        schedule_data = {
            'tasks': [],
            'machines': list(self.machines.keys()),
            'makespan': 0,
            'summary': {},
            'order_completion_times': []
        }
        
        # Group tasks by machine
        machine_tasks = defaultdict(list)
        for scheduled_task in self.scheduled_tasks:
            machine_tasks[scheduled_task.machine_id].append(scheduled_task)
            
        # Calculate makespan
        if self.scheduled_tasks:
            schedule_data['makespan'] = int(max(task.end_time for task in self.scheduled_tasks))
            
        # Calculate order completion times
        order_completion_times = {}
        for scheduled_task in self.scheduled_tasks:
            order_id = scheduled_task.task.order_id
            if order_id not in order_completion_times:
                order_completion_times[order_id] = 0
            order_completion_times[order_id] = max(order_completion_times[order_id], scheduled_task.end_time)
        
        # Format order completion information
        order_completion_list = []
        for order in self.orders:
            completion_time = order_completion_times.get(order.order_id, 0)
            
            # Extract product name from order_id
            product_name = order.order_id.split('_')[-1].title()
            
            order_info = {
                'user': order.user.title(),
                'product': product_name,
                'quantity': order.quantity,
                'completion_time': completion_time,
                'order_id': order.order_id,
                'job_name': order.job_name
            }
            order_completion_list.append(order_info)
        
        # Sort by completion time
        order_completion_list.sort(key=lambda x: x['completion_time'])
        schedule_data['order_completion_times'] = order_completion_list
        
        # Calculate completion time statistics
        if order_completion_list:
            completion_times = [order['completion_time'] for order in order_completion_list]
            schedule_data['completion_stats'] = {
                'fastest': min(completion_times),
                'slowest': max(completion_times),
                'average': sum(completion_times) / len(completion_times),
                'median': sorted(completion_times)[len(completion_times) // 2],
                'total_orders': len(completion_times)
            }
        else:
            schedule_data['completion_stats'] = {
                'fastest': 0,
                'slowest': 0,
                'average': 0,
                'median': 0,
                'total_orders': 0
            }
            
        # Format tasks for Gantt chart
        for machine_id, tasks in machine_tasks.items():
            for task in sorted(tasks, key=lambda x: x.start_time):
                task_data = {
                    'machine': machine_id,
                    'job': task.task.job_name,
                    'order_id': task.task.order_id,
                    'operation': task.task.operation_idx + 1,
                    'start_time': task.start_time,
                    'end_time': task.end_time,
                    'duration': task.processing_time,
                    'task_id': task.task.task_id
                }
                schedule_data['tasks'].append(task_data)
                
        # Summary statistics
        job_counts = defaultdict(int)
        for order in self.orders:
            job_counts[order.job_name] += order.quantity
            
        schedule_data['summary'] = {
            'total_orders': len(self.orders),
            'total_tasks': len(self.scheduled_tasks),
            'total_machines': len(self.machines),
            'job_distribution': dict(job_counts)
        }
        
        return schedule_data
        
    def run_scheduling(self) -> Dict:
        """Run the complete scheduling process"""
        try:
            self.load_machine_environment()
            self.load_user_orders()
            self.schedule_orders()
            return self.get_schedule_data()
        except Exception as e:
            print(f"Error during scheduling: {e}")
            return {
                'error': str(e),
                'tasks': [],
                'machines': [],
                'makespan': 0,
                'summary': {}
            }

def run_fjsp_scheduling(machine_env_file: str, user_orders_folder: str) -> Dict:
    """Main function to run FJSP scheduling"""
    scheduler = FJSPScheduler(machine_env_file, user_orders_folder)
    return scheduler.run_scheduling()

if __name__ == "__main__":
    # Test the scheduler
    import os
    from django.conf import settings
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    machine_env_file = os.path.join(base_dir, 'backend_data', 'factory_env', 'machineENV01.txt')
    user_orders_folder = os.path.join(base_dir, 'backend_data', 'user_orders')
    
    result = run_fjsp_scheduling(machine_env_file, user_orders_folder)
    print("Scheduling Result:")
    print(f"Makespan: {result['makespan']} minutes")
    print(f"Total tasks: {len(result['tasks'])}")
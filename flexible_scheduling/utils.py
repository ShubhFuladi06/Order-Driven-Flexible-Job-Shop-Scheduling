"""
Utility functions for FJSP scheduling visualization
"""

import json
from django.utils.safestring import mark_safe

def format_schedule_data_for_template(schedule_data):
    """
    Format schedule data for safe JSON output in Django templates
    """
    # Ensure all data is JSON serializable
    formatted_data = {
        'tasks': [],
        'machines': schedule_data.get('machines', []),
        'makespan': schedule_data.get('makespan', 0),
        'summary': schedule_data.get('summary', {})
    }
    
    # Format tasks
    for task in schedule_data.get('tasks', []):
        formatted_task = {
            'machine': str(task.get('machine', '')),
            'job': str(task.get('job', '')),
            'order_id': str(task.get('order_id', '')),
            'operation': int(task.get('operation', 0)),
            'start_time': int(task.get('start_time', 0)),
            'end_time': int(task.get('end_time', 0)),
            'duration': int(task.get('duration', 0)),
            'task_id': str(task.get('task_id', ''))
        }
        formatted_data['tasks'].append(formatted_task)
    
    # Sort tasks by machine and start time for better visualization
    formatted_data['tasks'].sort(key=lambda x: (x['machine'], x['start_time']))
    
    return mark_safe(json.dumps(formatted_data))

def get_machine_utilization(schedule_data):
    """
    Calculate machine utilization statistics
    """
    utilization = {}
    makespan = schedule_data.get('makespan', 1)
    
    for machine in schedule_data.get('machines', []):
        utilization[machine] = {
            'total_time': 0,
            'idle_time': makespan,
            'utilization_percent': 0,
            'task_count': 0
        }
    
    # Calculate working time for each machine
    for task in schedule_data.get('tasks', []):
        machine = task.get('machine')
        if machine in utilization:
            utilization[machine]['total_time'] += task.get('duration', 0)
            utilization[machine]['task_count'] += 1
    
    # Calculate utilization percentages
    for machine, data in utilization.items():
        if makespan > 0:
            data['idle_time'] = makespan - data['total_time']
            data['utilization_percent'] = round((data['total_time'] / makespan) * 100, 2)
    
    return utilization

def get_job_statistics(schedule_data):
    """
    Get statistics about job completion times and counts
    """
    job_stats = {}
    
    for task in schedule_data.get('tasks', []):
        job = task.get('job')
        if job not in job_stats:
            job_stats[job] = {
                'task_count': 0,
                'total_duration': 0,
                'earliest_start': float('inf'),
                'latest_end': 0,
                'avg_processing_time': 0
            }
        
        stats = job_stats[job]
        stats['task_count'] += 1
        stats['total_duration'] += task.get('duration', 0)
        stats['earliest_start'] = min(stats['earliest_start'], task.get('start_time', 0))
        stats['latest_end'] = max(stats['latest_end'], task.get('end_time', 0))
    
    # Calculate averages
    for job, stats in job_stats.items():
        if stats['task_count'] > 0:
            stats['avg_processing_time'] = round(stats['total_duration'] / stats['task_count'], 2)
            stats['completion_time'] = stats['latest_end'] - stats['earliest_start']
        else:
            stats['avg_processing_time'] = 0
            stats['completion_time'] = 0
    
    return job_stats
# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from .models import Subject, Task, PlannerTask, UserStatistics
from datetime import date, timedelta
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import models

import whisper
from dateutil.parser import parse as parse_datetime
import re
from django.core.files.base import ContentFile
import os
from django.conf import settings

from django.db.models import Count, F, Q
from datetime import date, timedelta
import json
from collections import defaultdict

whisper_model = whisper.load_model("tiny.en")

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    
    return render(request, 'signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('login')
    return redirect('home')

@login_required
def home_view(request):
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Get active tasks due today
    today_tasks = Task.objects.filter(
        subject__user=request.user,
        due_date=date.today(),
        completed=False
    ).order_by('due_time')
    
    # Get completed tasks due today
    completed_tasks = Task.objects.filter(
        subject__user=request.user,
        due_date=date.today(),
        completed=True
    ).order_by('due_time')

    # Get tasks due tomorrow
    tomorrow_tasks = Task.objects.filter(
        subject__user=request.user,
        due_date=tomorrow,
        completed=False
    ).order_by('due_time')
    
    # Get total, pending and completed tasks counts
    total_tasks = Task.objects.filter(subject__user=request.user).count()
    completed_count = Task.objects.filter(subject__user=request.user, completed=True).count()
    pending_count = total_tasks - completed_count
    
    return render(request, 'home.html', {
        'today_tasks': today_tasks,
        'completed_tasks': completed_tasks,
        'tomorrow_tasks': tomorrow_tasks,
        'today': today,
        'total_tasks': total_tasks,
        'completed_count': completed_count,
        'pending_count': pending_count
    })

@login_required
def subjects_view(request):
    subjects = Subject.objects.filter(user=request.user).order_by('name')
    today = date.today()  # Import date from datetime at the top if not already done

     # Add pending tasks count to each subject
    for subject in subjects:
        subject.pending_count = subject.tasks.filter(completed=False).count()
         # Get all tasks (this will be used in the template)
        all_tasks = list(subject.tasks.all())
        # Sort tasks so completed ones are at the end
        all_tasks.sort(key=lambda x: x.completed)
        # Store the sorted tasks on the subject
        subject.sorted_tasks = all_tasks

    return render(request, 'subjects.html', {
        'subjects': subjects,
        'today': today
    })

@login_required
def add_subject(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        color = request.POST.get('color')
        
        Subject.objects.create(
            user=request.user,
            name=name,
            color=color
        )
        
        return redirect('subjects')
    return redirect('subjects')

@login_required
def add_task(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        title = request.POST.get('title')
        due_date = request.POST.get('due_date')
        due_time = request.POST.get('due_time')
        ideal_time = request.POST.get('ideal_time')
        notes = request.POST.get('notes')
        
        subject = get_object_or_404(Subject, id=subject_id, user=request.user)
        
        # Create the task
        Task.objects.create(
            subject=subject,
            title=title,
            due_date=due_date,
            due_time=due_time,
            ideal_time=ideal_time if ideal_time else None,
            notes=notes
        )
        
        return redirect('subjects')
    return redirect('subjects')

@login_required
def edit_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        title = request.POST.get('title')
        due_date = request.POST.get('due_date')
        due_time = request.POST.get('due_time')
        ideal_time = request.POST.get('ideal_time')
        notes = request.POST.get('notes')
        
        task = get_object_or_404(Task, id=task_id, subject__user=request.user)
        
        # Update the task
        task.title = title
        task.due_date = due_date
        task.due_time = due_time
        task.ideal_time = ideal_time if ideal_time else None
        task.notes = notes
        task.save()
        
        return redirect('subjects')
    return redirect('subjects')

@login_required
def delete_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task = get_object_or_404(Task, id=task_id, subject__user=request.user)
        task.delete()
        return redirect(request.META.get('HTTP_REFERER', 'subjects'))
    return redirect('subjects')

@login_required
def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id, user=request.user)
    tasks = Task.objects.filter(subject=subject).order_by('due_date', 'due_time')
    
    return render(request, 'subject_detail.html', {
        'subject': subject,
        'tasks': tasks
    })

@login_required
@require_POST
def toggle_task_completion(request, task_id):
    task = get_object_or_404(Task, id=task_id, subject__user=request.user)
    
    try:
        # For AJAX requests
        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body)
            task.completed = data.get('completed', not task.completed)
        else:
            # For traditional form submissions
            task.completed = not task.completed
        
        # Make sure to save the task
        task.save()
        
        # Return JSON response for AJAX requests
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': True, 
                'task_id': task_id, 
                'completed': task.completed
            })
        
        # Redirect to the referring page for traditional form submissions
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    except json.JSONDecodeError:
        # Handle JSON parsing errors
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        return redirect('home')
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        return redirect('home')

@login_required
def delete_subject(request):
    if request.method == 'POST':
        subject_id = request.POST.get('subject_id')
        subject = get_object_or_404(Subject, id=subject_id, user=request.user)
        subject.delete()
        return redirect('subjects')
    return redirect('subjects')

@login_required
def calendar_view(request):
    # Get the selected date from URL parameter, default to today
    selected_date_str = request.GET.get('date', date.today().strftime('%Y-%m-%d'))
    try:
        selected_date = date.fromisoformat(selected_date_str)
    except ValueError:
        selected_date = date.today()

    # Get all tasks for the calendar view
    planner_tasks = PlannerTask.objects.filter(user=request.user).order_by('due_date')
    
    # Convert tasks to JSON-serializable format
    task_list = []
    for task in planner_tasks:
        task_dict = {
            'id': task.id,
            'title': task.title,
            'due_date': task.due_date.strftime('%Y-%m-%d'),
            'duration_hours': float(task.duration_hours) if task.duration_hours else None,
            'notes': task.notes,
            'completed': task.completed,
            'repeat_enabled': task.repeat_enabled,
            'repeat_type': task.repeat_type,
            'repeat_until': task.repeat_until.strftime('%Y-%m-%d') if task.repeat_until else None,
        }
        task_list.append(task_dict)

    # Get tasks for the selected date
    selected_date_tasks = []
    
    # First, add directly scheduled tasks
    direct_tasks = PlannerTask.objects.filter(
        user=request.user, 
        due_date=selected_date
    ).order_by('id')
    
    selected_date_tasks.extend(direct_tasks)
    
    # Then, add repeating tasks
    today = date.today()
    repeating_tasks = PlannerTask.objects.filter(
        user=request.user,
        repeat_enabled=True,
        due_date__lte=selected_date  # Task starts on or before selected date
    ).filter(
        models.Q(repeat_until__gte=selected_date) | models.Q(repeat_until__isnull=True)  # Task ends on or after selected date or doesn't end
    )
    
    for task in repeating_tasks:
        # Check if this task repeats on the selected date
        if task.due_date == selected_date:  # Already captured in direct_tasks
            continue
            
        # Calculate if the task should appear on the selected date based on repeat pattern
        should_show = False
        
        if task.repeat_type == 'daily':
            should_show = True
        elif task.repeat_type == 'weekly':
            # Check if the day of week matches
            should_show = task.due_date.weekday() == selected_date.weekday()
        elif task.repeat_type == 'monthly':
            # Check if the day of month matches
            # Handle month length differences (e.g., 31st in a month with only 30 days)
            day_of_month = min(task.due_date.day, [31, 29 if selected_date.year % 4 == 0 and (selected_date.year % 100 != 0 or selected_date.year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][selected_date.month - 1])
            should_show = day_of_month == selected_date.day
        
        if should_show:
            # For repeating tasks, we'll create a display copy but won't add it to the database
            selected_date_tasks.append(task)

    return render(request, 'calendar.html', {
        'tasks_json': json.dumps(task_list),
        'selected_date': selected_date.strftime('%Y-%m-%d'),
        'selected_date_tasks': selected_date_tasks,
    })


@login_required
def add_planner_task(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        due_date = request.POST.get('due_date')
        due_time = request.POST.get('due_time') or None
        duration_hours = request.POST.get('duration_hours') or None
        notes = request.POST.get('notes')

        # Get repeat information
        repeat_enabled = 'repeat_enabled' in request.POST
        repeat_type = request.POST.get('repeat_type') if repeat_enabled else None
        repeat_until = request.POST.get('repeat_until') if repeat_enabled else None
        
        # Create the planner task
        PlannerTask.objects.create(
            user=request.user,
            title=title,
            due_date=due_date,
            due_time=due_time,
            duration_hours=duration_hours,
            notes=notes,
            repeat_enabled=repeat_enabled,
            repeat_type=repeat_type,
            repeat_until=repeat_until
        )
        
        # Redirect back to calendar with the same date
        return redirect(f'/calendar/?date={due_date}')
    
    return redirect('calendar')

@login_required
def edit_planner_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        title = request.POST.get('title')
        due_date = request.POST.get('due_date')
        due_time = request.POST.get('due_time') or None
        duration_hours = request.POST.get('duration_hours') or None
        notes = request.POST.get('notes')

        # Get repeat information
        repeat_enabled = 'repeat_enabled' in request.POST
        repeat_type = request.POST.get('repeat_type') if repeat_enabled else None
        repeat_until = request.POST.get('repeat_until') if repeat_enabled else None
        
        task = get_object_or_404(PlannerTask, id=task_id, user=request.user)
        
        # Update the task
        task.title = title
        task.due_date = due_date
        task.due_time = due_time
        task.duration_hours = duration_hours
        task.notes = notes
        task.repeat_enabled = repeat_enabled
        task.repeat_type = repeat_type
        task.repeat_until = repeat_until
        task.save()
        
        # Redirect back to calendar with the same date
        return redirect(f'/calendar/?date={due_date}')
    
    return redirect('calendar')

@login_required
def delete_planner_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id')
        task = get_object_or_404(PlannerTask, id=task_id, user=request.user)
        due_date = task.due_date
        task.delete()
        
        # Redirect back to calendar with the same date
        return redirect(f'/calendar/?date={due_date}')
    
    return redirect('calendar')

@login_required
@require_POST
def toggle_planner_task_completion(request, task_id):
    task = get_object_or_404(PlannerTask, id=task_id, user=request.user)
    
    try:
        # For AJAX requests
        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body)
            task.completed = data.get('completed', not task.completed)
        else:
            # For traditional form submissions
            task.completed = not task.completed
        
        task.save()
        
        # Return JSON response for AJAX requests
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({
                'success': True, 
                'task_id': task_id, 
                'completed': task.completed
            })
        
        # Redirect to the referring page for traditional form submissions
        return redirect(request.META.get('HTTP_REFERER', 'calendar'))
    
    except Exception as e:
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        return redirect('calendar')
    
@login_required
def statistics_view(request):
    """
    Calculates and displays user statistics including streaks,
    subject performance, and weekly productivity.
    """
    # Get or create user statistics object
    stats, created = UserStatistics.objects.get_or_create(user=request.user)
    today = date.today()

    # --- 1. Calculate Streaks ---
    # Get all unique dates when any task was completed
    task_completion_dates = set(Task.objects.filter(
        subject__user=request.user, completed=True
    ).values_list('due_date', flat=True))
    
    planner_completion_dates = set(PlannerTask.objects.filter(
        user=request.user, completed=True
    ).values_list('due_date', flat=True))
    
    all_completion_dates = sorted(list(task_completion_dates.union(planner_completion_dates)))

    # Calculate current streak
    current_streak = 0
    if all_completion_dates:
        # Check for activity today or yesterday to determine the start of the streak
        if today in all_completion_dates:
            current_streak = 1
            check_date = today - timedelta(days=1)
        elif (today - timedelta(days=1)) in all_completion_dates:
            current_streak = 0 # Streak is broken if nothing today, but we check from yesterday
            check_date = today - timedelta(days=1)
        else: # No activity today or yesterday, streak is 0
            check_date = None

        if check_date:
            # Count consecutive days backwards
            while check_date in all_completion_dates:
                current_streak += 1
                check_date -= timedelta(days=1)

    # Calculate longest streak
    longest_streak = 0
    if all_completion_dates:
        current_run = 0
        previous_date = None
        for completion_date in all_completion_dates:
            if previous_date is None or (completion_date - previous_date).days > 1:
                current_run = 1
            else: # Consecutive day
                current_run += 1
            longest_streak = max(longest_streak, current_run)
            previous_date = completion_date

    # Update longest streak in the database if the new calculation is greater
    if longest_streak > stats.longest_streak:
        stats.longest_streak = longest_streak
        stats.save()

    # --- 2. Subject Performance ---
    # Use annotation for a more efficient query
    subjects = Subject.objects.filter(user=request.user).annotate(
        total_tasks=Count('tasks'),
        completed_tasks=Count('tasks', filter=Q(tasks__completed=True))
    )
    
    subject_stats = []
    for subject in subjects:
        completion_rate = (subject.completed_tasks / subject.total_tasks) * 100 if subject.total_tasks > 0 else 0
        subject_stats.append({
            'name': subject.name,
            'color': subject.color,
            'total_tasks': subject.total_tasks,
            'completed_tasks': subject.completed_tasks,
            'completion_rate': round(completion_rate, 1)
        })

    # --- 3. Overdue Tasks (Corrected Logic) ---
    # An overdue task is one that is NOT completed and its due date is in the past.
    overdue_subject_tasks = Task.objects.filter(
        subject__user=request.user, completed=False, due_date__lt=today
    ).count()
    overdue_planner_tasks = PlannerTask.objects.filter(
        user=request.user, completed=False, due_date__lt=today
    ).count()
    overdue_tasks = overdue_subject_tasks + overdue_planner_tasks

    # --- 4. Calendar Utilization (Weekly Productivity) ---
    days_of_week = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    calendar_utilization = {day: 0 for day in days_of_week}

    # Get count of all tasks (Planner and Subject) grouped by weekday
    # Note: Django's week_day is 1=Sun, 7=Sat. We adjust to 0=Mon, 6=Sun.
    all_tasks_by_day = PlannerTask.objects.filter(user=request.user).annotate(
        weekday=F('due_date__week_day')
    ).values('weekday').annotate(count=Count('id')).union(
        Task.objects.filter(subject__user=request.user).annotate(
            weekday=F('due_date__week_day')
        ).values('weekday').annotate(count=Count('id'))
    )

    # Aggregate counts from both querysets
    aggregated_counts = defaultdict(int)
    for entry in all_tasks_by_day:
        day_index = (entry['weekday'] - 2 + 7) % 7  # Adjust index (Mon=0)
        aggregated_counts[day_index] += entry['count']

    for day_index, count in aggregated_counts.items():
        calendar_utilization[days_of_week[day_index]] = count

    # --- 5. Prepare Context and Render ---
    context = {
        'current_streak': current_streak,
        'longest_streak': stats.longest_streak,
        'subject_stats': subject_stats,
        'overdue_tasks': overdue_tasks,
        'calendar_utilization': calendar_utilization,
    }
    
    return render(request, 'statistics.html', context)

# Audio feature view (Subjects page)

@login_required
@require_POST
@csrf_exempt
def transcribe_and_parse_task(request):
    if 'audio_data' not in request.FILES:
        return JsonResponse({'error': 'No audio file provided.'}, status=400)

    audio_file = request.FILES['audio_data']
    
    temp_file_path = os.path.join(settings.MEDIA_ROOT, 'temp_audio.webm')
    with open(temp_file_path, 'wb+') as temp_file:
        for chunk in audio_file.chunks():
            temp_file.write(chunk)

    try:
        result = whisper_model.transcribe(temp_file_path)
        transcribed_text = result['text'] 
        
        parsed_data = {
            'title': transcribed_text.strip(),
            'subject_name': None,
            'due_date': None,
            'due_time': None
        }
        
        lower_text = transcribed_text.lower()
        if 'for subject' in lower_text:
            user_subjects = list(Subject.objects.filter(user=request.user).values_list('name', flat=True))
            
            for subject_name in user_subjects:
                pattern = re.compile(f'for subject {re.escape(subject_name.lower())}', re.IGNORECASE)
                match = pattern.search(lower_text)
                
                if match:
                    parsed_data['subject_name'] = subject_name
                    
                    # --- THIS IS THE CORRECTED LINE ---
                    # The 'flags=re.IGNORECASE' argument has been removed.
                    transcribed_text = re.sub(pattern, '', transcribed_text).strip()
                    # --- END OF CORRECTION ---

                    break

        try:
            datetime_match = re.search(r'(due|on|at) (.+)', transcribed_text, re.IGNORECASE)
            if datetime_match:
                datetime_str = datetime_match.group(2)
                parsed_dt = parse_datetime(datetime_str)
                parsed_data['due_date'] = parsed_dt.strftime('%Y-%m-%d')
                parsed_data['due_time'] = parsed_dt.strftime('%H:%M')
                
                date_phrase_start = transcribed_text.lower().find(datetime_match.group(0).lower())
                if date_phrase_start != -1:
                    transcribed_text = transcribed_text[:date_phrase_start].strip()

        except (ValueError, OverflowError):
            pass

        final_title = transcribed_text.strip()
        if final_title.lower().endswith((' for', ' on', ' at', ' due')):
             final_title = final_title.rsplit(' ', 1)[0]
             
        parsed_data['title'] = final_title if final_title else "Untitled Task"
        
        return JsonResponse({'success': True, 'data': parsed_data})

    except Exception as e:
        print(f"Error during transcription/parsing: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
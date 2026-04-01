import os
import json
from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from .models import Reporter,Issue, CriticalIssue, LowPriorityIssue

# Helper functions for JSON file operations
def index(request):
    return render(request, 'issues/index.html')

def read_data(filename):
    if not os.path.exists(filename):
        return []
    
    if os.path.getsize(filename) == 0:
        return []

    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        # 3. If file has content but it's not valid JSON, return empty list
        return []
    

def write_data(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

def generate_custom_id(filename):
    data = read_data(filename)
    date_prefix = datetime.now().strftime("%Y%m%d-%H%M%S")

    todays_ids = []
    for item in data:
        str_id = str(item.get('id', ''))
        if str_id.startswith(date_prefix):
            try:
                serial = int(str_id.split('-')[-1])
                todays_ids.append(serial)
            except (IndexError, ValueError):
                continue
    
    next_serial = max(todays_ids, default=0) + 1
    return f"{date_prefix}-{next_serial:04d}"

def generate_user_id(filename):
    data = read_data(filename)
    date_prefix = datetime.now().strftime("%Y%m%d")

    todays_ids = []
    for item in data:
        str_id = str(item.get('id', ''))
        if str_id.startswith(date_prefix):
            try:
                serial = int(str_id.split('-')[-1])
                todays_ids.append(serial)
            except (IndexError, ValueError):
                continue
    
    next_serial = max(todays_ids, default=0) + 1
    return f"{date_prefix}-{next_serial:04d}"



@csrf_exempt
def handle_reporters(request):
    if request.method == 'GET':
        try:
            reporters = read_data('reporters.json')
            reporter_id = request.GET.get('id')

            if not reporters or not len(reporters):
                return JsonResponse({'error': 'No reporters found'}, status=404)
            
            # getting a single reporter by ID
            if reporter_id:
                for reporter in reporters:
                    if str(reporter['id']) == str(reporter_id):
                        return JsonResponse(reporter, status=200)
                        # return JsonResponse(reporter, safe=False, status=200)
                return JsonResponse({'error': 'Reporter not found'}, status=404)
            
            # return all reporters
            return JsonResponse(reporters, safe=False, status=200)
            # return JsonResponse(reporters, status=200)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_id = generate_user_id('reporters.json')
            reporter = Reporter(
                # id = data.get('id'),
                id = new_id,
                name = data.get('name'),
                email = data.get('email'),
                team = data.get('team')
            )
            reporter.validate()
            reporters = read_data('reporters.json')
            reporters.append(reporter.to_dict())
            write_data('reporters.json', reporters)
            return JsonResponse(reporter.to_dict(), status=201)
        
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except KeyError as e:
            return JsonResponse({'error': f"Missing field: {str(e)}"}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def handle_issues(request):
    if request.method == 'GET':
        issues = read_data('issues.json')
        issue_id = request.GET.get('id')
        status_filter = request.GET.get('status')
        priority_filter = request.GET.get('priority')

        result = []

        if status_filter in Issue.STATUS_CHOICES:
            status_filtered_issues = [issue for issue in issues if issue['status'] == status_filter]
            if not status_filtered_issues:
                return JsonResponse({'error': 'No issues found with this status'}, status=404)
            for data in status_filtered_issues:
                if data.get('priority') == 'critical':
                    issue = CriticalIssue(**data)
                elif data.get('priority') == 'low':
                    issue = LowPriorityIssue(**data)
                else:
                    issue = Issue(**data)
                issue_data = issue.to_dict()
                issue_data['description_label'] = issue.describe()
                result.append(issue_data)
            return JsonResponse(result, safe=False, status=200)

        if priority_filter in Issue.PRIORITY_CHOICES:
            priority_filtered_issues = [issue for issue in issues if issue['priority'] == priority_filter]
            if not priority_filtered_issues:
                return JsonResponse({'error': 'No issues found with this priority'}, status=404)
            return JsonResponse(priority_filtered_issues, safe=False, status=200)

        if not issues:
            return JsonResponse({'error': 'No issues found'}, status=404)

        if issue_id:
            for data in issues:
                if str(data['id']) == str(issue_id):
                    # return JsonResponse(issue, safe=False, status=200)
                    if data.get('priority') == 'critical':
                        issue = CriticalIssue(**data)
                    elif data.get('priority') == 'low':
                        issue = LowPriorityIssue(**data)
                    else:
                        issue = Issue(**data)
                    issue_data = issue.to_dict()
                    issue_data['description_label'] = issue.describe()
                    return JsonResponse(issue_data, status=200)
            return JsonResponse({'error': 'Issue not found'}, status=404)
        
        # return all issues
        for data in issues:
            if data.get('priority') == 'critical':
                issue = CriticalIssue(**data)
            elif data.get('priority') == 'low':
                issue = LowPriorityIssue(**data)
            else:
                issue = Issue(**data)
            issue_data = issue.to_dict()
            issue_data['description_label'] = issue.describe()
            result.append(issue_data)

        return JsonResponse(result, safe=False, status=200)
        # return JsonResponse(issues, status=200)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_id = generate_custom_id('issues.json')
            data['id'] = new_id
            priority = data.get('priority')

            if priority == 'critical':
                issue = CriticalIssue(**data)
            elif priority == 'low':
                issue = LowPriorityIssue(**data)
            else:
                issue = Issue(**data)

            issue.validate()

            response_data = issue.to_dict()
            response_data['message'] = issue.describe()
            issues = read_data('issues.json')
            issues.append(response_data)
            write_data('issues.json', issues)

            return JsonResponse(response_data, status=201)
        
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except KeyError as e:
            return JsonResponse({'error': f'Missing field: {e}'}, status=400)
        









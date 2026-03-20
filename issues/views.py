import os
import json
from django.http import JsonResponse
from .models import Reporter,Issue, CriticalIssue, LowPriorityIssue

# Helper functions for JSON file operations
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

def handle_reporters(request):
    if request.method == 'GET':
        reporters = read_data('reporters.json')
        reporter_id = request.GET.get('id')

        if not reporters or not len(reporters):
            return JsonResponse({'error': 'No reporters found'}, status=404)
        
        # getting a single reporter by ID
        if reporter_id:
            for reporter in reporters:
                if reporter['id'] == reporter_id:
                    return JsonResponse(reporter, status=200)
            return JsonResponse({'error': 'Reporter not found'}, status=404)
        
        # return all reporters
        return JsonResponse(reporters, status=200)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            reporter = Reporter(
                id = data.get('id'),
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

def handle_issues(request):
    if request.method == 'GET':
        issues = read_data('issues.json')
        issue_id = request.GET.get('id')
        status_filter = request.GET.get('status')
        priority_filter = request.GET.get('priority')

        if status_filter in Issue.STATUS_CHOICES:
            status_filtered_issues = [issue for issue in issues if issue['status'] == status_filter]
            if not status_filtered_issues:
                return JsonResponse({'error': 'No issues found with this status'}, status=404)
            return JsonResponse(status_filtered_issues, status=200)

        if priority_filter in Issue.PRIORITY_CHOICES:
            priority_filtered_issues = [issue for issue in issues if issue['priority'] == priority_filter]
            if not priority_filtered_issues:
                return JsonResponse({'error': 'No issues found with this priority'}, status=404)
            return JsonResponse(priority_filtered_issues, status=200)

        if not issues:
            return JsonResponse({'error': 'No issues found'}, status=404)

        if issue_id:
            for issue in issues:
                if issue['id'] == issue_id:
                    return JsonResponse(issue, status=200)
            return JsonResponse({'error': 'Issue not found'}, status=404)
        
        return JsonResponse(issues, safe=False)
    
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            priority = data.get('priority')

            if priority == 'critical':
                issue = CriticalIssue(**data)
            elif priority == 'low':
                issue = LowPriorityIssue(**data)
            else:
                issue = Issue(**data)

            issue.validate()

            response_data = issue.to_dict()
            issues = read_data('issues.json')
            issues.append(response_data)
            write_data('issues.json', issues)

            return JsonResponse(response_data, status=201)
        
        except ValueError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except KeyError as e:
            return JsonResponse({'error': f'Missing field: {e}'}, status=400)
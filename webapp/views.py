from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ListItem
from django.contrib.auth.models import User

class CustomLoginView(LoginView):
    template_name = 'webapp/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['latest_items'] = ListItem.objects.order_by('-number_in_list')[:10]
        return context

    def get_success_url(self):
        user = self.request.user

        # Debugging: Check the user and their groups
        print(f"User: {user.username}")
        print(f"Groups: {[group.name for group in user.groups.all()]}")

        # Normalize group name comparison
        groups = [group.name.lower() for group in user.groups.all()]

        if 'judge' in groups:
            print("Redirecting to /judge/")
            return '/judge/'
        elif 'listmaker' in groups:
            print("Redirecting to /listmaker/")
            return '/listmaker/'
        else:
            print("Redirecting to /public/")
            return '/public/'  # Default fallback

class CustomLogoutView(LogoutView):
    next_page = '/login/'  # Redirect to the custom login page
    http_method_names = ['get', 'post']

@login_required
def listmaker_view(request):
    return render(request, 'webapp/listmaker.html')

@login_required
def judge_view(request):
    return render(request, 'webapp/judge.html')

def public_view(request):
    return render(request, 'webapp/public.html')

# Combined Read and Write View for Items
@method_decorator(csrf_exempt, name='dispatch')
def manage_items(request, pk=None):
    if request.method == "GET":
        if pk:
            item = get_object_or_404(ListItem, pk=pk)
            data = {
                "number_in_list": item.number_in_list,
                "name": item.name,
                "description": item.description,
                "is_valid": item.is_valid,
                "votes_needed": item.votes_needed,
                "votes_had": item.votes_had,
                "created_by": item.created_by.username,
            }
            return JsonResponse(data)
        else:
            items = ListItem.objects.order_by('-number_in_list')  # Fetch all items
            data = [
                {
                    "number_in_list": item.number_in_list,
                    "name": item.name,
                    "description": item.description,
                    "is_valid": item.is_valid,
                    "votes_needed": item.votes_needed,
                    "votes_had": item.votes_had,
                    "created_by": item.created_by.username,
                }
                for item in items
            ]
            return JsonResponse(data, safe=False)

    elif request.method == "POST":
        try:
            body = json.loads(request.body)
            name = body.get("name", "Unnamed Item")
            description = body.get("description", "")
            votes_needed = body.get("votes_needed", 1)

            # Create the item
            item = ListItem.objects.create(
                name=name,
                description=description,
                votes_needed=votes_needed,
                created_by=request.user,
            )
            return JsonResponse({"success": True, "id": item.number_in_list})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return HttpResponse("Invalid request method", status=405)

@method_decorator(csrf_exempt, name='dispatch')
def judge_item(request, pk):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            vote = body.get("vote")  # 'valid' or 'not valid'

            if vote not in ["valid", "not valid"]:
                return JsonResponse({"success": False, "error": "Invalid vote value."})

            item = get_object_or_404(ListItem, pk=pk)

            # Update votes
            if vote == "valid":
                item.votes_had += 1
            elif vote == "not valid":
                item.votes_had -= 1

            # Check majority
            judges_count = User.objects.filter(groups__name='Judge').count()
            majority = judges_count // 2 + 1

            if item.votes_had >= majority:
                item.is_valid = True
            elif abs(item.votes_had) >= majority:
                item.is_valid = False
            else:
                item.is_valid = None  # Undecided

            item.save()
            return JsonResponse({"success": True, "is_valid": item.is_valid, "votes_had": item.votes_had})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return HttpResponse("Invalid request method", status=405)

@login_required
def fetch_list_items(request):
    items = ListItem.objects.order_by('-number_in_list')
    data = [
        {
            "number_in_list": item.number_in_list,
            "name": item.name,
            "description": item.description,
            "is_valid": item.is_valid,
            "votes_needed": item.votes_needed,
            "votes_had": item.votes_had,
        }
        for item in items
    ]
    return JsonResponse(data, safe=False)

@login_required
def add_list_item(request):
    if request.method == "POST":
        try:
            name = request.POST.get("name", "").strip()
            description = request.POST.get("description", "").strip()

            print("Received POST data:", {"name": name, "description": description})  # Debugging

            if not name or not description:
                return JsonResponse({"success": False, "error": "Both name and description are required."})

            votes_needed = int(request.POST.get("votes_needed", 1))

            # Create new item
            ListItem.objects.create(
                name=name,
                description=description,
                votes_needed=votes_needed,
                created_by=request.user,
            )
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return HttpResponse("Invalid request method", status=405)

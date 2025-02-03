from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ListItem, JudgeVote
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
    next_page = '/login/'  # The URL you want to redirect to after logout

    def dispatch(self, request, *args, **kwargs):
        # Call the parent dispatch to perform the logout
        response = super().dispatch(request, *args, **kwargs)
        # Then force a redirect to the login page
        return redirect(self.next_page)

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

@csrf_exempt
@login_required
def judge_item(request, pk):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            vote = body.get("vote")
            if vote not in ["valid", "not valid", "pending"]:
                return JsonResponse({"success": False, "error": "Invalid vote value."})
            item = get_object_or_404(ListItem, pk=pk)
            judge_vote, created = JudgeVote.objects.get_or_create(
                list_item=item, judge=request.user,
                defaults={'vote': vote}
            )
            if not created:
                judge_vote.vote = vote
                judge_vote.save()
            # Recalculate net votes
            net_votes = 0
            for jv in item.judge_votes.all():
                if jv.vote == "valid":
                    net_votes += 1
                elif jv.vote == "not valid":
                    net_votes -= 1
            item.votes_had = net_votes
            judges_count = User.objects.filter(groups__name='Judge').count()
            majority = judges_count // 2 + 1
            if net_votes >= majority:
                item.is_valid = True
            elif abs(net_votes) >= majority:
                item.is_valid = False
            else:
                item.is_valid = None
            item.save()
            return JsonResponse({
                "success": True,
                "is_valid": item.is_valid,
                "votes_had": item.votes_had
            })
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
def listmaker_view(request):
    return render(request, 'webapp/listmaker.html')

@login_required
@csrf_exempt
def add_list_item(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            name = body.get("name", "").strip()
            description = body.get("description", "").strip()

            if not name or not description:
                return JsonResponse({"success": False, "error": "Name and Description are required."})

            # Create new item
            item = ListItem.objects.create(
                name=name,
                description=description,
                votes_needed=3,  # Default votes needed
                created_by=request.user,
            )

            # Return full item details
            return JsonResponse({
                "success": True,
                "item": {
                    "number_in_list": item.number_in_list,
                    "name": item.name,
                    "description": item.description,
                    "is_valid": item.is_valid,
                    "votes_needed": item.votes_needed,
                    "votes_had": item.votes_had,
                }
            })

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)


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

@csrf_exempt
@login_required
def edit_list_item(request, pk):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            name = body.get("name", "").strip()
            description = body.get("description", "").strip()

            if not name or not description:
                return JsonResponse({"success": False, "error": "Name and Description are required."})

            item = get_object_or_404(ListItem, pk=pk)
            item.name = name
            item.description = description
            item.save()

            return JsonResponse({"success": True})

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

def public_fetch_list_items(request):
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
def fetch_judge_list_items(request):
    items = ListItem.objects.order_by('-number_in_list')
    data = []
    for item in items:
        # Try to get this judge's vote on the item; default to "pending" if none exists.
        try:
            current_vote = JudgeVote.objects.get(list_item=item, judge=request.user).vote
        except JudgeVote.DoesNotExist:
            current_vote = "pending"
        data.append({
            "number_in_list": item.number_in_list,
            "name": item.name,
            "description": item.description,
            "is_valid": item.is_valid,
            "votes_needed": item.votes_needed,
            "votes_had": item.votes_had,
            "current_judge_vote": current_vote
        })
    return JsonResponse(data, safe=False)
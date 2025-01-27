from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ListItem

class CustomLoginView(LoginView):
    template_name = 'webapp/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the latest 10 items
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
    next_page = '/login/'  
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
            items = ListItem.objects.all()
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

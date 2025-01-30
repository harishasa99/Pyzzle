from django.shortcuts import render
from django.http import JsonResponse
import traceback
from .state import get_init_and_goal_states
from .algorithms import BFSAlgorithm, BestFirstAlgorithm, AStarAlgorithm
from .heuristics import HammingHeuristic, ManhattanHeuristic
from django.views.decorators.csrf import csrf_exempt
import json
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.urls import path
import os


def index(request):
    """Renderuje početnu stranicu."""
    return render(request, "game/index.html")


def generate_states(request):
    """API endpoint za generisanje početnog i ciljnog stanja uz izbor dimenzije (3x3 ili 4x4)."""
    if request.method == "GET":
        try:
            size = int(request.GET.get("size", 3))  # Podrazumevano 3x3
            print(f"Size received: {size}")  # Debugging info

            initial_state, goal_state = get_init_and_goal_states(size=size)
            return JsonResponse({
                "initial_state": initial_state,
                "goal_state": goal_state,
                "size": size
            })
        except Exception as e:
            print(f"Error in generate_states: {e}")  # Debugging info
            traceback.print_exc()
            return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def solve_with_image(request):
    """API endpoint za rešavanje slagalice sa podrškom za slike i različite dimenzije."""
    try:
        if request.method == "POST":
            data = json.loads(request.body)
            initial_state = tuple(data.get("initial_state"))  
            goal_state = tuple(data.get("goal_state"))
            algorithm_name = data.get("algorithm", "astar")
            heuristic_name = data.get("heuristic", "manhattan")
            size = int(data.get("size", 3))
            image = data.get("image", "")

            print(f"Received request for solving {size}x{size} puzzle")
            print(f"Initial state: {initial_state}")
            print(f"Goal state: {goal_state}")

            algorithms = {
                "bfs": BFSAlgorithm,
                "greedy": BestFirstAlgorithm,
                "astar": AStarAlgorithm,
            }

            heuristics = {
                "hamming": HammingHeuristic,
                "manhattan": ManhattanHeuristic,
            }

            if algorithm_name not in algorithms or heuristic_name not in heuristics:
                print("Invalid algorithm or heuristic selected!")
                return JsonResponse({"error": "Invalid algorithm or heuristic name"}, status=400)

            algorithm_class = algorithms[algorithm_name]
            heuristic_class = heuristics[heuristic_name]

            algorithm = algorithm_class(heuristic_class())
            solution_steps = algorithm.get_steps(initial_state, goal_state, size)

            if not solution_steps:
                print("No solution found or empty solution!")
            else:
                print(f"Solution steps (backend, {size}x{size}): {solution_steps}")

            return JsonResponse({
                "solution_steps": solution_steps,
                "move_count": len(solution_steps),
                "size": size,
                "image": image
            })

        return JsonResponse({"error": "Invalid request method"}, status=405)
    except Exception as e:
        print(f"Error in solve_with_image: {e}")  
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def upload_image(request):
    """API endpoint za upload slike."""
    if request.method == "POST" and request.FILES.get("image"):
        image = request.FILES["image"]

        # Čuvanje slike u MEDIA_ROOT/uploads/
        file_path = default_storage.save(f"uploads/{image.name}", ContentFile(image.read()))

        return JsonResponse({
            "message": "Image uploaded successfully",
            "image_url": f"/media/{file_path}"
        })
    return JsonResponse({"error": "Invalid request"}, status=400)





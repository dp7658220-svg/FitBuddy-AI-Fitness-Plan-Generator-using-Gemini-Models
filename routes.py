

import os

from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import (
    get_db,
    save_user,
    save_plan,
    get_original_plan,
    get_user,
    update_plan,
    get_all_users,
    get_all_plans,
)
from app.gemini_generator import generate_workout_gemini, update_workout_plan
from app.gemini_flash_generator import generate_nutrition_tip_with_flash

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)


@router.get("/")
def home(request: Request):
    """Home route: displays the user input form."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@router.post("/generate-workout")
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: str = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Receives user input, calls Gemini Pro for the workout plan and
    Gemini Flash for the nutrition tip, stores everything, and
    renders result.html.
    """
    workout_plan = generate_workout_gemini(goal, intensity, age, weight)
    nutrition_tip = generate_nutrition_tip_with_flash(goal)

    save_user(db, user_id, username, age, weight, goal, intensity)
    save_plan(db, user_id, workout_plan, nutrition_tip)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "username": username,
            "user_id": user_id,
            "age": age,
            "weight": weight,
            "goal": goal,
            "intensity": intensity,
            "workout_plan": workout_plan,
            "nutrition_tip": nutrition_tip,
            "updated_plan": None,
        },
    )


@router.post("/submit-feedback")
def submit_feedback(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    """
    Retrieves the user's original plan, sends it plus feedback to
    Gemini Pro, stores the revised plan, and re-renders result.html.
    """
    user = get_user(db, user_id)
    plan = get_original_plan(db, user_id)

    if not user or not plan:
        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "error": "No existing plan found for that User ID. "
                "Please generate a plan first.",
            },
        )

    revised_plan = update_workout_plan(plan.workout_plan, feedback)
    update_plan(db, plan, revised_plan, feedback)

    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "username": user.username,
            "user_id": user.user_id,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "workout_plan": plan.workout_plan,
            "nutrition_tip": plan.nutrition_tip,
            "updated_plan": revised_plan,
            "feedback_submitted": True,
        },
    )


@router.get("/view-all-users")
def view_all_users(request: Request, db: Session = Depends(get_db)):
    """
    Admin dashboard: lists every user alongside their original and
    (if any) feedback-updated workout plan.
    """
    users = get_all_users(db)
    plans = get_all_plans(db)

    plans_by_user = {}
    for plan in plans:
        plans_by_user.setdefault(plan.user_id, plan)

    rows = []

    for user in users:
        plan = plans_by_user.get(user.user_id)

        rows.append(
            {
                "username": user.username,
                "user_id": user.user_id,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
                "workout_plan": plan.workout_plan if plan else "",
                "nutrition_tip": plan.nutrition_tip if plan else "",
                "updated_plan": plan.updated_plan if plan else None,
            }
        )

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": rows,
        },
    )


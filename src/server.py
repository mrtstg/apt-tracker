from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import itertools
from src.dependencies import get_redis_conn
from .models import *
from .parser import SiteParser
from .templates import render_template

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
parser = SiteParser()


def generate_error(message: str, **kwargs) -> HTMLResponse:
    return render_template("error.html", error_message=message, **kwargs)


@app.get("/")
async def index(r=Depends(get_redis_conn)):
    groups = await parser.get_cached_groups(r)
    if len(groups) == 0:
        return generate_error(
            "Не удалось получить информацию о группах с сайта. Попробуйте позже."
        )

    group_infos = await parser.get_groups_info_cached(r, [i.id for i in groups])
    # точно распаршеные группы
    filtered_info: list[GroupInfo] = list(filter(lambda x: x is not None, group_infos))  # type: ignore
    if len(group_infos) != len(filtered_info):
        return generate_error(
            "Не удалось получить полную информацию о группах с сайта. Попробуйте позже."
        )
    # бюджетники
    budget_groups = sorted(
        list(filter(lambda x: x.is_budget(), filtered_info)), key=lambda x: x.name
    )
    # небюджетники
    non_budget_groups = sorted(
        list(filter(lambda x: not x.is_budget(), filtered_info)), key=lambda x: x.name
    )

    # всего студентов
    total_students = sum([len(i.students) for i in filtered_info])
    # общий план
    total_plan = sum([i.plan for i in filtered_info])
    # план бюджетников
    total_budget_plan = sum(list(map(lambda x: x.plan, budget_groups)))
    # льготники на бюджете (не уверен что бывает другое, но на всякий)
    budget_benefits = len(
        list(
            filter(
                lambda x: x.benefit,
                itertools.chain.from_iterable(map(lambda x: x.students, budget_groups)),
            )
        )
    )
    # все студенты, одним массивом
    all_students: list[Student] = list(
        itertools.chain.from_iterable(map(lambda x: x.students, filtered_info))
    )
    # всего льготников
    total_benefits = len(list(filter(lambda x: x.benefit, all_students)))
    benefits_percentage = round(budget_benefits / total_budget_plan, 2)
    return render_template(
        "index.html",
        total_students=total_students,
        total_benefits=total_benefits,
        total_plan=total_plan,
        total_budget_plan=total_budget_plan,
        benefits_percentage=benefits_percentage,
        budget_groups=budget_groups,
        non_budget_groups=non_budget_groups,
    )

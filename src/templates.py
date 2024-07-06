import jinja2
from fastapi.responses import HTMLResponse

loader = jinja2.FileSystemLoader("templates")
env = jinja2.Environment(loader=loader)


def render_template(template_name: str, **kwargs) -> HTMLResponse:
    template = env.get_template(template_name)
    return HTMLResponse(template.render(**kwargs))

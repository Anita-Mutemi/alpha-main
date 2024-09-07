from fastapi import FastAPI, Depends, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from .dependencies import RouterTags
from .file_handlers import upload_investors
from packages.crm import util

from . import auth
from .routers import clients, collections, entities, lookup, monitoring, parser, projects

# Logger setup
# logfile = util.project_root() / "logs/web" / f"web.log"
# logger.add(logfile.absolute(), rotation="00:00", format="[Web App] {time} {name} {level}: {message}",
#           level="DEBUG", backtrace=True, diagnose=True)
# api_logger.remove()
# logfile = util.project_root() / "logs/web" / f"web_api.log"
# api_logger.add(sys.stderr, format="[Web Api] {time} {name} {level}: {message}", level="DEBUG")
# api_logger.add(logfile.absolute(), rotation="00:00", format="[Web Api] {time} {name} {level}: {message}",
#           level="DEBUG", backtrace=True, diagnose=True)

# CORS origins
origins = ["*", "staging.alphaterminal.pro", "https://staging.alphaterminal.pro"]

# Main app for crm_api
app = FastAPI()

# Auth routes
app.include_router(auth.router, prefix="")  # root auth routes
app.include_router(auth.router, prefix="/v1")  # v1 auth routes

# Parser app and routes
parsing = FastAPI(dependencies=[Depends(auth.get_current_active_user)])
parsing.include_router(parser.router, prefix="")
parsing.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Tags metadata for v1 API
tags_metadata = sorted([{"name": t.value} for t in RouterTags], key=lambda x: x["name"])

# v1 app and routes
v1 = FastAPI(dependencies=[Depends(auth.get_current_active_user)], openapi_tags=tags_metadata)

v1.include_router(entities.router, prefix="")
v1.include_router(clients.router, prefix="/clients", tags=[RouterTags.clients])
v1.include_router(lookup.router, prefix="/lookup")
v1.include_router(monitoring.router, prefix="/monitoring", tags=[RouterTags.logs])
v1.include_router(projects.router, prefix="/projects", tags=[RouterTags.projects])
v1.include_router(collections.router, prefix="/collections")

# CORS middleware for main app and v1 app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

v1.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount parsing and v1 apps to the main app
app.mount("/parsing", parsing)
app.mount("/v1", v1)


# Heartbeat route
@app.get("/heartbeat", status_code=204)
def heartbeat():
    pass


# Upload investors route
@app.post("/uploads/investors")
def linkedin_upload(_: auth.LoggedInUser, file: UploadFile):
    # Pass the file-like object to the handler
    upload_investors(file)

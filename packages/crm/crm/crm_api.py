from fastapi import FastAPI, Depends, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
import sys

from packages.crm.crm.dependencies import RouterTags
from packages.crm.crm.file_handlers import upload_investors
from packages.crm import util

from . import auth
from packages.crm.crm.routers import clients, collections, entities, lookup, monitoring, parser, projects


# logfile = util.project_root() / "logs/web" / f"web.log"
# logger.add(logfile.absolute(), rotation="00:00", format="[Web App] {time} {name} {level}: {message}",
#           level="DEBUG", backtrace=True, diagnose=True)
# api_logger.remove()
# logfile = util.project_root() / "logs/web" / f"web_api.log"
# api_logger.add(sys.stderr, format="[Web Api] {time} {name} {level}: {message}", level="DEBUG")
# api_logger.add(logfile.absolute(), rotation="00:00", format="[Web Api] {time} {name} {level}: {message}",
#           level="DEBUG", backtrace=True, diagnose=True)


origins = [
    "*",
    "staging.alphaterminal.pro",
    "https://staging.alphaterminal.pro",
    "https://illustrious-palmier-9d22e4.netlify.app",
    "https://desolate-harbor-30841-707d8d470803.herokuapp.com",
    "https://66e81f3100b3a30008c9b1b6--superlative-kelpie-338e57.netlify.app"
]

app = FastAPI()
app.include_router(auth.router, prefix='')
app.include_router(auth.router, prefix='/v1')

app.include_router(parser.router, prefix='',
                   dependencies=[Depends(auth.get_current_active_user)])

parsing = FastAPI(
    dependencies=[Depends(auth.get_current_active_user)]
)
parsing.include_router(parser.router, prefix='')
parsing.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


tags_metadata = sorted([{"name": t.value} for t in RouterTags], key=lambda x: x['name'])

v1 = FastAPI(
    dependencies=[Depends(auth.get_current_active_user)],
    openapi_tags=tags_metadata
)

v1.include_router(entities.router, prefix='')
v1.include_router(clients.router, prefix='/clients', tags=[RouterTags.clients])
v1.include_router(lookup.router, prefix='/lookup')
v1.include_router(monitoring.router, prefix='/monitoring', tags=[RouterTags.logs])
v1.include_router(projects.router, prefix='/projects', tags=[RouterTags.projects])
v1.include_router(collections.router, prefix='/collections')


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


app.mount('/parsing', parsing)
app.mount('/v1', v1)


@app.get('/heartbeat', status_code=204)
def hearbeat():
    pass


@app.post('/uploads/investors')
def linkedin_upload(_: auth.LoggedInUser, file: UploadFile):
    # pass the file-like object to handler
    upload_investors(file)

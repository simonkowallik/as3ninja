# -*- coding: utf-8 -*-
"""API"""
from typing import List, Optional, Union

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from . import __description__, __projectname__, __version__
from .declaration import (
    AS3Declaration,
    AS3JSONDecodeError,
    AS3TemplateSyntaxError,
    AS3UndefinedError,
)
from .gitget import Gitget, GitgetException
from .schema import AS3Schema, AS3SchemaVersionError, AS3ValidationError
from .utils import deserialize

CORS_SETTINGS = {
    "allow_origins": [
        "http://localhost",
        "http://localhost:8000",
        "https://localhost",
        "https://localhost:8000",
    ],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}


class AS3ValidationResult(BaseModel):
    """AS3 declaration Schema validation result"""

    valid: bool
    error: Optional[str]


class LatestVersion(BaseModel):
    """AS3 /schema/latest_version response"""

    latest_version: str


class Error(BaseModel):
    """Generic Error Model"""

    code: int
    message: str


class AS3DeclareGit(BaseModel):
    """Model for an AS3 Declaration from a Git repository"""

    repository: str
    branch: Optional[str]
    commit: Optional[str]
    depth: int = 1
    template_configuration: Optional[Union[str, List[str]]]


class AS3Declare(BaseModel):
    """Model for an inline AS3 Declaration"""

    template_configuration: Union[dict, List[dict]]
    declaration_template: str


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)

app.add_middleware(CORSMiddleware, **CORS_SETTINGS)


@app.on_event("startup")
def startup():
    # preload AS3Schema Class - assume Schemas are available
    _ = AS3Schema()


@app.get("/")
async def default_redirect():
    """redirect / to /api/docs"""
    return RedirectResponse(url="/api/docs")


@app.get("/docs")
async def docs_redirect():
    """redirect /docs to /api/docs"""
    return RedirectResponse(url="/api/docs")


@app.get("/redoc")
async def redoc_redirect():
    """redirect /redoc to /api/redoc"""
    return RedirectResponse(url="/api/redoc")


@app.get("/openapi.json")
async def openapi_redirect():
    """redirect /openapi.json to /api/openapi.json"""
    return RedirectResponse(url="/api/openapi.json")


api = FastAPI(
    openapi_prefix="/api",
    title=__projectname__,
    description=__description__,
    version=__version__,
)

api.add_middleware(CORSMiddleware, **CORS_SETTINGS)


@api.get("/schema/latest_version")
async def get_schema_latest_version():
    """Returns latest known AS3 Schema version"""
    return LatestVersion(latest_version=AS3Schema().latest_version)


@api.get("/schema/schema")
async def get_schema_schema_version(
    version: str = Query("latest", title="AS3 Schema version to get"),
):
    """Returns AS3 Schema of ``version``"""
    try:
        return AS3Schema(version=version).schema
    except AS3SchemaVersionError as exc:
        error = Error(code=400, message=str(exc))
        raise HTTPException(status_code=error.code, detail=error.message)


@api.get("/schema/schemas")
async def get_schema_schemas():
    """Returns all known AS3 Schemas"""
    return AS3Schema().schemas


@api.get("/schema/versions")
async def get_schema_versions():
    """Returns array of version numbers for all known AS3 Schemas"""
    return AS3Schema().versions


@api.post("/schema/validate", response_model=AS3ValidationResult)
async def _schema_validate(
    declaration: dict,
    version: str = Query("latest", title="AS3 Schema version to validation against"),
):
    """Validate declaration in POST payload against AS3 Schema of ``version`` (Default: latest)"""
    try:
        AS3Schema(version=version).validate(declaration=declaration)
        return AS3ValidationResult(valid=True)
    except AS3SchemaVersionError as exc:
        error = Error(code=400, message=str(exc))
        raise HTTPException(status_code=400, detail=error.message)
    except AS3ValidationError as exc:
        return AS3ValidationResult(valid=False, error=str(exc))


@api.post("/declaration/transform")
async def post_declaration_transform(as3d: AS3Declare):
    """Transforms an AS3 declaration template, see ``AS3Declare`` for details on the expected input. Returns the AS3 Declaration."""
    error = None
    try:
        d = AS3Declaration(
            template_configuration=as3d.template_configuration,
            declaration_template=as3d.declaration_template,
        )
        return d.declaration

    except (
        AS3SchemaVersionError,
        AS3JSONDecodeError,
        AS3TemplateSyntaxError,
        AS3UndefinedError,
    ) as exc:
        error = Error(code=400, message=str(exc))
        raise HTTPException(status_code=error.code, detail=error.message)


@api.post("/declaration/transform/git")
async def post_declaration_git_transform(as3d: AS3DeclareGit):
    """Transforms an AS3 declaration template, see ``AS3DeclareGit`` for details on the expected input. Returns the AS3 Declaration."""
    error = None
    try:
        template_configuration: list = []
        with Gitget(
            repository=as3d.repository,
            branch=as3d.branch,
            commit=as3d.commit,
            depth=as3d.depth,
        ) as gitrepo:
            if as3d.template_configuration and isinstance(
                as3d.template_configuration, list
            ):
                for config_file in as3d.template_configuration:
                    template_configuration.append(
                        deserialize(datasource=f"{gitrepo.repodir}/{config_file}")
                    )
            elif as3d.template_configuration:
                template_configuration.append(
                    deserialize(
                        datasource=f"{gitrepo.repodir}/{as3d.template_configuration}"
                    )
                )
            else:
                try:
                    template_configuration.append(
                        deserialize(datasource=f"{gitrepo.repodir}/ninja.json")
                    )
                except:
                    # json failed, try yaml, then yml
                    try:
                        template_configuration.append(
                            deserialize(datasource=f"{gitrepo.repodir}/ninja.yaml")
                        )
                    except:
                        template_configuration.append(
                            deserialize(datasource=f"{gitrepo.repodir}/ninja.yml")
                        )
            template_configuration.append({"as3ninja": {"git": gitrepo.info}})
            d = AS3Declaration(
                template_configuration=template_configuration,
                jinja2_searchpath=gitrepo.repodir,
            )
            return d.declaration
    except (
        GitgetException,
        AS3SchemaVersionError,
        AS3JSONDecodeError,
        AS3TemplateSyntaxError,
        AS3UndefinedError,
    ) as exc:
        error = Error(code=400, message=str(exc))
        raise HTTPException(status_code=error.code, detail=error.message)


# mount api
app.mount("/api", api)

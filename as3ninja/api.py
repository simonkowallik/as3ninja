# -*- coding: utf-8 -*-
"""
AS3Ninja's REST API
"""

# pylint: disable=C0330 # Wrong hanging indentation before block
# pylint: disable=C0301 # Line too long

from typing import List, Optional, Union

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import RedirectResponse

from . import __description__, __projectname__, __version__
from .declaration import AS3Declaration
from .exceptions import (
    AS3JSONDecodeError,
    AS3SchemaVersionError,
    AS3TemplateSyntaxError,
    AS3UndefinedError,
    AS3ValidationError,
)
from .gitget import Gitget, GitgetException
from .schema import AS3Schema
from .templateconfiguration import (
    AS3TemplateConfiguration,
    AS3TemplateConfigurationError,
)

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

    repository: str = Field(..., description="Git repository to clone")
    branch: Optional[str] = Field(None, description="Branch of git repository")
    commit: Optional[str] = Field(
        None, description="Git commit id or HEAD~<int> syntax"
    )
    depth: int = Field(1, description="git --depth: Number of commits to clone")
    template_configuration: Optional[Union[List[Union[dict, str]], dict, str]] = Field(
        None, description="Template Configuration to use"
    )
    declaration_template: Optional[str] = Field(
        None, description="File to use as the Declaration Template"
    )


class AS3Declare(BaseModel):
    """Model for an inline AS3 Declaration"""

    template_configuration: Union[List[dict], dict] = Field(
        ..., description="Template Configuration to use"
    )
    declaration_template: str = Field(..., description="Declaration Template")


app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)  # pylint: disable=C0103

app.add_middleware(CORSMiddleware, **CORS_SETTINGS)


@app.on_event("startup")
def startup():
    """preload AS3Schema Class - assume Schemas are available"""
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


api = FastAPI(  # pylint: disable=C0103
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
    try:
        as3tc = AS3TemplateConfiguration(as3d.template_configuration)

        as3declaration = AS3Declaration(
            template_configuration=as3tc.dict(),
            declaration_template=as3d.declaration_template,
        )
        return as3declaration.dict()

    except (
        AS3SchemaVersionError,
        AS3JSONDecodeError,
        AS3TemplateSyntaxError,
        AS3UndefinedError,
        AS3TemplateConfigurationError,
    ) as exc:
        error = Error(code=400, message=str(exc))
        raise HTTPException(status_code=error.code, detail=error.message)


@api.post("/declaration/transform/git")
async def post_declaration_git_transform(as3d: AS3DeclareGit):
    """Transforms an AS3 declaration template, see ``AS3DeclareGit`` for details on the expected input. Returns the AS3 Declaration."""
    try:
        with Gitget(
            repository=as3d.repository,
            branch=as3d.branch,
            commit=as3d.commit,
            depth=as3d.depth,
        ) as gitrepo:
            as3tc = AS3TemplateConfiguration(
                template_configuration=as3d.template_configuration,
                base_path=f"{gitrepo.repodir}/",
                overlay={"as3ninja": {"git": gitrepo.info}},
            )

            if as3d.declaration_template is not None:
                with open(
                    f"{gitrepo.repodir}/{as3d.declaration_template}", "r"
                ) as template:
                    as3d.declaration_template = template.read()

            as3declaration = AS3Declaration(
                template_configuration=as3tc.dict(),
                declaration_template=as3d.declaration_template,
                jinja2_searchpath=gitrepo.repodir,
            )
            return as3declaration.dict()
    except (
        GitgetException,
        AS3SchemaVersionError,
        AS3JSONDecodeError,
        AS3TemplateSyntaxError,
        AS3UndefinedError,
        AS3TemplateConfigurationError,
        KeyError,  # missing declaration_template (explicit and within as3ninja.)
    ) as exc:
        error = Error(code=400, message=str(exc))
        raise HTTPException(status_code=error.code, detail=error.message)


# mount api
app.mount("/api", api)

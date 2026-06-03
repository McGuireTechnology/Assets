from contextlib import asynccontextmanager
from typing import Any

from fastapi import Body, Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlmodel import SQLModel, Session, select

from app.config import DATABASE_KIND, DATABASE_URL, SKIP_DB_INIT
from app.database import get_session, init_db
from app.models import (
    AutonomousSystem,
    ConfigurationItem,
    IeeeRegistry,
    IpAddress,
    IpAggregate,
    IpPrefix,
    IpRange,
    L2Role,
    L3Role,
    MacAddress,
    MacAddressBlockAssignment,
    RegionalInternetRegistry,
    Site,
    Vlan,
    VirtualRoutingForwarding,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not SKIP_DB_INIT:
        init_db()
    yield


app = FastAPI(
    title="Assets API",
    version="26.6.0",
    description="Backend API for the McGuire Technology, LLC - Assets application.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_origin_regex=r"^http://(localhost|127\.0\.0\.1):\d+$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "assets-api", "database": DATABASE_KIND}


def register_crud_routes(path: str, model: type[SQLModel]) -> None:
    def list_route(session: Session = Depends(get_session)) -> list[SQLModel]:
        return list_records(session, model)

    def get_route(record_id: int, session: Session = Depends(get_session)) -> SQLModel:
        return get_record(session, model, record_id)

    def create_route(
        payload: dict[str, Any] = Body(...),
        session: Session = Depends(get_session),
    ) -> SQLModel:
        try:
            record = model.model_validate(payload)
            session.add(record)
            session.commit()
            session.refresh(record)
            return record
        except SQLAlchemyError as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to create {model.__name__}",
            ) from error

    def update_route(
        record_id: int,
        payload: dict[str, Any] = Body(...),
        session: Session = Depends(get_session),
    ) -> SQLModel:
        record = get_record(session, model, record_id)

        for key, value in payload.items():
            if key != "id" and hasattr(record, key):
                setattr(record, key, value)

        try:
            session.add(record)
            session.commit()
            session.refresh(record)
            return record
        except SQLAlchemyError as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to update {model.__name__} {record_id}",
            ) from error

    def delete_route(record_id: int, session: Session = Depends(get_session)) -> dict[str, int]:
        record = get_record(session, model, record_id)

        try:
            session.delete(record)
            session.commit()
            return {"id": record_id}
        except SQLAlchemyError as error:
            raise HTTPException(
                status_code=400,
                detail=f"Unable to delete {model.__name__} {record_id}",
            ) from error

    app.add_api_route(path, list_route, methods=["GET"], response_model=list[model])
    app.add_api_route(path, create_route, methods=["POST"], response_model=model, status_code=201)
    app.add_api_route(f"{path}/{{record_id}}", get_route, methods=["GET"], response_model=model)
    app.add_api_route(f"{path}/{{record_id}}", update_route, methods=["PUT"], response_model=model)
    app.add_api_route(f"{path}/{{record_id}}", delete_route, methods=["DELETE"])


def list_records[T: SQLModel](session: Session, model: type[T]) -> list[T]:
    try:
        return session.exec(select(model)).all()
    except SQLAlchemyError as error:
        raise HTTPException(
            status_code=503,
            detail=f"Database unavailable at {DATABASE_URL}",
        ) from error


def get_record[T: SQLModel](session: Session, model: type[T], record_id: int) -> T:
    record = session.get(model, record_id)

    if record is None:
        raise HTTPException(status_code=404, detail=f"{model.__name__} {record_id} not found")

    return record


register_crud_routes("/api/configuration-items", ConfigurationItem)
register_crud_routes("/api/l2/roles", L2Role)
register_crud_routes("/api/l2/ieee-registries", IeeeRegistry)
register_crud_routes("/api/l2/mac-address-block-assignments", MacAddressBlockAssignment)
register_crud_routes("/api/l2/vlans", Vlan)
register_crud_routes("/api/l2/mac-addresses", MacAddress)
register_crud_routes("/api/l3/roles", L3Role)
register_crud_routes("/api/ipam/ip-addresses", IpAddress)
register_crud_routes("/api/ipam/ip-prefixes", IpPrefix)
register_crud_routes("/api/ipam/ip-roles", L3Role)
register_crud_routes("/api/ipam/virtual-routing-forwardings", VirtualRoutingForwarding)
register_crud_routes("/api/ipam/sites", Site)
register_crud_routes("/api/ipam/regional-internet-registries", RegionalInternetRegistry)
register_crud_routes("/api/ipam/autonomous-systems", AutonomousSystem)
register_crud_routes("/api/ipam/ip-aggregates", IpAggregate)
register_crud_routes("/api/ipam/ip-ranges", IpRange)

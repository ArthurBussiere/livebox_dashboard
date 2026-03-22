from fastapi import APIRouter, Depends

from core.session import LiveboxSession
from core.auth import get_session
from models.devices import (
    DeviceAlternativeRequest,
    DeviceAlternativeRules,
    DeviceFind,
    DeviceFindByIP,
    DeviceSetName,
    DeviceSetType,
    DeviceTagRequest,
)

router = APIRouter()


@router.get("")
async def get_devices(
    expression: str | None = None,
    flags: str = "",
    session: LiveboxSession = Depends(get_session),
):
    params: dict = {"flags": flags}
    if expression is not None:
        params["expression"] = expression
    return await session.call("Devices", "get", params)


@router.post("/find")
async def find_devices(body: DeviceFind, session: LiveboxSession = Depends(get_session)):
    return await session.call("Devices", "find", body.model_dump(exclude_none=True))


@router.get("/by-ip")
async def find_by_ip(
    body: DeviceFindByIP, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "Devices",
        "findByIPAddress",
        body.model_dump(),
    )


@router.get("/{key}")
async def fetch_device(
    key: str, flags: str = "", session: LiveboxSession = Depends(get_session)
):
    return await session.call("Devices", "fetchDevice", {"key": key, "flags": flags})


@router.put("/{key}")
async def set_device(
    key: str, body: dict, session: LiveboxSession = Depends(get_session)
):
    return await session.call("Devices.Device", "set", body)


@router.delete("/{key}")
async def destroy_device(key: str, session: LiveboxSession = Depends(get_session)):
    return await session.call("Devices", "destroyDevice", {"key": key})


@router.put("/{key}/name")
async def set_name(
    key: str, body: DeviceSetName, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "Devices.Device", "setName", body.model_dump()
    )


@router.post("/{key}/name")
async def add_name(
    key: str, body: DeviceSetName, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "Devices.Device", "addName", body.model_dump()
    )


@router.delete("/{key}/name")
async def remove_name(
    key: str, source: str, session: LiveboxSession = Depends(get_session)
):
    return await session.call("Devices.Device", "removeName", {"source": source})


@router.put("/{key}/type")
async def set_type(
    key: str, body: DeviceSetType, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "Devices.Device", "setType", body.model_dump()
    )


@router.delete("/{key}/type")
async def remove_type(
    key: str, source: str, session: LiveboxSession = Depends(get_session)
):
    return await session.call("Devices.Device", "removeType", {"source": source})


@router.get("/{key}/tags/{tag}")
async def has_tag(
    key: str,
    tag: str,
    body: DeviceTagRequest | None = None,
    session: LiveboxSession = Depends(get_session),
):
    params: dict = {"tag": tag}
    if body:
        params.update(body.model_dump(exclude_none=True))
    return await session.call("Devices.Device", "hasTag", params)


@router.put("/{key}/tags/{tag}")
async def set_tag(
    key: str,
    tag: str,
    body: DeviceTagRequest,
    session: LiveboxSession = Depends(get_session),
):
    params = body.model_dump(exclude_none=True)
    params["tag"] = tag
    return await session.call("Devices.Device", "setTag", params)


@router.delete("/{key}/tags/{tag}")
async def clear_tag(
    key: str,
    tag: str,
    body: DeviceTagRequest | None = None,
    session: LiveboxSession = Depends(get_session),
):
    params: dict = {"tag": tag}
    if body:
        params.update(body.model_dump(exclude_none=True))
    return await session.call("Devices.Device", "clearTag", params)


@router.get("/{key}/topology")
async def get_topology(
    key: str,
    expression: str = "",
    traverse: str = "",
    flags: str = "",
    session: LiveboxSession = Depends(get_session),
):
    return await session.call(
        "Devices.Device",
        "topology",
        {"expression": expression, "traverse": traverse, "flags": flags},
    )


@router.get("/{key}/parameters")
async def get_parameters(
    key: str,
    parameter: str = "",
    expression: str = "",
    traverse: str = "",
    session: LiveboxSession = Depends(get_session),
):
    return await session.call(
        "Devices.Device",
        "getParameters",
        {"parameter": parameter, "expression": expression, "traverse": traverse},
    )


@router.put("/{key}/alternative")
async def set_alternative(
    key: str,
    body: DeviceAlternativeRequest,
    session: LiveboxSession = Depends(get_session),
):
    return await session.call(
        "Devices.Device", "setAlternative", {"alternative": body.alternative}
    )


@router.delete("/{key}/alternative")
async def remove_alternative(
    key: str,
    body: DeviceAlternativeRequest,
    session: LiveboxSession = Depends(get_session),
):
    return await session.call(
        "Devices.Device", "removeAlternative", {"alternative": body.alternative}
    )

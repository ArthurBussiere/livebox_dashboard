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


@router.get("/{key}/name/probe")
async def probe_set_name(
    key: str, name: str = "test", session: LiveboxSession = Depends(get_session)
):
    """Debug endpoint: try every known rename approach and return raw Livebox responses."""
    attempts = [
        ("Devices", "setName", {"key": key, "name": name, "source": "GUI"}),
        ("Devices", "setName", {"key": key, "name": name}),
        ("Devices", "addName", {"key": key, "name": name, "source": "GUI"}),
        (f"Devices.Device[{key}]", "setName", {"name": name, "source": "GUI"}),
        (f"Devices.Device[{key}]", "setName", {"name": name}),
        (f"Devices.Device[{key.lower()}]", "setName", {"name": name, "source": "GUI"}),
        (f"Devices.Device[{key}]", "setName", {"name": name, "source": "webui"}),
    ]
    results = []
    for svc, mth, params in attempts:
        raw = await session.raw_call(svc, mth, params)
        results.append({"service": svc, "method": mth, "params": params, "response": raw})
    return results


@router.put("/{key}/name")
async def set_name(
    key: str, body: DeviceSetName, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "Devices", "setName", {"key": key, "name": body.name, "source": body.source}
    )


@router.post("/{key}/name")
async def add_name(
    key: str, body: DeviceSetName, session: LiveboxSession = Depends(get_session)
):
    return await session.call(
        "Devices", "addName", {"key": key, "name": body.name, "source": body.source}
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

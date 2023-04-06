from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_get_dr
from homeassistant.helpers.area_registry import async_get as async_get_ar
from homeassistant.helpers.entity_registry import async_get as async_get_entities
from homeassistant.const import EVENT_STATE_CHANGED
import logging

logger = logging.getLogger(__name__)
import requests
from homeassistant.helpers.start import async_at_start
from homeassistant.core import Event
from .const import DOMAIN
import threading
import time
from datetime import timedelta
import pysher
import json

entities_can_sync = []

async def async_setup(hass: HomeAssistant, config: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    async_at_start(hass, on_started)
    return True


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry):
    hass.data[DOMAIN]["config"] = config.data
    return True


def sync_devices(hass: HomeAssistant):
    token = hass.data[DOMAIN].get("config", {}).get("token", None)
    domain = hass.data[DOMAIN].get("config", {}).get("domain", None)
    if token is None:
        logger.warn("Couldn't sync devices without token")
        return

    if domain is None:
        return

    dr = async_get_dr(hass)
    devices = []

    for device in dr.devices.values():
        if device.area_id is None or device.area_id == "":
            continue
        devices.append(
            {
                "id": device.id,
                "area_id": device.area_id,
                "disabled": True if device.disabled_by is not None else False,
                "hw_version": device.hw_version,
                "sw_version": device.sw_version,
                "manufacturer": device.manufacturer,
                "model": device.model,
                "name": device.name,
                "config_entries": list(device.config_entries),
            }
        )

    # sync devices
    r = requests.put(
        "https://" + domain + "/api/ha-sync/devices?token=" + token,
        json=devices,
        verify=False,
    )
    if r.status_code != 200:
        logger.warn(r.reason)


def sync_states(hass: HomeAssistant):
    token = hass.data[DOMAIN].get("config", {}).get("token", None)
    domain = hass.data[DOMAIN].get("config", {}).get("domain", None)
    if token is None:
        logger.warn("Couldn't sync entities without token")
        return

    if domain is None:
        return

    states = []
    for _, state in enumerate(hass.states.async_all()):
        
        states.append(state.as_dict())

    r = requests.put(
        "https://" + domain + "/api/ha-sync/states?token=" + token,
        json=states,
        verify=False,
    )
    if r.status_code != 200:
        logger.warn(r.reason)


def sync_entities(hass: HomeAssistant):
    token = hass.data[DOMAIN].get("config", {}).get("token", None)
    domain = hass.data[DOMAIN].get("config", {}).get("domain", None)
    if token is None:
        logger.warn("Couldn't sync entities without token")
        return

    if domain is None:
        return

    entities = []
    dr = async_get_dr(hass)
    er = async_get_entities(hass)
    # logger.warn(json.dumps(async_get_entities(hass).entities))
    for _, entry in er.entities.items():
        if entry.area_id == "" or entry.area_id is None:
            divice = dr.async_get(entry.device_id)
            if device.area_id is None or device.area_id == "":
                continue
        entities_can_sync.append(entry.entity_id)
        entities.append(
            {
                "entity_id": entry.entity_id,
                "unique_id": entry.unique_id,
                "platform": entry.platform,
                "area_id": entry.area_id,
                # 'capabilities': dict(entry.capabilities),
                "device_class": entry.device_class,
                "device_id": entry.device_id,
                "disabled": False if entry.disabled_by is None else True,
                # 'entity_category': entry.entity_category, <EntityCategory.DIAGNOSTIC: 'diagnostic'>,
                "id": entry.id,
                "name": entry.name,
                # 'options': entry.options,
                "original_device_class": entry.original_device_class,
                "original_icon": entry.original_icon,
                "original_name": entry.original_name,
                "supported_features": entry.supported_features,
                "unit_of_measurement": entry.unit_of_measurement,
            }
        )

    r = requests.put(
        "https://" + domain + "/api/ha-sync/entities?token=" + token,
        json=entities,
        verify=False,
    )
    if r.status_code != 200:
        logger.warn(r.reason)
        

def sync_areas(hass: HomeAssistant):
    token = hass.data[DOMAIN].get("config", {}).get("token", None)
    domain = hass.data[DOMAIN].get("config", {}).get("domain", None)
    if token is None:
        logger.warn("Couldn't sync areas without token")
        return

    ar = async_get_ar(hass)
    areas = list()
    for area in ar.async_list_areas():
        areas.append(
            {
                "id": area.id,
                "name": area.name,
                "normalized_name": area.normalized_name,
                "picture": area.picture,
            }
        )

    r = requests.put(
         "https://" + domain + "/api/ha-sync/areas?token=" + token, json=areas, verify=False,
    )
    if r.status_code != 200:
        logger.warn(r.reason)


def update_state(hass: HomeAssistant, event: Event):
    # logger.warn('state changed started')
    data = event.data
    entity_id: str = data["entity_id"]
    if entity_id in entities_can_sync != True:
        return

    token = hass.data[DOMAIN].get("config", {}).get("token", None)
    domain = hass.data[DOMAIN].get("config", {}).get("domain", None)
    if token is None:
        return

    if domain is None:
        return

    r = requests.put(
        "https://" + domain + "/api/ha-sync/state?token=" + token,
        json=data.get("new_state").as_dict(),
        verify=False,
    )
    if r.status_code != 200:
        logger.warn(r.reason)


def sync_all(hass):
    logger.warn("begin to sync all devices, 3600 seconds once")
    while True:
        sync_areas(hass)
        sync_devices(hass)
        sync_entities(hass)
        sync_states(hass)
        time.sleep(300)


def heart_beat(hass):
    domain = hass.data[DOMAIN].get("config", {}).get("domain", None)
    token = hass.data[DOMAIN].get("config", {}).get("token", None)
    while True:
        if domain is not None:
            requests.get(
                "https://" + domain + "/api/heart-beat?token=" + token,
                verify=False,
            )
        time.sleep(300)


def on_started(hass: HomeAssistant):
    logger.warn("on_started")
    threading.Thread(target=sync_all, args=(hass,)).start()
    threading.Thread(target=heart_beat, args=(hass,)).start()

    def on_state_changed(event: Event):
        update_state(hass, event)

    hass.bus.async_listen(EVENT_STATE_CHANGED, on_state_changed)
    # threading.Thread(target=test_token, args=(hass,)).start()
    handle_action(hass)


def handle_action(hass):
    hassID = hass.data[DOMAIN].get("config", {}).get("id", None)
    if hassID is None:
        return
    pusherAppKey = (
        hass.data[DOMAIN]
        .get("config", {})
        .get("pusher", {})
        .get("app_key", "f3838bc732eed964d75b")
    )
    pusher = pysher.Pusher(pusherAppKey, cluster="ap1")

    # logger.info("subscribe " + hassID)

    def action(data):
        # print("processing data:", data)
        jsonData = json.loads(data)
        hass.services.call(**jsonData)

    def connect_handler(data):
        # logger.info(data)
        channel = pusher.subscribe(hassID)
        channel.bind("action", action)

    pusher.connection.bind("pusher:connection_established", connect_handler)
    pusher.connect()

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import async_get as async_get_dr
from homeassistant.helpers.area_registry import async_get as async_get_ar
import logging
logger = logging.getLogger(__name__)
import requests
from homeassistant.helpers.start import async_at_start
from homeassistant.const import EVENT_STATE_CHANGED
from homeassistant.core import Event
from .const import DOMAIN
import threading


async def async_setup(hass: HomeAssistant, config: ConfigEntry):
    hass.data.setdefault(DOMAIN, {})
    # async_track_state_change_event(hass, action=on_state_changed)
    async_at_start(hass, on_started)
    
    
    return True


async def async_setup_entry(hass: HomeAssistant, config: ConfigEntry):
    hass.data[DOMAIN]['config'] = config.data

    def on_state_changed(event: Event):
        update_state(hass, event)

    # hass.bus.async_listen(EVENT_STATE_CHANGED, on_state_changed)
    
    threading.Thread(target=sync_areas, args=(hass,)).start()
    threading.Thread(target=sync_devices, args=(hass,)).start()
    threading.Thread(target=sync_states, args=(hass,)).start()
    return True

def sync_devices(hass: HomeAssistant):
    token = hass.data[DOMAIN].get('config', {}).get('token', None)
    if token is None:
        logger.warn("Couldn't sync devices without token")
        return
    
    dr = async_get_dr(hass)
    devices = []
    
    for device in dr.devices.values():
        devices.append({
            "id": device.id,
            "area_id": device.area_id,
            "disabled": True if device.disabled_by is not None else False,
            "hw_version": device.hw_version, 
            "sw_version": device.sw_version,
            "manufacturer": device.manufacturer,
            "model": device.model,
            "name": device.name,
            "config_entries": list(device.config_entries)
        })
    
    # sync devices
    r = requests.put('https://metamall.vatxx.com/api/ha-sync/devices?token=' + token, json=devices)
    if r.status_code != 200:
        logger.warn(r.reason)

def sync_states(hass: HomeAssistant):
    token = hass.data[DOMAIN].get('config', {}).get('token', None)
    if token is None:
        logger.warn("Couldn't sync states without token")
        return
    
    states = []
    for _, state in enumerate(hass.states.async_all()):
        if filter_state(state.entity_id) == True:
            states.append(state.as_dict())

    r = requests.put('https://metamall.vatxx.com/api/ha-sync/states?token=' + token, json=states)
    if r.status_code != 200:
        logger.warn(r.reason)

def sync_areas(hass: HomeAssistant):
    token = hass.data[DOMAIN].get('config', {}).get('token', None)
    if token is None:
        logger.warn("Couldn't sync areas without token")
        return

    ar = async_get_ar(hass)
    areas = list()
    for area in ar.async_list_areas():
        areas.append({
            'id': area.id,
            'name': area.name,
            'normalized_name': area.normalized_name,
            'picture': area.picture
        })
    
    r = requests.put('https://metamall.vatxx.com/api/ha-sync/areas?token=' + token, json=areas)
    if r.status_code != 200:
        logger.warn(r.reason)

def update_state(hass: HomeAssistant, event:Event):
    # logger.warn('state changed started')
    data=event.data
    # logger.warn(data)
    # logger.warn(event)
    entity_id:str = data['entity_id']
    if filter_state(entity_id) != True:
        return

    token = hass.data[DOMAIN].get('config', {}).get('token', None)
    if token is None:
        return

    r = requests.put('https://metamall.vatxx.com/api/ha-sync/state?token=' + token, json=data.get('new_state').as_dict())
    if r.status_code != 200:
        logger.warn(r.reason)

def filter_state(entity_id:str):
    if entity_id.split('.', 2)[0] in ['update', 'person', 'persistent_notification']:
        return False
    return True
    
def on_started(hass: HomeAssistant):
    # sync_areas(hass)
    # sync_devices(hass)
    # sync_states(hass)
    logger.warn('on_started')

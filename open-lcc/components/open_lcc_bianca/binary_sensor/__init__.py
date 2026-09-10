import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import binary_sensor
from esphome.const import CONF_ID, UNIT_CELSIUS, UNIT_SECOND, ICON_RADIOACTIVE, STATE_CLASS_MEASUREMENT, STATE_CLASS_NONE

from .. import open_lcc_bianca_ns, OpenLCCBianca

CONF_OPEN_LCC_BIANCA_ID = "open_lcc_bianca_id"

CONF_BREWING = "brewing"
CONF_FILLING_SERVICE_BOILER = "filling_service_boiler"
CONF_WATER_TANK_LOW = "water_tank_low"
CONF_BREW_BOILER_HEATING = "brew_boiler_heating"
CONF_SERVICE_BOILER_HEATING = "service_boiler_heating"
CONF_OPERATIONAL_READY = "operational_ready"

OpenLCCBiancaSensor = open_lcc_bianca_ns.class_(
    "OpenLCCBiancaBinarySensor",
    cg.Component,
    cg.Parented.template(OpenLCCBianca),
)

CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ID): cv.declare_id(OpenLCCBiancaSensor),
        cv.GenerateID(CONF_OPEN_LCC_BIANCA_ID): cv.use_id(OpenLCCBianca),
        cv.Optional(CONF_BREWING): binary_sensor.binary_sensor_schema(
            icon=ICON_RADIOACTIVE,
        ),
        cv.Optional(CONF_FILLING_SERVICE_BOILER): binary_sensor.binary_sensor_schema(
            icon=ICON_RADIOACTIVE,
        ),
        cv.Optional(CONF_WATER_TANK_LOW): binary_sensor.binary_sensor_schema(
            icon=ICON_RADIOACTIVE,
        ),
        cv.Optional(CONF_BREW_BOILER_HEATING): binary_sensor.binary_sensor_schema(
            icon=ICON_RADIOACTIVE,
        ),
        cv.Optional(CONF_SERVICE_BOILER_HEATING): binary_sensor.binary_sensor_schema(
            icon=ICON_RADIOACTIVE,
        ),
        cv.Optional(CONF_OPERATIONAL_READY): binary_sensor.binary_sensor_schema(
            icon=ICON_RADIOACTIVE,
        ),
    }
)

async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await cg.register_parented(var, config[CONF_OPEN_LCC_BIANCA_ID])

    # [MOD] water_tank_low and operational_ready are created before brewing/
    # filling_service_boiler on purpose: brewing's on_press automation (in openlcc.yaml)
    # references id(water_low_sens) and id(operational_ready_sens) in a lambda, and ESPHome's
    # codegen coroutine suspends this whole to_code() call while resolving each reference. Since
    # a suspended coroutine can't jump ahead to code further down in itself, creating both
    # earlier in this same function is what lets those references ever resolve - otherwise this
    # is a genuine self-inflicted "circular dependency" (this function waiting on something only
    # its own, not-yet-reached code could produce). Any future on_press/on_release/lambda
    # reference from one of these entities to another must respect the same ordering constraint.
    if water_tank_low_config := config.get(CONF_WATER_TANK_LOW):
        sens = await binary_sensor.new_binary_sensor(water_tank_low_config)
        cg.add(var.set_water_tank_low(sens))
    if operational_ready_conf := config.get(CONF_OPERATIONAL_READY):
        sens = await binary_sensor.new_binary_sensor(operational_ready_conf)
        cg.add(var.set_operational_ready(sens))
    if brewing_config := config.get(CONF_BREWING):
        sens = await binary_sensor.new_binary_sensor(brewing_config)
        cg.add(var.set_brewing(sens))
    if filling_config := config.get(CONF_FILLING_SERVICE_BOILER):
        sens = await binary_sensor.new_binary_sensor(filling_config)
        cg.add(var.set_filling_service_boiler(sens))
    if brew_boiler_heating_conf := config.get(CONF_BREW_BOILER_HEATING):
        sens = await binary_sensor.new_binary_sensor(brew_boiler_heating_conf)
        cg.add(var.set_brew_boiler_heating(sens))
    if service_boiler_heating_conf := config.get(CONF_SERVICE_BOILER_HEATING):
        sens = await binary_sensor.new_binary_sensor(service_boiler_heating_conf)
        cg.add(var.set_service_boiler_heating(sens))

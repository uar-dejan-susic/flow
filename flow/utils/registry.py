"""Utility method for registering environments with OpenAI gym."""

import gym
from gym.envs.registration import register

from copy import deepcopy

from flow.core.params import InitialConfig
from flow.core.traffic_lights import TrafficLights


def make_create_env(params, version=0, render=None):
    """Create a parametrized flow environment compatible with OpenAI gym.

    This environment creation method allows for the specification of several
    key parameters when creating any flow environment, including the requested
    environment and scenario classes, and the inputs needed to make these
    classes generalizable to networks of varying sizes and shapes, and well as
    varying forms of control (e.g. AVs, automated traffic lights, etc...).

    This method can also be used to recreate the environment a policy was
    trained on and assess it performance, or a modified form of the previous
    environment may be used to profile the performance of the policy on other
    types of networks.

    Parameters
    ----------
    params : dict
        flow-related parameters, consisting of the following keys:
         - exp_tag: name of the experiment
         - env_name: name of the flow environment the experiment is running on
         - scenario: name of the scenario class the experiment uses
         - sumo: sumo-related parameters (see flow.core.params.SumoParams)
         - env: environment related parameters (see flow.core.params.EnvParams)
         - net: network-related parameters (see flow.core.params.NetParams and
           the scenario's documentation or ADDITIONAL_NET_PARAMS component)
         - veh: vehicles to be placed in the network at the start of a rollout
           (see flow.core.vehicles.Vehicles)
         - initial (optional): parameters affecting the positioning of vehicles
           upon initialization/reset (see flow.core.params.InitialConfig)
         - tls (optional): traffic lights to be introduced to specific nodes
           (see flow.core.traffic_lights.TrafficLights)
    version : int, optional
        environment version number
    render : bool, optional
        specifies whether to use sumo's gui during execution. This overrides
        the render attribute in SumoParams

    Returns
    -------
    function
        method that calls OpenAI gym's register method and make method
    str
        name of the created gym environment
    """
    exp_tag = params["exp_tag"]

    env_name = params["env_name"] + '-v{}'.format(version)

    module = __import__("flow.scenarios", fromlist=[params["scenario"]])
    scenario_class = getattr(module, params["scenario"])

    env_params = params['env']
    net_params = params['net']
    vehicles = params['veh']
    initial_config = params.get('initial', InitialConfig())
    traffic_lights = params.get("tls", TrafficLights())

    def create_env(*_):
        scenario = scenario_class(
            name=exp_tag,
            vehicles=vehicles,
            net_params=net_params,
            initial_config=initial_config,
            traffic_lights=traffic_lights,
        )

        sumo_params = deepcopy(params['sumo'])

        if render is not None:
            sumo_params.render = render

        try:
            register(
                id=env_name,
                entry_point='flow.envs:' + params["env_name"],
                kwargs={
                    "env_params": env_params,
                    "sumo_params": sumo_params,
                    "scenario": scenario
                })
        except Exception:
            pass
        return gym.envs.make(env_name)

    return create_env, env_name

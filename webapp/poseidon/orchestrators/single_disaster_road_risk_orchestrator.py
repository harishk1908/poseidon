"""
This orchestrator class provides an API that allows you to simulate the impact of a disaster upon a road network and
returns city-wise risks for that disaster. The inputs are just the raw parameters of the disaster
"""
from poseidon.infrastructure.road_network_revised import RoadNetwork
from poseidon.infrastructure.bernoulli import BernoulliRoadDamageModel
from poseidon.disasters.earthquakes import GaussianEarthquake
from poseidon.metrics.graph_metrics import is_node_connected_to_hub
from poseidon.simulators.monte_carlo import MonteCarloSimulator


class SingleDisasterRoadRiskOrchestrator:
    def __init__(self):
        self.road_network = RoadNetwork()
        self.road_damage_model = BernoulliRoadDamageModel()
        self.metrics = [is_node_connected_to_hub]

    def get_risk_metric_for_cities(self, inputs):
        if inputs['type'] == 'hurricane':
            disaster = None
        elif inputs['type'] == 'earthquake':
            disaster = GaussianEarthquake(inputs['params'])
        else:
            raise(ValueError("Disaster not supported"))

        simulator = MonteCarloSimulator(disaster, self.road_network, self.road_damage_model, self.metrics)
        metrics = simulator.run(10)
        risks = 100 * (1 - metrics)

        cities = []
        i = 0

        for node, attr in self.road_network.graph_settlement_view.nodes():
            pos = attr['pos']
            cities.append({
                "city": attr['name'],
                "population": int(attr['population']),
                "lat": pos.deg_lat,
                "lng": pos.deg_lon,
                "damage": risks[i]
            })
            i += 1





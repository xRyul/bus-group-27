import numpy as np

class BuildingEnergyMonitoring:
    def __init__(self):

        self.data = {
            "Computer Science": {
                "electric": [120, 118, 123, 119, 121, 117, 122, 124, 300, 116],
                "gas": [5.0, 5.1, 5.2, 5.0, 5.3, 5.2, 5.1, 5.2, 5.0, 15.0],
                "water": [320, 310, 325, 315, 318, 312, 319, 314, 700, 316]
            },
            "Physics": {
                "electric": [135, 133, 137, 134, 132, 136, 138, 140, 350, 134],
                "gas": [6.0, 5.9, 6.1, 6.2, 5.8, 6.0, 6.1, 6.2, 6.0, 20.0],
                "water": [400, 390, 405, 395, 398, 392, 399, 397, 850, 396]
            },
            "Library": {
                "electric": [90, 92, 91, 93, 89, 90, 92, 91, 250, 90],
                "gas": [3.0, 3.1, 3.2, 3.0, 3.3, 3.2, 3.1, 3.2, 10.0, 3.0],
                "water": [210, 220, 215, 212, 218, 214, 216, 213, 600, 217]
            }
        }

    def detect_iqr_anomalies(self, k=1.5):
        anomalies = {}
        for building, utilities in self.data.items():
            anomalies[building] = {}
            for utility, values in utilities.items():
                values_np = np.array(values)
                q1 = np.percentile(values_np, 25)
                q3 = np.percentile(values_np, 75)
                iqr = q3 - q1
                lower_bound = q1 - k * iqr
                upper_bound = q3 + k * iqr
                outlier_indices = np.where((values_np < lower_bound) | (values_np > upper_bound))[0].tolist()
                anomalies[building][utility] = {"values": values,"outliers": outlier_indices}
        return anomalies

class CommunityEngagement:
    ### FR5 Logic ###
    ### FR6 Logic ###
    pass
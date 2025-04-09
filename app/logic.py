import numpy as np

class BuildingEnergyMonitoring:
    def __init__(self):

        # Only 5 working days (Monday to Friday) of simulated data to exclude weekend
        # data to avoid further complexity in data trends.

        self.hourly_data = {
            "Computer Science": {
                "electric": {
                    0: [50, 52, 51, 53, 54],
                    1: [49, 51, 50, 52, 53],
                    2: [48, 47, 49, 50, 12],  # Injected outlier (12)
                    3: [46, 48, 47, 49, 50],
                    4: [45, 44, 46, 47, 48],
                    5: [46, 47, 45, 48, 49],
                    6: [60, 62, 61, 63, 64],
                    7: [80, 82, 81, 83, 84],
                    8: [111, 250, 105, 110, 108],  # Injected outlier (250)
                    9: [120, 125, 122, 123, 124],
                    10: [130, 135, 132, 134, 136],
                    11: [140, 142, 141, 143, 144],
                    12: [150, 148, 149, 151, 152],
                    13: [140, 139, 141, 142, 143],
                    14: [130, 128, 129, 131, 132],
                    15: [120, 118, 119, 121, 122],
                    16: [110, 108, 109, 111, 112],
                    17: [100, 220, 102, 105, 106],  # Injected outlier (220)
                    18: [90, 92, 91, 93, 94],
                    19: [80, 78, 79, 81, 82],
                    20: [70, 68, 69, 71, 72],
                    21: [60, 59, 61, 62, 63],
                    22: [55, 56, 54, 57, 58],
                    23: [53, 52, 54, 55, 56]
                }
            }
        }

        self.daily_data = self.build_daily_data()

    def detect_per_hour_iqr_anomalies(self, k=1.5):
        hourly_data = self.hourly_data["Computer Science"]["electric"]
        outlier_dict = {}

        for hour, values in hourly_data.items():
            values_array = np.array(values)
            q1 = np.percentile(values_array, 25)
            q3 = np.percentile(values_array, 75)
            iqr = q3 - q1
            lower = q1 - k * iqr
            upper = q3 + k * iqr
            for i, val in enumerate(values):
                if val < lower or val > upper:
                    if i not in outlier_dict:
                        outlier_dict[i] = {}
                    outlier_dict[i][hour] = val

        return outlier_dict

    def build_daily_data(self):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        daily = {}
        outlier_dict = self.detect_per_hour_iqr_anomalies()

        for i, day in enumerate(days):
            values = []
            for hour in range(24):
                values.append(self.hourly_data["Computer Science"]["electric"][hour][i])
            outlier_info = (
                {"index": hour, "value": val}
                for hour, val in outlier_dict.get(i, {}).items()
            )
            daily[day] = {
                "data": values,
                "outliers": list(outlier_info)
            }

        return daily

print(BuildingEnergyMonitoring().daily_data)

class CommunityEngagement:
    def __init__(self, user: User):
        self.user = user

    def log_activity(self, activity: SustainableActivity):
        if not self.user or not activity:
            return {'error': 'Invalid user or activity'}, 400

        user_activity = SustainableActivity(
            user_id=self.user.id,
            activity_type=activity.activity_type,
            description=activity.description,
            points_awarded=activity.points_awarded,
            carbon_saved=activity.carbon_saved,
            status='verified'
        )
        db.session.add(user_activity)
        self._update_user_points(activity)
        db.session.commit()

        return {
            'message': f"Activity logged. {activity.points_awarded} points awarded.",
            'total_points': self.user.points.total_points
        }, 200

    def submit_activity(self, activity_type: str, description: str = "", evidence: str = None):
        try:
            activity = SustainableActivity(
                user_id=self.user.id,
                activity_type=activity_type,
                description=description,
                evidence=evidence,
                status='pending'
            )
            db.session.add(activity)
            db.session.commit()
            return {"message": "Activity submitted for review."}, 201
        except Exception as e:
            return {"error": str(e)}, 400

    def _update_user_points(self, activity: SustainableActivity):
        if hasattr(self.user, 'points') and self.user.points:
            self.user.points.total_points += activity.points_awarded
            self.user.points.green_score += activity.carbon_saved
        else:
            self.user.points = UserPoints(
                total_points=activity.points_awarded,
                green_score=activity.carbon_saved,
                user_id=self.user.id
            )
            db.session.add(self.user.points)
     ### FR6 Logic ###
    pass

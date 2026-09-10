from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

class OceanDataProvider(ABC):
    @abstractmethod
    def get_ocean_data(self, lat: float, lon: float) -> Dict[str, Any]:
        pass

class WeatherDataProvider(ABC):
    @abstractmethod
    def get_weather_data(self, lat: float, lon: float) -> Dict[str, Any]:
        pass

class SatelliteDataProvider(ABC):
    @abstractmethod
    def get_satellite_data(self, lat: float, lon: float) -> Dict[str, Any]:
        pass

class AdvisoryDataProvider(ABC):
    @abstractmethod
    def get_advisories(self, region: str) -> List[Dict[str, Any]]:
        pass

"""
Test data factories for ArchaeoVault tests.

This module provides factory classes for generating test data
in a consistent and maintainable way.
"""

import uuid
from datetime import datetime, date
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import factory
from factory import fuzzy
import random

from app.models.artifact import Artifact, ArtifactData
from app.models.civilization import Civilization, CivilizationData
from app.models.excavation import Excavation, ExcavationData

# Base factory class
class BaseFactory(factory.Factory):
    """Base factory with common functionality"""
    
    @classmethod
    def create_batch(cls, size: int, **kwargs) -> List[Any]:
        """Create a batch of instances"""
        return [cls.create(**kwargs) for _ in range(size)]
    
    @classmethod
    def build_batch(cls, size: int, **kwargs) -> List[Any]:
        """Build a batch of instances without saving"""
        return [cls.build(**kwargs) for _ in range(size)]

# Artifact factories
class ArtifactDataFactory(BaseFactory):
    """Factory for ArtifactData"""
    
    class Meta:
        model = ArtifactData
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"Test Artifact {n}")
    material = factory.Iterator(["ceramic", "metal", "stone", "bone", "wood", "textile"])
    period = factory.Iterator([
        "Paleolithic", "Neolithic", "Bronze Age", "Iron Age", 
        "Classical", "Medieval", "Renaissance"
    ])
    condition_score = factory.LazyFunction(lambda: random.randint(1, 10))
    location = factory.LazyFunction(lambda: {
        "lat": round(random.uniform(-90, 90), 6),
        "lon": round(random.uniform(-180, 180), 6),
        "site_name": f"Test Site {random.randint(1, 100)}"
    })
    discovery_date = factory.LazyFunction(lambda: date.today())
    image_urls = factory.LazyFunction(lambda: [f"test_image_{random.randint(1, 100)}.jpg"])
    analysis_data = factory.LazyFunction(lambda: {
        "confidence": round(random.uniform(0.5, 1.0), 2),
        "description": f"Test description for artifact {random.randint(1, 100)}",
        "civilization": random.choice(["Egyptian", "Greek", "Roman", "Chinese", "Maya"]),
        "dating_estimate": f"{random.randint(1000, 3000)} BCE"
    })
    metadata = factory.LazyFunction(lambda: {
        "color": random.choice(["red", "black", "brown", "white", "gray"]),
        "decoration": random.choice(["geometric", "figurative", "none", "text"]),
        "size": f"{random.randint(5, 50)}cm",
        "weight": f"{random.randint(100, 5000)}g"
    })
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

class ArtifactFactory(BaseFactory):
    """Factory for Artifact model"""
    
    class Meta:
        model = Artifact
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    project_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"Artifact {n}")
    material = factory.Iterator(["ceramic", "metal", "stone", "bone", "wood", "textile"])
    period = factory.Iterator([
        "Paleolithic", "Neolithic", "Bronze Age", "Iron Age", 
        "Classical", "Medieval", "Renaissance"
    ])
    location = factory.LazyFunction(lambda: {
        "lat": round(random.uniform(-90, 90), 6),
        "lon": round(random.uniform(-180, 180), 6)
    })
    discovery_date = factory.LazyFunction(lambda: date.today())
    condition_score = factory.LazyFunction(lambda: random.randint(1, 10))
    image_urls = factory.LazyFunction(lambda: [f"image_{random.randint(1, 100)}.jpg"])
    analysis_data = factory.LazyFunction(lambda: {
        "confidence": round(random.uniform(0.5, 1.0), 2),
        "description": f"Analysis for artifact {random.randint(1, 100)}"
    })
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

# Civilization factories
class CivilizationDataFactory(BaseFactory):
    """Factory for CivilizationData"""
    
    class Meta:
        model = CivilizationData
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Iterator([
        "Ancient Egypt", "Ancient Greece", "Roman Empire", "Han Dynasty",
        "Maya Civilization", "Inca Empire", "Aztec Empire", "Sumerian",
        "Babylonian", "Assyrian", "Persian", "Byzantine"
    ])
    time_period = factory.LazyFunction(lambda: (
        random.randint(1000, 3000),
        random.randint(500, 2000)
    ))
    region = factory.LazyFunction(lambda: {
        "name": random.choice(["Mediterranean", "Mesopotamia", "Mesoamerica", "Andes", "Nile Valley"]),
        "coordinates": [
            [round(random.uniform(-90, 90), 6), round(random.uniform(-180, 180), 6)]
            for _ in range(random.randint(3, 8))
        ]
    })
    achievements = factory.LazyFunction(lambda: random.sample([
        "Writing System", "Architecture", "Mathematics", "Astronomy", "Medicine",
        "Engineering", "Art", "Philosophy", "Law", "Government", "Trade",
        "Agriculture", "Metallurgy", "Pottery", "Textiles"
    ], random.randint(3, 8)))
    notable_artifacts = factory.LazyFunction(lambda: [
        f"Artifact {i}" for i in range(random.randint(2, 10))
    ])
    cultural_data = factory.LazyFunction(lambda: {
        "language": random.choice(["Hieroglyphic", "Cuneiform", "Greek", "Latin", "Chinese", "Mayan"]),
        "religion": random.choice(["Polytheistic", "Monotheistic", "Animistic", "Shamanistic"]),
        "government": random.choice(["Monarchy", "Republic", "Empire", "City-State", "Theocracy"]),
        "economy": random.choice(["Agricultural", "Trade-based", "Mercantile", "Feudal"])
    })
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

class CivilizationFactory(BaseFactory):
    """Factory for Civilization model"""
    
    class Meta:
        model = Civilization
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Iterator([
        "Ancient Egypt", "Ancient Greece", "Roman Empire", "Han Dynasty",
        "Maya Civilization", "Inca Empire", "Aztec Empire", "Sumerian"
    ])
    time_period = factory.LazyFunction(lambda: (
        random.randint(1000, 3000),
        random.randint(500, 2000)
    ))
    region = factory.LazyFunction(lambda: [
        [round(random.uniform(-90, 90), 6), round(random.uniform(-180, 180), 6)]
        for _ in range(random.randint(3, 8))
    ])
    achievements = factory.LazyFunction(lambda: random.sample([
        "Writing System", "Architecture", "Mathematics", "Astronomy", "Medicine"
    ], random.randint(3, 5)))
    notable_artifacts = factory.LazyFunction(lambda: [
        f"Artifact {i}" for i in range(random.randint(2, 5))
    ])
    cultural_data = factory.LazyFunction(lambda: {
        "language": random.choice(["Hieroglyphic", "Cuneiform", "Greek", "Latin"]),
        "religion": random.choice(["Polytheistic", "Monotheistic", "Animistic"])
    })
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

# Excavation factories
class ExcavationDataFactory(BaseFactory):
    """Factory for ExcavationData"""
    
    class Meta:
        model = ExcavationData
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    project_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    site_name = factory.Sequence(lambda n: f"Excavation Site {n}")
    location = factory.LazyFunction(lambda: {
        "lat": round(random.uniform(-90, 90), 6),
        "lon": round(random.uniform(-180, 180), 6)
    })
    grid_size = factory.LazyFunction(lambda: {
        "width": random.randint(5, 20),
        "height": random.randint(5, 20)
    })
    layers = factory.LazyFunction(lambda: [
        {
            "depth": round(random.uniform(0.1, 2.0), 2),
            "soil_type": random.choice(["topsoil", "clay", "sand", "gravel", "loam"]),
            "color": random.choice(["brown", "red", "yellow", "gray", "black"]),
            "artifacts": [f"Artifact {i}" for i in range(random.randint(0, 5))],
            "inclusions": random.choice(["stones", "shells", "charcoal", "none"])
        }
        for _ in range(random.randint(2, 8))
    ])
    findings = factory.LazyFunction(lambda: [
        f"Finding {i}" for i in range(random.randint(1, 10))
    ])
    status = factory.Iterator(["planned", "in_progress", "completed", "suspended"])
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

class ExcavationFactory(BaseFactory):
    """Factory for Excavation model"""
    
    class Meta:
        model = Excavation
    
    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    project_id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    site_name = factory.Sequence(lambda n: f"Site {n}")
    location = factory.LazyFunction(lambda: {
        "lat": round(random.uniform(-90, 90), 6),
        "lon": round(random.uniform(-180, 180), 6)
    })
    grid_size = factory.LazyFunction(lambda: {
        "width": random.randint(5, 20),
        "height": random.randint(5, 20)
    })
    layers = factory.LazyFunction(lambda: [
        {
            "depth": round(random.uniform(0.1, 2.0), 2),
            "soil_type": random.choice(["topsoil", "clay", "sand", "gravel"]),
            "artifacts": [f"Artifact {i}" for i in range(random.randint(0, 3))]
        }
        for _ in range(random.randint(2, 5))
    ])
    findings = factory.LazyFunction(lambda: [
        f"Finding {i}" for i in range(random.randint(1, 5))
    ])
    status = factory.Iterator(["planned", "in_progress", "completed"])
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)

# Specialized factories for specific test scenarios
class CeramicArtifactFactory(ArtifactDataFactory):
    """Factory for ceramic artifacts specifically"""
    material = "ceramic"
    period = factory.Iterator(["Bronze Age", "Iron Age", "Classical"])
    metadata = factory.LazyFunction(lambda: {
        "color": random.choice(["red", "black", "brown"]),
        "decoration": random.choice(["geometric", "figurative", "none"]),
        "firing_temperature": random.choice(["low", "medium", "high"]),
        "clay_type": random.choice(["earthenware", "stoneware", "porcelain"])
    })

class MetalArtifactFactory(ArtifactDataFactory):
    """Factory for metal artifacts specifically"""
    material = "metal"
    period = factory.Iterator(["Bronze Age", "Iron Age", "Classical"])
    metadata = factory.LazyFunction(lambda: {
        "metal_type": random.choice(["bronze", "iron", "copper", "gold", "silver"]),
        "alloy_composition": random.choice(["pure", "alloyed", "mixed"]),
        "manufacturing_technique": random.choice(["casting", "forging", "beating"]),
        "corrosion_level": random.choice(["none", "light", "moderate", "heavy"])
    })

class StoneArtifactFactory(ArtifactDataFactory):
    """Factory for stone artifacts specifically"""
    material = "stone"
    period = factory.Iterator(["Paleolithic", "Neolithic", "Bronze Age"])
    metadata = factory.LazyFunction(lambda: {
        "stone_type": random.choice(["flint", "obsidian", "granite", "limestone", "marble"]),
        "tool_type": random.choice(["handaxe", "scraper", "blade", "point", "adze"]),
        "manufacturing_technique": random.choice(["knapping", "pecking", "grinding"]),
        "use_wear": random.choice(["none", "light", "moderate", "heavy"])
    })

class EgyptianCivilizationFactory(CivilizationDataFactory):
    """Factory for Egyptian civilization specifically"""
    name = "Ancient Egypt"
    time_period = (3100, 30)
    region = {
        "name": "Nile Valley",
        "coordinates": [
            [31.2001, 29.9187], [31.2001, 32.3219],
            [24.0889, 32.3219], [24.0889, 29.9187]
        ]
    }
    achievements = ["Hieroglyphic Writing", "Pyramid Construction", "Mummification", "Mathematics", "Medicine"]
    cultural_data = {
        "language": "Hieroglyphic",
        "religion": "Polytheistic",
        "government": "Monarchy",
        "economy": "Agricultural"
    }

class GreekCivilizationFactory(CivilizationDataFactory):
    """Factory for Greek civilization specifically"""
    name = "Ancient Greece"
    time_period = (800, 146)
    region = {
        "name": "Mediterranean",
        "coordinates": [
            [39.0742, 20.4573], [39.0742, 28.2336],
            [35.0000, 28.2336], [35.0000, 20.4573]
        ]
    }
    achievements = ["Democracy", "Philosophy", "Theater", "Olympic Games", "Mathematics"]
    cultural_data = {
        "language": "Greek",
        "religion": "Polytheistic",
        "government": "City-State",
        "economy": "Trade-based"
    }

# Performance test factories
class LargeDatasetFactory:
    """Factory for generating large datasets for performance testing"""
    
    @staticmethod
    def create_artifacts(count: int) -> List[ArtifactData]:
        """Create large number of artifacts"""
        return ArtifactDataFactory.create_batch(count)
    
    @staticmethod
    def create_civilizations(count: int) -> List[CivilizationData]:
        """Create large number of civilizations"""
        return CivilizationDataFactory.create_batch(count)
    
    @staticmethod
    def create_excavations(count: int) -> List[ExcavationData]:
        """Create large number of excavations"""
        return ExcavationDataFactory.create_batch(count)

# Security test factories
class MaliciousDataFactory:
    """Factory for generating malicious test data"""
    
    @staticmethod
    def sql_injection_payloads() -> List[str]:
        """Generate SQL injection test payloads"""
        return [
            "'; DROP TABLE artifacts; --",
            "1' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users --",
            "'; INSERT INTO artifacts VALUES ('hack', 'hack'); --"
        ]
    
    @staticmethod
    def xss_payloads() -> List[str]:
        """Generate XSS test payloads"""
        return [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "<svg onload=alert('XSS')>",
            "<iframe src=javascript:alert('XSS')>"
        ]
    
    @staticmethod
    def path_traversal_payloads() -> List[str]:
        """Generate path traversal test payloads"""
        return [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "..%2F..%2F..%2Fetc%2Fpasswd",
            "..%252F..%252F..%252Fetc%252Fpasswd"
        ]

# Test data utilities
class TestDataUtils:
    """Utilities for test data manipulation"""
    
    @staticmethod
    def create_artifact_with_specific_material(material: str) -> ArtifactData:
        """Create artifact with specific material"""
        return ArtifactDataFactory.create(material=material)
    
    @staticmethod
    def create_civilization_in_period(start_year: int, end_year: int) -> CivilizationData:
        """Create civilization in specific time period"""
        return CivilizationDataFactory.create(time_period=(start_year, end_year))
    
    @staticmethod
    def create_excavation_with_status(status: str) -> ExcavationData:
        """Create excavation with specific status"""
        return ExcavationDataFactory.create(status=status)
    
    @staticmethod
    def create_artifacts_by_period(period: str, count: int) -> List[ArtifactData]:
        """Create multiple artifacts from specific period"""
        return ArtifactDataFactory.create_batch(count, period=period)
    
    @staticmethod
    def create_artifacts_by_material(material: str, count: int) -> List[ArtifactData]:
        """Create multiple artifacts of specific material"""
        return ArtifactDataFactory.create_batch(count, material=material)


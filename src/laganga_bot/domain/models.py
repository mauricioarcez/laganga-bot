from dataclasses import dataclass
from typing import Optional

@dataclass
class Deal:
    id: int
    name: str
    current_price: float
    original_price: float
    discount_percent: int
    source: str
    details: Optional[str]
    image_url: str
    slug: str
    
    @property
    def url(self) -> str:
        return f"https://lagangaofertas.com/flash-deals/{self.slug}"

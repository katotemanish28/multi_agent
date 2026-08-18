from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date
 
 
class TripIntent(BaseModel):
    origin: str = Field(description="IATA city/airport code of origin, e.g. BOM")
    destination: str = Field(description="IATA city/airport code of destination, e.g. DEL")
    depart_date: date
    return_date: Optional[date] = None
    adults: int = 1
    budget_inr: Optional[int] = None
    preferences: List[str] = Field(default_factory=list, description="e.g. ['budget', 'beach', 'window seat']")
 
 
class FlightOffer(BaseModel):
    offer_id: str
    airline: str
    price_inr: float
    depart_time: str
    arrive_time: str
    duration: str
    stops: int
 
 
class HotelOffer(BaseModel):
    offer_id: str
    name: str
    price_per_night_inr: float
    rating: Optional[float] = None
    address: str
 
 
class ItineraryDay(BaseModel):
    day_number: int
    theme: str
    activities: List[str]
 
 
class TripItinerary(BaseModel):
    destination: str
    days: List[ItineraryDay]
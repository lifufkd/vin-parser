from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime


class FindVehicle(BaseModel):
    use_vin_number: Optional[bool] = Field(None)
    use_plate_number: Optional[bool] = Field(None)

    @model_validator(mode="after")
    def exactly_one_required(self) -> "FindVehicle":
        if self.use_vin_number and self.use_plate_number:
            raise ValueError("Нельзя использовать одновременно VIN и госномер")
        if not (self.use_vin_number or self.use_plate_number):
            raise ValueError("Необходимо указать либо VIN, либо госномер")
        return self


class Vehicle(BaseModel):
    vin_number: Optional[str] = Field(None)
    plate_number: Optional[str] = Field(None)
    date: Optional[datetime] = Field()


class VehicleInfo(BaseModel):
    policy_series: Optional[str] = Field(None)
    policy_number: Optional[str] = Field(None)
    osago_status: Optional[str] = Field(None)
    usage_period: Optional[str] = Field(None)
    vehicle_model: Optional[str] = Field(None)
    vin: Optional[str]
    license_plate: Optional[str]
    insurance_company: Optional[str] = Field(None)
    belarus_extension: Optional[str] = Field(None)
    data_date: Optional[str] = Field(None)

from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import date


class FindVehicle(BaseModel):
    use_vin_number: bool
    use_plate_number: bool

    @model_validator(mode="after")
    def exactly_one_required(self) -> "FindVehicle":
        if self.use_vin_number and self.use_plate_number:
            raise ValueError("Нельзя использовать одновременно VIN и госномер")
        if not (self.use_vin_number or self.use_plate_number):
            raise ValueError("Необходимо указать либо VIN, либо госномер")
        return self


class Vehicle(BaseModel):
    vin_number: Optional[str] = Field(None, alias='vin')
    plate_number: Optional[str] = Field(None, alias='number')
    date: Optional[date] = Field(alias='datetime')


class VehicleInfo(BaseModel):
    policy_series: Optional[str] = Field(None, alias='policySeries')
    policy_number: Optional[str] = Field(None, alias='policyNumber')
    osago_status: Optional[str] = Field(None, alias='osagoStatus')
    usage_period: Optional[str] = Field(None, alias='usagePeriod')
    vehicle_model: Optional[str] = Field(None, alias='vehicleModel')
    vin: Optional[str]
    license_plate: Optional[str]
    insurance_company: Optional[str] = Field(None, alias='insuranceCompany')
    belarus_extension: Optional[str] = Field(None, alias='belarusExtension')
    data_date: Optional[str] = Field(None, alias='dataDate')

from pydantic import BaseModel


class SellerDashboardResponse(BaseModel):
    total_listings: int
    active_listings: int
    pending_approvals: int
    sold_cars: int
    inquiries: int

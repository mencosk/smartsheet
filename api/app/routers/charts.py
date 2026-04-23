from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.routers.upload import get_dataframe
from app.services.chart_data_builder import build_chart_data

router = APIRouter()


class ChartDataRequest(BaseModel):
    session_id: str
    chart_type: str
    parameters: dict


@router.post("/chart-data")
async def get_chart_data(request: ChartDataRequest):
    df = get_dataframe(request.session_id)

    try:
        data = build_chart_data(df, request.chart_type, request.parameters)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Column not found: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error building chart data: {str(e)}")

    return {"data": data}

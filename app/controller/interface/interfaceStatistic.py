from fastapi import APIRouter
from fastapi.params import Depends

from app.controller import Authentication
from app.model.base import User
from app.response import Response

router = APIRouter(prefix="/interface/statistic", tags=['自动化接口步骤'])


@router.get('/api/added')
async def get_interface_added_statistic(_: User = Depends(Authentication())):


    return Response.success()

"""REST routes for relativity feature."""
import logging
from fastapi import APIRouter
from core.utils import load_instruction
from sympy_mcp.session import SymPySessionManager
from sympy_mcp.features.relativity.models import (
    CreatePredefinedMetricRequest,
    SearchPredefinedMetricsRequest,
    CalculateTensorRequest,
    CreateCustomMetricRequest,
    PrintLatexTensorRequest,
    RelativityResponse,
)

logger = logging.getLogger(__name__)


def create_router(session_manager: SymPySessionManager) -> APIRouter:
    router = APIRouter(prefix="/relativity", tags=["Relativity"])

    @router.post(
        "/metric/predefined",
        response_model=RelativityResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def create_predefined_metric(request: CreatePredefinedMetricRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.create_predefined_metric(request.metric_name)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return RelativityResponse(success=True, result=resolved, result_key=raw)
            return RelativityResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"create_predefined_metric error: {e}")
            return RelativityResponse(success=False, error=str(e))

    @router.post(
        "/metric/search",
        response_model=RelativityResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def search_predefined_metrics(request: SearchPredefinedMetricsRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            result = state.search_predefined_metrics(request.query)
            return RelativityResponse(success=True, result=result)
        except Exception as e:
            logger.error(f"search_predefined_metrics error: {e}")
            return RelativityResponse(success=False, error=str(e))

    @router.post(
        "/tensor/calculate",
        response_model=RelativityResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def calculate_tensor(request: CalculateTensorRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.calculate_tensor(
                request.metric_key,
                request.tensor_type,
                simplify_result=request.simplify,
            )
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return RelativityResponse(success=True, result=resolved, result_key=raw)
            return RelativityResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"calculate_tensor error: {e}")
            return RelativityResponse(success=False, error=str(e))

    @router.post(
        "/metric/custom",
        response_model=RelativityResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def create_custom_metric(request: CreateCustomMetricRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.create_custom_metric(
                request.components,
                request.symbols,
                request.config,
            )
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return RelativityResponse(success=True, result=resolved, result_key=raw)
            return RelativityResponse(success=False, error=raw)
        except Exception as e:
            logger.error(f"create_custom_metric error: {e}")
            return RelativityResponse(success=False, error=str(e))

    @router.post(
        "/tensor/latex",
        response_model=RelativityResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def print_latex_tensor(request: PrintLatexTensorRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            result = state.print_latex_tensor(request.tensor_key)
            return RelativityResponse(success=True, result=result)
        except Exception as e:
            logger.error(f"print_latex_tensor error: {e}")
            return RelativityResponse(success=False, error=str(e))

    return router

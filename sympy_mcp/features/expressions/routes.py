"""REST routes for expressions feature."""
import logging
from fastapi import APIRouter
from core.utils import load_instruction
from sympy_mcp.session import SymPySessionManager
from sympy_mcp.features.expressions.models import (
    IntroduceExpressionRequest, IntroduceEquationRequest,
    PrintLatexRequest, SubstituteExpressionRequest,
    FactorRequest, ExpandRequest, CollectRequest, ApartRequest, EvalfRequest,
    ExpressionResponse
)

logger = logging.getLogger(__name__)


def create_router(session_manager: SymPySessionManager) -> APIRouter:
    router = APIRouter(prefix="/expressions", tags=["Expressions"])

    @router.post(
        "/introduce",
        response_model=ExpressionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def introduce_expression(request: IntroduceExpressionRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.introduce_expression(request.expr_str, request.canonicalize, request.name)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return ExpressionResponse(success=True, result=resolved, result_key=raw)
            return ExpressionResponse(success=False, error=raw)
        except Exception as e:
            return ExpressionResponse(success=False, error=str(e))

    @router.post(
        "/introduce_equation",
        response_model=ExpressionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def introduce_equation(request: IntroduceEquationRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.introduce_equation(request.lhs_str, request.rhs_str)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return ExpressionResponse(success=True, result=resolved, result_key=raw)
            return ExpressionResponse(success=False, error=raw)
        except Exception as e:
            return ExpressionResponse(success=False, error=str(e))

    @router.post(
        "/latex",
        response_model=ExpressionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def print_latex(request: PrintLatexRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            result = state.print_latex_expression(request.expr_key)
            return ExpressionResponse(success=True, result=result)
        except Exception as e:
            return ExpressionResponse(success=False, error=str(e))

    @router.post(
        "/substitute",
        response_model=ExpressionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def substitute(request: SubstituteExpressionRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.substitute_expression(request.expr_key, request.var_name, request.replacement_expr_key)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return ExpressionResponse(success=True, result=resolved, result_key=raw)
            return ExpressionResponse(success=False, error=raw)
        except Exception as e:
            return ExpressionResponse(success=False, error=str(e))

    @router.post(
        "/factor",
        response_model=ExpressionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def factor(request: FactorRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.factor_expression(request.expr_key)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return ExpressionResponse(success=True, result=resolved, result_key=raw)
            return ExpressionResponse(success=False, error=raw)
        except Exception as e:
            return ExpressionResponse(success=False, error=str(e))

    @router.post(
        "/expand",
        response_model=ExpressionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def expand(request: ExpandRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.expand_expression(request.expr_key)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return ExpressionResponse(success=True, result=resolved, result_key=raw)
            return ExpressionResponse(success=False, error=raw)
        except Exception as e:
            return ExpressionResponse(success=False, error=str(e))

    @router.post(
        "/collect",
        response_model=ExpressionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def collect(request: CollectRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.collect_expression(request.expr_key, request.var_name)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return ExpressionResponse(success=True, result=resolved, result_key=raw)
            return ExpressionResponse(success=False, error=raw)
        except Exception as e:
            return ExpressionResponse(success=False, error=str(e))

    @router.post(
        "/apart",
        response_model=ExpressionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def apart(request: ApartRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.apart_expression(request.expr_key, request.var_name)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return ExpressionResponse(success=True, result=resolved, result_key=raw)
            return ExpressionResponse(success=False, error=raw)
        except Exception as e:
            return ExpressionResponse(success=False, error=str(e))

    @router.post(
        "/evalf",
        response_model=ExpressionResponse,
        description=load_instruction("instructions.md", __file__),
    )
    async def evalf(request: EvalfRequest):
        state = session_manager.get_or_create_sync(request.session_id)
        try:
            raw = state.evalf_expression(request.expr_key, request.n)
            resolved = state.resolve_result(raw)
            if raw != resolved:
                return ExpressionResponse(success=True, result=resolved, result_key=raw)
            return ExpressionResponse(success=False, error=raw)
        except Exception as e:
            return ExpressionResponse(success=False, error=str(e))

    return router

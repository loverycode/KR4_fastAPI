from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from models import ErrorResponse

class CustomExceptionA(HTTPException):
    def __init__(self, detail: str = "Условие не выполнено"):
        super().__init__(status_code=400, detail=detail)

class CustomExceptionB(HTTPException):
    def __init__(self, detail:str="Ресурс не найден"):
        super().__init__(status_code=404, detail=detail)

def register_exception_handlers(app):
    @app.exception_handler(CustomExceptionA)
    async def handle_custom_a(request: Request, exc: CustomExceptionA):
        return JSONResponse(
            status_code=exc.status_code, 
            content=ErrorResponse(
                status_code=exc.status_code,
                error_type="CustomExceptionA",
                message=exc.detail,
                details={"condition":"специфичное условие не выполнено"}
            ).model_dump()
        )

    @app.exception_handler(CustomExceptionB)
    async def handle_custom_b(request: Request, exc: CustomExceptionB):
        return JSONResponse(
            status_code=exc.status_code, 
            content=ErrorResponse(
                status_code=exc.status_code,
                error_type="CustomExceptionB",
                message=exc.detail,
                details={"resource":"запрашиваемый ресурс"}
            ).model_dump()
        )
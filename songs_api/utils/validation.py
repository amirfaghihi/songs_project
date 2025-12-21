from __future__ import annotations

from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import jsonify, request
from pydantic import BaseModel, ValidationError

from songs_api.constants import HTTPStatusCode


def validate_request[T: BaseModel, F: Callable[..., Any]](model: type[T]) -> Callable[[F], F]:
    """Validate request JSON body against Pydantic model."""
    def decorator(f: F) -> F:
        @wraps(f)
        def wrapped(*args: Any, **kwargs: Any):
            try:
                json_data = request.get_json()
                if json_data is None:
                    return jsonify({"error": "Request body must be JSON"}), HTTPStatusCode.BAD_REQUEST
                validated_data = model(**json_data)
            except ValidationError as e:
                return jsonify({"errors": e.errors()}), HTTPStatusCode.UNPROCESSABLE_ENTITY
            except Exception as e:
                return jsonify({"error": str(e)}), HTTPStatusCode.BAD_REQUEST

            return f(validated_data, *args, **kwargs)

        return wrapped  # type: ignore[return-value]

    return decorator


def validate_query[T: BaseModel, F: Callable[..., Any]](model: type[T]) -> Callable[[F], F]:
    """Validate query parameters against Pydantic model."""
    def decorator(f: F) -> F:
        @wraps(f)
        def wrapped(*args: Any, **kwargs: Any):
            try:
                query_data = request.args.to_dict()
                validated_data = model(**query_data)
            except ValidationError as e:
                return jsonify({"errors": e.errors()}), HTTPStatusCode.UNPROCESSABLE_ENTITY
            except Exception as e:
                return jsonify({"error": str(e)}), HTTPStatusCode.BAD_REQUEST

            return f(validated_data, *args, **kwargs)

        return wrapped  # type: ignore[return-value]

    return decorator

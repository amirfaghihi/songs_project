from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Type, TypeVar

from flask import jsonify, request
from pydantic import BaseModel, ValidationError


F = TypeVar("F", bound=Callable[..., Any])
T = TypeVar("T", bound=BaseModel)


def validate_request(model: Type[T]) -> Callable[[F], F]:
    """
    Decorator to automatically validate request JSON against a Pydantic model.
    
    Usage:
        @validate_request(MyRequestModel)
        def my_endpoint(data: MyRequestModel):
            # data is already validated
    """

    def decorator(f: F) -> F:
        @wraps(f)
        def wrapped(*args: Any, **kwargs: Any):
            try:
                json_data = request.get_json()
                if json_data is None:
                    return jsonify({"error": "Request body must be JSON"}), 400
                validated_data = model(**json_data)
            except ValidationError as e:
                return jsonify({"errors": e.errors()}), 422
            except Exception as e:
                return jsonify({"error": str(e)}), 400

            return f(validated_data, *args, **kwargs)

        return wrapped  # type: ignore[return-value]

    return decorator


def validate_query(model: Type[T]) -> Callable[[F], F]:
    """
    Decorator to automatically validate query parameters against a Pydantic model.
    
    Usage:
        @validate_query(MyQueryModel)
        def my_endpoint(query: MyQueryModel):
            # query is already validated
    """

    def decorator(f: F) -> F:
        @wraps(f)
        def wrapped(*args: Any, **kwargs: Any):
            try:
                query_data = request.args.to_dict()
                validated_data = model(**query_data)
            except ValidationError as e:
                return jsonify({"errors": e.errors()}), 422
            except Exception as e:
                return jsonify({"error": str(e)}), 400

            return f(validated_data, *args, **kwargs)

        return wrapped  # type: ignore[return-value]

    return decorator




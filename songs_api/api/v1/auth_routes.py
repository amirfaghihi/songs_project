from __future__ import annotations

from flask import Blueprint, jsonify

from songs_api.constants import TokenType
from songs_api.schemas import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
from songs_api.services import AuthService
from songs_api.utils.dependencies import inject
from songs_api.utils.validation import validate_request


def register_auth_routes(bp: Blueprint) -> None:
    @bp.route("/auth/login", methods=["POST"])
    @validate_request(LoginRequest)
    @inject(AuthService)
    def login(data: LoginRequest, auth_service: AuthService):
        """
        Login to obtain JWT access token
        ---
        tags:
          - Authentication
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                username:
                  type: string
                  example: admin
                password:
                  type: string
                  example: admin
        responses:
          200:
            description: Successfully authenticated
            schema:
              type: object
              properties:
                access_token:
                  type: string
                token_type:
                  type: string
                  example: bearer
          401:
            description: Invalid credentials
          422:
            description: Validation error
        """
        access_token = auth_service.login(username=data.username, password=data.password)

        response = LoginResponse(access_token=access_token, token_type=TokenType.BEARER.value)
        return jsonify(response.model_dump())

    @bp.route("/auth/register", methods=["POST"])
    @validate_request(RegisterRequest)
    @inject(AuthService)
    def register(data: RegisterRequest, auth_service: AuthService):
        """
        Register a new user
        ---
        tags:
          - Authentication
        parameters:
          - in: body
            name: body
            required: true
            schema:
              type: object
              properties:
                username:
                  type: string
                  minLength: 3
                  maxLength: 50
                  example: testuser
                password:
                  type: string
                  minLength: 6
                  example: password123
        responses:
          201:
            description: User registered successfully
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: User registered successfully
                username:
                  type: string
                  example: testuser
          409:
            description: Username already exists
          422:
            description: Validation error
        """
        result = auth_service.register(username=data.username, password=data.password)
        response = RegisterResponse(**result)
        return jsonify(response.model_dump()), 201

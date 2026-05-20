@router.post("/login")
def login(
    data: LoginRequest,
    response: Response,
    session: Session = Depends(get_session)
):
    token = login_user(
        email=data.email,
        password=data.password,
        session=session
    )

    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=1800
    )

    return {
        "message": "Login exitoso"
    }
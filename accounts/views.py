from django.contrib.auth import logout
from django.http import HttpResponse
from django.shortcuts import redirect


def login_view(request):
    return HttpResponse("""
        <h1>Login</h1>
        <p>Login feature is being completed.</p>
        <a href="/">Back to Home</a>
    """)


def register_view(request):
    return HttpResponse("""
        <h1>Register</h1>
        <p>Registration feature is being completed.</p>
        <a href="/">Back to Home</a>
    """)


def dashboard(request):
    return HttpResponse("""
        <h1>Customer Dashboard</h1>
        <p>Customer account feature is being completed.</p>
        <a href="/">Back to Home</a>
    """)


def logout_view(request):
    logout(request)
    return redirect('/')
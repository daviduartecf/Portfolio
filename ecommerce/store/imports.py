from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData, guestOrder, getData
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.conf import settings
import requests
import base64
from django.http import HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.core.mail import send_mail
from django.shortcuts import render,redirect,HttpResponse
from todolist import urls
#from base.models import UserProfile
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.shortcuts import render, redirect
from base.models import Task

from django.shortcuts import render, redirect
from .models import Task

from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_protect
from django.utils.decorators import method_decorator
from django.views import View
from django.http import JsonResponse
from .models import Task
from base import models
from .models import Tambola
import random




def homepage(request):
    error_msg = ""
    if request.method== "POST":
        user_1=request.POST.get('user')
        password_1=request.POST.get('pass')
        #print(user_1)
        user= authenticate(request, username=user_1, password=password_1)
        #print(user123)
        if user is not None:
            # The credentials are valid, log in the user
            #print(123)
            login(request, user)
            messages.success(request, 'Login successful!')
            fname=user.first_name
            #data_to_pass = { 'user123':user123,'fname' : fname,}
            
            return redirect('/todopage',{'fname':fname})
        else:
            # The credentials are not valid, display an error message
            #print(456)
            #error_message ="Invalid User Name or Password"
          
            #print(error_message)
            return redirect('/')

    return render(request, 'home_page.html')



def sign_up(request):
    if request.method == 'POST':
        username = request.POST.get('u_name','')
        email = request.POST.get('e_mail','')
        password = request.POST.get('pass1','')
        confirm_password = request.POST.get('pass2','')
        first_name = request.POST.get('f_name','')
        last_name = request.POST.get('l_name','')
        print(password)
        print(confirm_password)

        # Check if the username already exists
        if User.objects.filter(username=username).exists():
            error_message1 = "Username already exists"
            return redirect('/signup?error_message1=' + error_message1)

        # Check if passwords match
        if password != confirm_password:
            error_message2 = "Passwords do not match"
            return redirect('/signup?error_message2=' + error_message2)

        # Create a new user if the username doesn't exist and passwords match
        user = User.objects.create_user(username=username, email=email, password=password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        account_msg="Account Created Sucssefully"

        return redirect('/?account_msg='+account_msg)

    return render(request, "signup_page.html")






def logout_user(request):
    request.session.clear()

    # Redirect to 'homepage'
    return redirect('homepage')




@login_required
def todo_you(request):
    if request.method=='POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        priority = int(request.POST.get('priority'))
        due_date = request.POST.get('due_date')

        task = Task.objects.create(
            name=name,
            description=description,
            priority=priority,
            due_date=due_date,
            user=request.user
        )
        read= models.Task.objects.filter(user=request.user).order_by('-due_date', 'priority') #request.user is used to get details of current user.
        return redirect('/todopage',{'read':read})
    all_tasks=Task.objects.filter(user=request.user)
    completed_tasks = all_tasks.filter(completed=True)
    pending_tasks = all_tasks.filter(completed=False)
    return render(request,'todo.html',{'completed':completed_tasks,'pending':pending_tasks})

@login_required
def edit_todo(request, id):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        priority = int(request.POST.get('priority'))
        due_date = request.POST.get('due_date')

        taskss = models.Task.objects.get(id=id)
        taskss.name = name
        taskss.description = description
        taskss.priority=priority
        taskss.due_date=due_date
        taskss.save()

        return redirect('/todopage?id={}'.format(id))

    taskss = models.Task.objects.get(id=id)
    return render(request, 'edit_todo.html', {'taskss': taskss})
@login_required
def completed(request,id):
    task = models.Task.objects.get(id=id)
    # Assuming you have a 'completed' field in your model, set it to True.
    task.completed = True
    task.save()
    return redirect('/todopage')

def deleted(request,id):
    task=models.Task.objects.get(id=id)
    task.delete()
    return redirect('/todopage')


def tambola(request):
    tambola_obj = Tambola.objects.last()

    if request.method == 'POST':
        min_range = int(request.POST.get('min_range', 1))
        max_range = int(request.POST.get('max_range', 100))

        if tambola_obj:
            tambola_obj.min_range = min_range
            tambola_obj.max_range = max_range
            tambola_obj.generated_numbers = ''
            tambola_obj.save()
        else:
            tambola_obj = Tambola.objects.create(min_range=min_range, max_range=max_range, generated_numbers='')

    generated_numbers = list(map(int, tambola_obj.generated_numbers.split(','))) if tambola_obj and tambola_obj.generated_numbers else []
    context = {
        'min_range': tambola_obj.min_range if tambola_obj else 1,  # Default to 1 if tambola_obj is None
        'max_range': tambola_obj.max_range if tambola_obj else 100,  # Default to 100 if tambola_obj is None
        'generated_numbers': generated_numbers,
    }

    return render(request, 'tambola.html', context)

def generate_number(request):
    tambola_obj = Tambola.objects.last()

    if tambola_obj:
        min_range = tambola_obj.min_range
        max_range = tambola_obj.max_range
        all_numbers = set(range(min_range, max_range + 1))
        generated_numbers = set(map(int, tambola_obj.generated_numbers.split(','))) if tambola_obj.generated_numbers else set()

        remaining_numbers = all_numbers - generated_numbers

        if remaining_numbers:
            next_number = random.choice(list(remaining_numbers))
            generated_numbers.add(next_number)
            tambola_obj.generated_numbers = ','.join(map(str, generated_numbers))
            tambola_obj.save()

    return redirect('tambola')

# weather/views.py
from django.shortcuts import render
import requests
from django.conf import settings

def get_temperature(api_key, city='Bangalore', country='india', units='metric'):
    url = f'http://api.weatherapi.com/v1/current.json?q={city},{country}&units={units}&appid=7212cb2489944ae5889121501242601'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors (e.g., 404, 500)

        data = response.json()

        if 'main' in data and 'temp' in data['main']:
            temperature = data['main']['temp']
            return temperature
        else:
            return f'Temperature data not found in the response: {data}'
    except requests.exceptions.RequestException as e:
        return f'Failed to fetch weather data. Error: {e}'

def temperature_api(request):
    api_key = settings.OPENWEATHERMAP_API_KEY
    temperature = get_temperature(api_key)
    print(temperature)
    return render(request, 'temperature_api.html', {'temperature': temperature})

from django.shortcuts import render, redirect
import requests
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
import json

def login_view(request):
    if request.method == 'POST':
        # Get the form data
        username = request.POST['username']
        password = request.POST['password']

        # Make a request to the external API to validate credentials
        api_url = 'https://netzwelt-devtest.azurewebsites.net/Account/SignIn'
        payload = {
            "username": username,
            "password": password
        }
        response = requests.post(api_url, json=payload)

        print("API Request:", response.request.url)
        print("API Request Body:", response.request.body.decode())
        print("API Response:", response.text)

        if response.status_code == 200:
            # User is authenticated in the external API, authenticate the user in Django
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print("User is authenticated in Django.")
                return redirect('home')
            else:
                error_message = 'Failed to authenticate the user in Django.'
        else:
            # Authentication failed, display an error message
            error_message = 'Invalid username or password.'
        print("Authentication failed.")
        return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')


def home_view(request):
    # Check if the user is authenticated
    if not request.user.is_authenticated:
        return redirect('login')

    # Fetch the list of territories from the external API
    api_url = 'https://netzwelt-devtest.azurewebsites.net/Territories/All'
    response = requests.get(api_url)
    territories = response.json()

    # Arrange the list of territories into a hierarchical structure
    hierarchy = build_hierarchy(territories)

    return render(request, 'home.html', {'hierarchy': hierarchy})

def build_hierarchy(territories):
    hierarchy = {}
    
    for territory in territories['data']:
        territory_id = territory['id']
        parent_id = territory['parent']
        territory_name = territory['name']

        node = {'id': territory_id, 'name': territory_name, 'children': []}

        if parent_id in hierarchy:
            hierarchy[parent_id]['children'].append(node)
        elif parent_id is None:
            hierarchy[territory_id] = node
        else:
            print(f"Parent ID {parent_id} not found for territory {territory_id}")

    return list(hierarchy.values())





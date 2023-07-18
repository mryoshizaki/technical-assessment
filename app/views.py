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
    territory_dict = {territory['id']: territory for territory in territories['data']}
    hierarchy = []

    def add_children(node):
        territory_id = node['id']
        if territory_id in territory_dict:
            territory = territory_dict[territory_id]
            node['children'] = [add_children(child) for child in territory_dict.values() if child['parent'] == territory_id]
        return node

    for territory in territories['data']:
        if territory['parent'] is None:
            hierarchy.append(add_children({'id': territory['id'], 'name': territory['name'], 'children': []}))

    return hierarchy






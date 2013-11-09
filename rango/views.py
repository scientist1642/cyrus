from django.http import HttpResponse
from django.template import RequestContext
from django.shortcuts import render_to_response
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime

def decode_url(cat_name_url):
    return cat_name_url.replace('_', ' ')

def encode_url(cat_name_url):
    return cat_name_url.replace(' ', '_')

def index(request):

    # Obtain the context
    context = RequestContext(request)
    
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {'categories' : category_list, 'pages' : page_list}
    for category in category_list:
        category.url = category.name.replace(' ', '_')

    response = render_to_response('rango/index.html', context_dict, context)


    if request.session.get('last_visit'):
        last_visit_time = request.session.get('last_visit')
        visits = request.session.get('visits', 0)

        if (datetime.now() - datetime.strptime(last_visit_time[:-7], "%Y-%m-%d %H:%M:%S")).days > -1:
            request.session['visits'] = visits + 1
            request.session['last_visit'] = str(datetime.now())
    else:
        request.session['last_visit'] = str(datetime.now())
        request.session['visits'] = 1
    return response

def about(request):
    return render_to_response('rango/about.html', {}, RequestContext(request))
    #return HttpResponse("<a href='/rango/'>Index</a>")


def category(request, category_name_url):

    context = RequestContext(request)

    #reqconstruct category name
    category_name = decode_url(category_name_url)
    
    context_dict = {'category_name' : category_name, 'category_name_url': category_name_url}

    try:
        category = Category.objects.get(name=category_name)
        pages = Page.objects.filter(category=category)
        context_dict['pages'] = pages
        context_dict['category'] = category
    except Category.DoesNotExist:
        pass

    return render_to_response('rango/category.html', context_dict, context)


def add_category(request):
    context = RequestContext(request)

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit = True)
            return index(request)
        else:
            print form.errors
    else:
        form = CategoryForm()

    return render_to_response('rango/add_category.html', {'form': form}, context)

def add_page(request, category_name_url):
    context = RequestContext(request)

    category_name = decode_url(category_name_url)
    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():

            page = form.save(commit=False)
            page.category = Category.objects.get(name=category_name)
            page.views = 0
            page.save()
            return category(request, category_name_url)
        else:
            print form.errors
    else:
        form = PageForm()

    return render_to_response('rango/add_page.html',
        {'category_name_url': category_name_url,
         'category_name': category_name, 'form': form},context)


def register(request):
    if request.session.test_cookie_worked():
        print 'Test cookie worked'
        request.session.delete_test_cookie()
    context = RequestContext(request)

    registered = False
    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()

            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True
        else:
            print user_form.errors, profile_form.errors

    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    context_dict = {'user_form' : user_form, 'profile_form': profile_form, 'registered':registered}

    return render_to_response('rango/register.html', context_dict, context)

def user_login(request):

    context = RequestContext(request)

    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse('Your account is disabled')
        else:
             print 'invalid login details:{0}, {1}'.format(username, password)
             return HttpResponse("Invalid login details supplied.")
    else:
        return render_to_response('rango/login.html',{}, context)


@login_required
def restricted(request):
    return HttpResponse('Since you are logged in you can see this message')

@login_required
def user_logout(request):
    logout(request)

    return HttpResponseRedirect('/rango/')


def charge(request):
    import stripe
    stripe.api_key = 'sk_test_lXShtSPE6dS9qTY4skH8rUmr'
    if request.method =='POST':
        token = request.POST['stripeToken']
        try:
            charge = stripe.Charge.create(
                amount=3000, # amount in cents, again
                currency="gel",
                card=token,
                description="payinguser@example.com")

        except  (stripe.CardError,stripe.InvalidRequestError):
            return HttpResponse("unsuccessful")

        print request
        return HttpResponse("successful")

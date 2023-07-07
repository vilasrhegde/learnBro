from django.shortcuts import render,redirect

from django.contrib.auth.decorators import login_required
from django.db.models import Q
# from  django.contrib.auth.models import User

from django.contrib.auth import authenticate, login, logout 
from django.contrib import messages


# from django.contrib.auth.forms import UserCreationForm
# Create your views here.
from django.http import HttpResponse

from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm
# rooms = [
#     {'id':1, 'name':'Lets learn python'},
#     {'id':2, 'name':'Chin up designers!'},
#     {'id':3, 'name':'Go big Developers..'},

# ]


def  loginPage(request):
    page = 'login'

    if request.user.is_authenticated: # if user already logged in, then he can't manually enter /login
        return redirect('home')

    if request.method == 'POST':
        # username = request.POST.get('username').lower()
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email) 
        except:
            messages.error(request, 'User does not exist!')
            return redirect('login')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or Password did not match!')

    context ={'page':page}
    return render(request,'base/login_register.html', context)



def logoutUser(request):
    logout(request )
    return redirect('home')

def registerPage(request):
    # form = UserCreationForm()
    form = MyUserCreationForm()

    if request.method == 'POST':
        # form = UserCreationForm(request.POST)
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)# freezing the form by saving. To change the data
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Something occured during registration!')

    return render(request, 'base/login_register.html',{'form':form})


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    # __ means parent, icontains => contains element, rather than ==, i means case insensitive
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)) # Q enables us to use AND(&), OR(|) while searching/matching

    topics = Topic.objects.all()[:5]
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {'rooms':rooms, 'topics':topics, 'room_count':room_count, 'room_messages':room_messages}
    return render(request, 'base/home.html', context)

def room(request,  pk):
    # return HttpResponse('Welcome to Room')

    # room = None
    # for i in rooms:
    #     if i['id'] == int(pk):
    #         room =  i

    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all() # we can query children also
    participants = room.participants.all()
    if request.method=='POST':
        message  = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body'),
        )
        room.participants.add(request.user)
        return redirect('room',pk=room.id)


    context = {'room':room, 'room_messages':room_messages, 'participants': participants}

    return render(request, 'base/room.html',context)


def userProfile(request,pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()#get children using _set
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'room_messages': room_messages, 'topics':topics}
    return render(request,'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name) # get if it's present, created will be false since the topicname isnt present

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),

        )
        return redirect('home')
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False) #save into database 
        #     room.host = request.user
        #     room.save()
        #     return redirect('home')

    context ={ 'form': form, 'topics':topics }
    return render(request,'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room) # form is prefilled
    topics = Topic.objects.all()


    if request.user != room.host:
        return HttpResponse('You are not allowed here!!!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
     
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        #     return redirect('home')

    context = {'form':form, 'topics':topics,'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request,pk):
    room = Room.objects.get(id=pk)


    if request.user != room.host:
        return HttpResponse('You are not allowed here!!!')

    if request.method == "POST":
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':room})



@login_required(login_url='login')
def deleteMessage(request,pk):
    message = Message.objects.get(id=pk)


    if request.user != message.user:
        return HttpResponse('You are not allowed here!!!')

    if request.method == "POST":
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj':message})



@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)
    if request.method == 'POST':
        form = UserForm(request.POST,request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile',pk=user.id)
    return render(request,'base/update-user.html',{'form':form})

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    return render(request,'base/topics.html',{'topics':topics})

def activityPage(request):
    room_messages = Message.objects.all()
    return render(request, 'base/activity.html',{'room_messages':room_messages})
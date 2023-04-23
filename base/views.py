
from cgi import print_arguments
from django.shortcuts import render, redirect
from .models import ChatMessage, Profile, Friend
from .forms import ChatMessageForm
from .serializer import ProfileSerializer, FriendSerializer, ChatMessageSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
import json


@api_view(['GET'])
def index(request):
    user = request.user.profile

    friends = user.Friend.all()
    context = {"user": user, "friends": friends}
    serializer = ProfileSerializer(user, many=True)
    serializer = FriendSerializer(friends, many=True)
    
    return Response(serializer.data)

@api_view(['GET', 'POST'])
def detail(request,pk):
    friend = Friend.objects.get(profile_id=pk)
    user = request.user.profile
    profile = Profile.objects.get(id=friend.profile.id)
    chats = ChatMessage.objects.all()
    rec_chats = ChatMessage.objects.filter(msg_sender=profile, msg_receiver=user, seen=False)
    rec_chats.update(seen=True)
    form = ChatMessageForm()
    if request.method == "POST":
        form = ChatMessageForm(request.POST)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.msg_sender = user
            chat_message.msg_receiver = profile
            chat_message.save()
            return redirect("detail", pk=friend.profile.id)
    serializer = ProfileSerializer(user, many=True)
    serializer = FriendSerializer(friend, many=True)
    serializer = ChatMessageSerializer(chats, rec_chats, many=True)
    context = {"friend": friend, "form": form, "user":user, 
               "profile":profile, "chats": chats, "num": rec_chats.count()}
    return Response(serializer.data)


@api_view(['GET'])
def sentMessages(request, pk):
    user = request.user.profile
    friend = Friend.objects.get(profile_id=pk)
    profile = Profile.objects.get(id=friend.profile.id)
    data = json.loads(request.body)
    new_chat = data["msg"]
    new_chat_message = ChatMessage.objects.create(body=new_chat, msg_sender=user, msg_receiver=profile, seen=False )
    serializer = ProfileSerializer(user, many=True)
    serializer = FriendSerializer(friend, many=True)
    serializer = ChatMessageSerializer(new_chat, many=True)
    print(new_chat)
    return Response(serializer.data)


@api_view(['GET'])
def receivedMessages(request, pk):
    user = request.user.profile
    friend = Friend.objects.get(profile_id=pk)
    profile = Profile.objects.get(id=friend.profile.id)
    arr = []
    chats = ChatMessage.objects.filter(msg_sender=profile, msg_receiver=user)
    serializer = ProfileSerializer(user, many=True)
    serializer = FriendSerializer(friend, many=True)
    serializer = ChatMessageSerializer(chats, many=True)
    for chat in chats:
        arr.append(chat.body)
    return Response(serializer.data)


@api_view(['GET'])
def chatNotification(request):
    user = request.user.profile
    friends = user.friends.all()
    arr = []
    serializer = ProfileSerializer(user, many=True)
    serializer = FriendSerializer(friend, many=True)
    for friend in friends:
        chats = ChatMessage.objects.filter(msg_sender__id=friend.profile.id, msg_receiver=user, seen=False)
        arr.append(chats.count())
    return Response(serializer.data)
    
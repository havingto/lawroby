from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

# Create your views here.

def intro(request):
    starting=[
        'OK, I am ready.',
        'First, I would like to know a bit more about you.',
    ]
    return render(request, 'portal/intro.html', { 'starting' : starting })

def disclaimer(request):

    choice_number = request.POST.get('choice', False)
 
    if choice_number == '1':

        timeframe=[
            'It relates to events that happened sometime in the past.',
            'It is happening right now, or just recently.'
        ]
        question_text = ('What is the time-frame of your present inquiry?')
        context = {'question_text' : question_text, 'timeframe' : timeframe}
        return render(request, 'employment/employ_intro.html', context)
 
    else: 
        return render(request, 'portal/goodby.html')

def portal(request):

    choice_number = request.POST.get('choice', False)
 
    if choice_number == '1':

        acceptance=[
            'I am fine with that.',
            'Perhaps, I come back another time.'
        ]
        return render(request, 'portal/disclaimer.html', {'acceptance' : acceptance})
 
    else:
        start=[
            'OK, I am ready.',
            'No, thanks. I just dropped by to look around.'
        ]
        return render(request, 'portal/about.html', {'start' : start})
        
def about(request):

    choice_number = request.POST.get('choice', False)

    if choice_number == '1':

        acceptance=[
            'I am fine with that.',
            'Perhaps, I come back another time.'
        ]
        return render(request, 'portal/disclaimer.html', {'acceptance' : acceptance})
    
    else:        
        return render(request, 'portal/goodby.html')
    


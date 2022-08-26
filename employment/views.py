from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.utils.datastructures import MultiValueDictKeyError
from .models import Abort, Exit, Law, Other, Case, Issue, Temporary, Direction 
from .models import Question, Choice, Comment, Dependency, Reference
from .classes import G
from django.core.exceptions import ObjectDoesNotExist
from PyPDF2 import PdfFileMerger
import io
from django.http import FileResponse
from django.conf import settings
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

## To activate tracking for testing, replace '# print(' with 'print('.

## The relative locations of the output pdf files
RELEVANT_LAW = str(BASE_DIR) + '\\employment\\legislation\\relevant_law\\'
FULL_SECTIONS = str(BASE_DIR) + '\\employment\\legislation\\full_sections\\'
# RELEVANT_LAW = str(BASE_DIR) + '/employment/legislation/relevant_law/'
# FULL_SECTIONS = str(BASE_DIR) + '/employment/legislation/full_sections/'


def intro(request):
## Initiate the global variables
    G.key = ""
    G.val = ""
    G.choices = []
    G.tense = ""
    G.choice_ids = []
    G.resolve = []
    G.case = {}
    G.answers = []
    G.question_text = ""
    G.html = ""
    G.question_id = 0

## Post the introductory page in past or present tense
    ch = request.POST.get('choice', False)
    if ch == '1':
        G.tense = 'past'
    else:
        G.tense = 'now'
    comment_text = ('For this interview, please keep at hand all relevant documents '
        'and information that you would want to present to a lawyer in a real-life '
        'interview.')
    return render(request, 'employment/comment.html', {'comment_text': comment_text} )

###########
# The main part of the interview
###########

def interview(request):

    # print('URL = interview')
    # print('G.key, G.val, G.case, G.resolve, G.tense')
    # print(G.key, G.val, G.case, G.resolve, G.tense)

    if G.key == "":
# redirection came from the intro page, i.e. the session is just starting

        G.key = 'issue'
        G.val = '(default)'
        # print('First assignment of the Pair:  '  + G.key + '-' + G.val)

    else:
## redirection came from the interview page with the choice (new_value) 
## submitted by the user

        requested = request.POST 
        # print('Requested POST: ' + str(requested))

## Check whether the request came from terminating class after a back page
        if G.html == 'exit':
            context={ 
                'error_message': "(Please don't use <back-page>. If you think some of your previous responses "
                    "were incorrect, click on the logo and start again.)\n\n",
                        }
            return render( request, 'employment/exit.html', context )
        if G.html == 'abort':
            context={ 
                'error_message': "(Please don't use <back-page>. If you think some of your previous responses "
                    "were incorrect, click on the logo and start again.)\n\n",
                        }
            return render( request, 'employment/abort.html', context )
        if G.html == 'other_issue':
            context={ 
                'error_message': "(Please don't use <back-page>. If you think some of your previous responses "
                    "were incorrect, click on the logo and start again.)\n\n",
                        }
            return render( request, 'employment/other_issue.html', context )

        if G.html == 'comment':
## the HTTP request was a comment (with no choice assigned)

            if list(requested)[1] == 'comment':
## The response came from comment.html, so G.val will take on new_value in Comment record

                # print('Searching for comment: '+ G.key+'-'+G.val)
                comment = Comment.objects.get(key=G.key, value=G.val)
                G.val = str(comment.new_value)
                # print('The new_value from comment: '+G.val+' So the new Pair is '+G.key+'-'+G.val)
            else:
## the request was a comment.html, but the response came from a different page 
## after back page from user
                comment = Comment.objects.get( key=G.key, value=G.val )
                # print(G.key + '-' + G.val + ' is in Comment')
                if G.tense == 'past':
                    comment_text = comment.comment_text_past
                else:
                    comment_text = comment.comment_text_now
                context={ 
                    'comment_text' : comment_text,
                    'error_message': "If you think some of your previous responses "
                        "were incorrect, it's the best to start again from the home page."
                        "\n\nOtherwise, please press the button on the bottom to continue.",
                            }
                return render(request, 'employment/comment.html', context)

        elif list(requested)[1] == str(G.question_id):
## the HTTP response was a question with the correct question_id and relevant choices. 
## G.val will change.
## This also means that G.choice_ids has already been assigned.
## (The numbering in a HTML form start at 1, not at 0, as in a list.)

            G.html = "question"
            choice = int(requested[list(requested)[1]])
            pick = G.choice_ids[choice-1]
            a = [G.question_text, G.choices[choice-1]]
            G.answers.append(a)
            ch = Choice.objects.get(id=pick)
            G.val = str(ch.new_value)
            # print('user choice has been evaluated. The Pair is ' + G.key + '-' + G.val)

        else:
## Mismatch of question_id. The response came from a previous page after a back page

            G.html = "question"
            context={ 
                'choices' : G.choices,
                'question_text' : G.question_text,
                'error_message': "Please don't leave this page without making "
                    "a choice!\n\n (If you think some of your previous responses "
                    "were incorrect, it's the best to start again from the home page.)\n\n\n\n",
                'question_id' : G.question_id,
                        }
            return render( request, 'employment/interview.html', context )

## A new Pair has been established from user input.
    new_pair = True
    
    while True:
## This loop determines what happens with the new Pair
        # print('New pair? ' + str(new_pair))

        while new_pair:
## This loop checks whether the value of a new Pair is reassigned either with a condition
## in Dependency, i.e. with reference to another key / final_value Pair, or without condition. 
## In this case the variable new_pair retains its "TRUE" value, as it has not been fully
## evaluated.
##
## If a Pair is not in Dependency, then the variable new_pair changes to "FALSE", i.e. there
## is no new value assigned to the key. In this case, the Pair will be checked in other classes.

## If the reference key field is not "" for a Dependency record, that reference key 
## has to be evaluated. In this case, we temporarily stop the
## evaluation of the original Pair, and evaluate the reference key (before we return and 
## continue the evaluation of the original pair).
## Of course, the evaluation of this new key may also include further references.
## Hence the need for a stack with Pairs to return to.

            dependency=Dependency.objects.filter( key=G.key, value=G.val )
## dependency will be a set of id's from the class for the Pair (can be empty)

            if dependency.count() == 0:
## if G.val is not in dependency           
                # print(G.key + '-' + G.val + '   is not in Dependency')
                new_pair = False

            else:
## Pair is in Dependency, the corresponding references (if any) will be evaluated and 
## the value of G.val will change
                # print(G.key + '-' + G.val + ' is in dependency. G.val will change.')
                # print('dependency:' + str(dependency))

                for d in dependency:
## Looping through the relevant records in Dependency, we check whether ref_key 
## has been evaluated, and (if it has) whether its (final)value is identical with ref_val
                    # print('looping:' + str(d))
                    d_id=int(str(d))
                    d_record=Dependency.objects.get(id=d_id)
## Arrange the reference pair into a list
                    reference=[ d_record.ref_key, d_record.ref_value ]

                    if reference[0] == "":
## If there is no reference to evaluate, it is a simple reassign of value.
                        G.val = str(d_record.new_value)
                        # print('G.val has been reassigned, the new Pair: ' + G.key +'-' + G.val)
                        break
                    else:
## There is a reference to evaluate.                        
                        # print('The reference is ' + str(reference))
                        if reference[0] in list(G.case):                          
## If the reference key is in Case, i.e. it has been evaluated

                            if G.case[reference[0]] == reference[1]:
## ...and the reference key's value is the one assigned to it in Case'
##  then the dependency is satisfied, G.val assigned to new_value in the  
## record, and a new_pair is established. We break out of this for loop, and continue 
## with checking the new Pair in Dependency, so we stay in the while loop 
## (new_pair stays TRUE)
                                # print(reference[0] + ' is in Case, and its value is ' + G.case[reference[0]])
                                G.val = str(d_record.new_value)
                                # print('The reference is satisfied (pair is in Case), new G.val: ' + G.key +'-' + G.val)
                                break

## Otherwise, i.e. if the referenced key is in G.case, i.e. it has already been evaluated,
## but the final_value to that key in G.case is not as in the Dependency record,
## then the dependency is not satisfied, we do nothing and we stay in this for loop
## moving on to the next record (with id = d) in the list dependency.

                        else:
## If the reference key is not in Case, i.e. it has not been evaluated, then the current 
## Pair is appended to the stack G.resolve, we break out of this for loop,
## and the evaluation of the reference key begins with the value "(default)". 
                            # print(reference[0] + '  reference key has not been evaluated')
                            r = [G.key, G.val]
                            G.resolve.append(r)
                            # print('Pair appended to G.resolve: ' + str(G.resolve))
                            G.key = reference[0]
                            G.val = '(default)'
                            # print('New pair: ' + G.key +'-' + G.val)
## As we found a new key to evaluate, we break out of this for loop and check if it
## too has been reassigned in Dependency.
                            break
                else:
## This is the end of the for loop, i.e. all of the reference pairs tried, but none
## matched. The Pair is unchanged, i.e. stops being a new pair.
## (It will be tried in the other classes.).
                    # print('End of for loop of dependency records. None satisfied.')
                    new_pair = False       
        try:
            abort=Abort.objects.get(key=G.key, value=G.val)
        except ObjectDoesNotExist:
            # print(G.key + '-' + G.val + '   is not to abort')
            pass
        else:
# aborted, likely due to jurisdiction problems
            # print(G.key + '-' + G.val + ' is in Abort')
            G.html = "abort"
            return render( request, 'employment/abort.html')
        try:
            other=Other.objects.get(key=G.key, value=G.val)
        except ObjectDoesNotExist:
            # print(G.key + '-' + G.val + '   is not in other issue')
            pass
        else:
# interrupted as the case seems to fall beyond the ambit of the FWA.
            # print(G.key + '-' + G.val + ' is in Other')
            G.html = "other_issue"
            return render( request, 'employment/other_issue.html')
        try:
            finish=Exit.objects.get(key=G.key, value=G.val)
        except ObjectDoesNotExist:
            # print(G.key + '-' + G.val + '   is not in exit')
            pass
        else:
# If G.key has reached its final value append the Pair to G.case
            G.case[G.key] = str(finish.final_value)
            # print(G.key + '-' + G.val + '   is in exit')
# At this point the session reached its end, and the entire transcript becomes available.
            # print(' The session has finished, the PDF files are ready. \nThe case was:\n' + str(G.case))
            G.html = "exit"
            return render( request, 'employment/exit.html' )

        try:
            comment = Comment.objects.get( key=G.key, value=G.val )
        except ObjectDoesNotExist:
            # print(G.key + '-' + G.val + '   is not in comment')
            pass
        else:
            # print(G.key + '-' + G.val + ' is in Comment')
            if G.tense == 'past':
                comment_text = comment.comment_text_past
            else:
                comment_text = comment.comment_text_now
            G.html = "comment"
            return render(request, 'employment/comment.html', {'comment_text':comment_text})
        try:
            question=Question.objects.get(key=G.key, value=G.val)
        except ObjectDoesNotExist:
            # print(G.key + '-' + G.val + '   is not in question')
            pass
        else:
## As the class Choice returns the id in string, i.e. query set, they need to be
## converted to int and put into a list to iterate
            # print('The Pair   ' + G.key + ' ' + G.val + '   points to a question')
            G.choice_ids = []
            G.choices = []
            choice_id_list = Choice.objects.filter(key=G.key, value=G.val)
            for ch_id in choice_id_list:
## Create list of ID's of choices with items as int)
                G.choice_ids.append( ch_id.id )                    
## Create list of choice_text with items as string)
                if G.tense == 'past':
                    G.choices.append( ch_id.choice_text_past )
                else:
                    G.choices.append( ch_id.choice_text_now )
            if G.tense == 'past':
                G.question_text = question.question_text_past
            else:
                G.question_text = question.question_text_now
            G.question_id = G.question_id + 1
            context={ 'choices' : G.choices,
                      'question_text' : G.question_text,
                      'question_id' : G.question_id,
                    }
            G.html = "question"
            return render( request, 'employment/interview.html', context )

        try:
            direction=Direction.objects.get(key=G.key, value=G.val)
        except ObjectDoesNotExist:
            # print(G.key + '-' + G.val + '  is not in Direction')
            reference=Reference.objects.get(key=G.key, value=G.val)
            # print(G.key + '-' + G.val + '   is in Reference')
# the Pair must be in Reference, i.e. G.key has reached its final value
            G.case[G.key] = str(reference.final_value)
            # print('Pair is added to Case:')
            # print(G.case)
# append the Pair to G.case pop "old" Pair from the G.resolve.
            # print(G.key + '   final_value: ' + str(reference.final_value))
            pair = G.resolve.pop()
            G.key = pair[0]
            G.val = pair[1]
            # print(G.key + '-' + G.val + '   popped from resolve')
            new_pair = True
        else:
# If the Pair is in Direction, i.e. G.key has reached its final value
# and a new Key is to be established append the Pair to G.case
            G.case[G.key] = str(direction.final_value)
            # print('Case is appended: ' + str(G.case))
# and establish a new Key with default value.
            # print(G.key + '-' + G.val + '   is in Direction. The new Key: ' + str(direction.new_key))
            G.key = str(direction.new_key)
            G.val='(default)'
            new_pair = True

#########
# Creating the output pdf files
#########
def create_output(request):

    G.case_id = Case.objects.create(
        case = G.case,
        answers = G.answers,
        )
    # print('Case id is ' + str(case_id))

    case = G.case
    relevant = []
    full = []

    if 'feedback' in request.POST:
        return render( request, 'employment/feedback.html')

    if 'relevant_law' in request.POST:
# append (non-null) relevant_law file name strings into two lists
        for k, v in case.items():
            try:
                law = Law.objects.get(key=k, final_value=v)
            except ObjectDoesNotExist:
                # print(k + '-' + v + '   is not in Law')
                pass
            else:
                r = str(law.relevant_law)
                if r == "":
                    pass
                else:
                    relevant.append(r)
# merge relevant pdf files into an output file
        merger = PdfFileMerger()
        for r in relevant:
            relevant_pdf = open( RELEVANT_LAW + r + ".pdf", "rb" )
            merger.append(relevant_pdf)
            # print(r + '.pdf has been uppended to relevant output')
# Create a file-like buffer to receive PDF data.
        relevant_buffer = io.BytesIO()
        relevant_buffer.flush()
        # print('relevant_buffer assigned and flushed')
# Write the merged pdf file into an output file-like object
        merger.write(relevant_buffer)
        # print('relevant law output file created')
        relevant_buffer.seek(0)
        return FileResponse(relevant_buffer, as_attachment=True, filename='Relevant law.pdf')            

    if 'full_sections' in request.POST:
# append (non-null) full_section file name strings into two lists
        for k, v in case.items():
            try:
                law = Law.objects.get(key=k, final_value=v)
            except ObjectDoesNotExist:
                # print(k + '-' + v + '   is not in Law')
                pass
            else:
                f = str(law.full_section)
                if f == "":
                    pass
                else:
                    full.append(f)
# merge relevant pdf files into an output file
        merger = PdfFileMerger()
        for f in full:
            full_pdf = open( FULL_SECTIONS + f + ".pdf", "rb" )
            merger.append(full_pdf)
            # print(f + '.pdf has been uppended to full section output')
# Create a file-like buffer to receive PDF data.
        full_buffer = io.BytesIO()
        full_buffer.flush()
        # print('full section buffer assigned and flushed')
# Write the merged pdf file into an output file-like object
        merger.write(full_buffer)
        # print('full sections output file created')
        full_buffer.seek(0)
        return FileResponse(full_buffer, as_attachment=True, filename='Full sections.pdf')            

#########
# Storing user input in case of an issue falling out of the ambit of the FWA
#########

def other_issue(request):
    issue = request.POST['issue']
    if len(issue) > 10:
        Issue.objects.create(
            key = G.key,
            case = G.case,
            answers = G.answers,
            other_issue = issue
            )
    return render( request, 'employment/goodby.html')
#########
# Storing feedback in Case
#########

def feedback(request):
    feedback = request.POST['feedback']
    if len(feedback) > 10:
        c = Case.objects.get( id=str(G.case_id))
        c.feedback = str(feedback)
        c.save()
    return render( request, 'employment/goodby.html')
 

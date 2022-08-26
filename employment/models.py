from django.db import models
from django.utils import timezone
##import uuid

# Create your models here.

##### Classes at the end of session

class Abort(models.Model):
# Abort takes place when there is a jurisdiction problem, so no help is available.

    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)    
    def __str__(self):
        return "%s" % (self.id)

class Exit(models.Model):
# Final key. The session exits with a PDF output. 

    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    final_value = models.CharField(max_length=50)
    def __str__(self):
        return "%s" % (self.id)

class Law(models.Model):
# Relevant law snippets and full sections in PDF files.

    key = models.CharField(max_length=50)
    final_value = models.CharField(max_length=50)
    relevant_law = models.CharField(max_length=100)
    full_section = models.CharField(max_length=100)
    def __str__(self):
        return "%s" % (self.id)

class Other(models.Model):
# The issue is out of ambit of FWA.

    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    def __str__(self):
        return "%s" % (self.id)

####### Classes to store Cases and Issues

class Case (models.Model):

    email = models.EmailField(null=True)
    date = models.DateTimeField(auto_now=True)
    case = models.JSONField(default=dict)
    answers = models.JSONField(default=dict)
    feedback = models.CharField(max_length=1500, null=True)
    def __str__(self):
        return '%s' % str(self.id)

class Issue (models.Model):
# an issue which is out of the ambit of the FWA (or algorithm error) to examine.
# alternatively, it may also pass this info to admin via email.
    key = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now=True)
    case = models.JSONField(default=dict)
    answers = models.JSONField(default=dict)
    other_issue = models.CharField(max_length=1500)
    def __str__(self):
        return "%s" % (self.id)

class Temporary (models.Model):
# Temporary storage of Case where session stopped due to missing information
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now=True)
    case = models.JSONField(default=dict)
    answers = models.JSONField(default=dict)
    def __str__(self):
        return '%s' % str(self.id)

####### Classes where final_value is assigned to a key and session continues

class Direction(models.Model):
# At this point the A/final_value pair moves into the Case dictionary,
# and the key changes to next_key with value "default".

    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    final_value = models.CharField(max_length=50)
    new_key = models.CharField(max_length=50)
    def __str__(self):
        return "%s" % (self.id)

class Reference(models.Model):
# Referred key. Called when there is a dependency.
# When the final_value is reached, the control returns to the caller. 

    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    final_value = models.CharField(max_length=50)
    def __str__(self):
        return "%s" % (self.id)

####### Classes for interaction with user

    
class Question(models.Model):
    
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    question_text_now = models.TextField()
    question_text_past = models.TextField()
    def __str__(self):
        return "%s" % (self.id)

class Choice(models.Model):
# At this point the choice user imput determines the new value
# for the A/value pair. It returns the ID to avoid pattern matching
# of long text.

    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    choice_text_now = models.CharField(max_length=500)
    choice_text_past = models.CharField(max_length=500)
    new_value = models.CharField(max_length=50)
    def __str__(self):
        return "%s" % (self.id)

class Comment(models.Model):
# Comments are guidance to the user.
# They render a form where there is only one choice: "continue".

    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    comment_text_now = models.TextField()    
    comment_text_past = models.TextField()    
    new_value = models.CharField(max_length=50)
    def __str__(self):
        return "%s" % (self.id)

###### Non-interactive classes that control the flow of the session
    
class Dependency(models.Model):
## Stores the Pairs where VAL is assigned a new_value. Each entry may have one
## freference / dependency to check, or none (that means Val changes without 
## condition, i.e it is a simple reassign). 
## There may be multiple entries for the same Pair. Dependencies
## are key - final_value pairs in CASE which, if satisfied, then the key in
## Dependency takes on the corresponding new_value.
## If a reference key is not in CASE (have not been evaluated), then
## they need to be evaluated.
## (the reference Pairs may be empty, i.e. simple reassign of value.)

    key = models.CharField(max_length=50)
    value = models.CharField(max_length=50)
    new_value = models.CharField(max_length=50)
    ref_key = models.CharField(max_length=50)
    ref_value = models.CharField(max_length=50)
    def __str__(self):
        return "%s" % (self.id)

## class Reasign has been incorporated into Dependency
# class Reassign (models.Model):
# # VAL changes to new_value without conditions

#     key = models.CharField(max_length=50)
#     value = models.CharField(max_length=50)
#     new_value = models.CharField(max_length=50)
#     def __str__(self):
#         return "%s" % (self.id)




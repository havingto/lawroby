
def populate(apps, schema_editor):

    question_fields = [
        ]
    choice_fields = [
        ]

    direction_fields = [
        ]

    dependency_fields = [
        ]

    comment_fields = [
        ]

    abort_fields = [
        ]

    reference_fields = [
        ]

    exit_fields = [
        ]

    law_fields = [
        ]

    other_fields = [

        ]

    Question = apps.get_model("employment", "Question")
    Choice = apps.get_model("employment", "Choice")
    Direction = apps.get_model("employment", "Direction")
    Dependency = apps.get_model("employment", "Dependency")
    Comment = apps.get_model("employment", "Comment")
    Abort = apps.get_model("employment", "Abort")
    Reference = apps.get_model("employment", "Reference")
    Exit = apps.get_model("employment", "Exit")
    Law = apps.get_model("employment", "Law")
    Other = apps.get_model("employment", "Other")

    for put in question_fields:
        x1 = put[0]
        x2 = put[1]
        x3 = put[2]
        x4 = put[3]
        y = Question.objects.create(
            key=x1,
            value=x2,
            question_text_now=x3,
            question_text_past=x4,
        )

    for put in choice_fields:
        x1 = put[0]
        x2 = put[1]
        x3 = put[2]
        x4 = put[3]
        x5 = put[4]
        y = Choice.objects.create(
            key=x1,
            value=x2,
            choice_text_now=x3,
            choice_text_past=x4,
            new_value=x5
        )

    for put in direction_fields:
        x1 = put[0]
        x2 = put[1]
        x3 = put[2]
        x4 = put[3]
        y = Direction.objects.create(
            key=x1,
            value=x2,
            final_value=x3,
            new_key=x4,
        )

    for put in dependency_fields:
        x1 = put[0]
        x2 = put[1]
        x3 = put[2]
        x4 = put[3]
        x5 = put[4]
        y = Dependency.objects.create(
            key=x1,
            value=x2,
            new_value=x3,
            ref_key=x4,
            ref_value=x5,
        )

    for put in comment_fields:
        x1 = put[0]
        x2 = put[1]
        x3 = put[2]
        x4 = put[3]
        x5 = put[4]
        y = Comment.objects.create(
            key=x1,
            value=x2,
            comment_text_now=x3,
            comment_text_past=x4,
            new_value=x5,
        )
  
    for put in abort_fields:
        x1 = put[0]
        x2 = put[1]
        y = Abort.objects.create(
            key=x1,
            value=x2,
        )

        
    for put in reference_fields:
        x1 = put[0]
        x2 = put[1]
        x3 = put[2]
        y = Reference.objects.create(
            key=x1,
            value=x2,
            final_value=x3,
        )
        
    for put in exit_fields:
        x1 = put[0]
        x2 = put[1]
        x3 = put[2]
        y = Exit.objects.create(
            key=x1,
            value=x2,
            final_value=x3,
        )

    for put in law_fields:
        x1 = put[0]
        x2 = put[1]
        x3 = put[2]
        x4 = put[3]
        y = Law.objects.create(
            key=x1,
            final_value=x2,
            relevant_law=x3,
            full_section=x4,
        )

    for put in other_fields:
        x1 = put[0]
        x2 = put[1]
        y = Other.objects.create(
            key=x1,
            value=x2,
        )


        migrations.RunPython(populate),

template1="""
You are a doctor who needs to use a website called MDCalc inorder to check Doctor's Diagnosis in the information provided
MDCalc is the most trusted medical reference for clinical decision tools and content.
MDCalc is used by millions of clinicians around the world, including more than 80% of the clinicians in the United States alone. 
MDCalc is consistently rated as one of the most useful medical platforms for healthcare professionals in their daily workflow.

information provided:

{Information}

You are presented with the above information.
You need to verify Doctor's diagnosis
"""

template2="""
----------------------------------------------------
On the first page of website you are presented with the following options.
Choose every option that allows us to verify Doctor's diagnosis

{Options}

Choose every option that allows us to verify Doctor's diagnosis
----------------------------------------------------
"""

template3="""
{format_instructions}
"""

template4="""
information provided:
{Information}

Form title: {Option}
Based on the information provided above
fill this form below

Subheading:{subheading}
form:{form}


"""

information="""patient vitals:
age = 50 years old
Temperature =38.4°C
Heart rate =111 bpm
Respiratory rate = 25 bpm
 WBC count =15 K/microliter

Doctor Diagnosis = Sepsis

"""

template5=""" 

dawg
"""

show_form="""





"""
import statistics
from django import template
# from wellbeingapp.forms import SurveyForm
from wellbeingapp.models import *
import mammoth

register = template.Library()


@register.filter
def average(data_list, category):
    value_list = [i[category] for i in data_list]
    return round(statistics.mean(value_list), 1)


@register.filter
def getdata(dictionary, field):
    return dictionary.get(field, "")

@register.filter
def formdata(instance):
    form = SurveyForm(instance=instance)
    
    return form

# @register.filter
# def listToString(s):  
#     # initialize an empty string 
#     str1 = " " 
    
#     # return string   
#     return (str1.join(s)) 

@register.filter
def notesfill(qid):
    count = 0
    if TabularNotes.objects.filter(question_id=qid).count() == 0:
        count = 0
        
    else:
        count = 1
    return count

# @register.filter
# def notesfill2(survey_id):
#     count = 0

#     if TabularNotes.objects.filter(survey_id=survey_id).count() == 0:
#         count = 0
#     else:
#         count = 1
#     return count
                
@register.filter
def customnotesfill(uid):
    count = 0
    if CustomNotes.objects.filter(user2_id=uid).count() == 0:
        count = 0
        
    else:
        count = 1
    
    return count


@register.filter
def checkemp(pid):
    return len(pid)

@register.filter
def point(number):
    try:
        return '%.2f' % number
    except:
        return number

@register.filter
def checkcount(emp):
    return len(emp)

@register.filter
def convert_int(qid):
    return int(qid)

@register.filter
def checkusercount(qid):
    user_count = UserRankView.objects.filter(rank_idea_id=qid).values('user_id').count()
    
    return user_count

@register.filter
def lastuserid(qid, survey_id):
    user_count = UserRankView.objects.filter(survey=survey_id,rank_idea_id=qid).last()
    
    return user_count.user_id

@register.filter
def emoji_count_thumbup(string):
    return string.count('👍')

@register.filter
def emoji_count_thumbdown(string):
    return string.count('👎')

@register.filter
def emoji_count_thumbcross(string):
    return string.count('🤞')

@register.filter(name='split')
def split(value):
    """
        Returns the value turned into a list.
    """
    
    try:
        data = str(value).split('/')[1]
    except:
        return value
    return data

@register.filter
def view_content(doc_file):
    docs_content = ''
    try:
        f = open("media/{}".format(doc_file), 'rb')
        document = mammoth.convert_to_html(f)
        return document.value
    except Exception as e:
        print(' error ==',e)
        docs_content = ''
    return docs_content

@register.filter
def positive_count(idea_id):
    count = AddNotesForOptions.objects.filter(idea=idea_id, is_positive=True).count()
    return count

@register.filter
def nagative_count(idea_id):
    count = AddNotesForOptions.objects.filter(idea=idea_id, is_negative=True).count()
    return count

@register.filter
def items_positive_count(items_id):
    count = AddNotesForOptionsActionItems.objects.filter(items_id=items_id, is_positive=True).count()
    return count

@register.filter
def items_nagative_count(items_id):
    count = AddNotesForOptionsActionItems.objects.filter(items_id=items_id, is_negative=True).count()
    return count

@register.filter
def lastuseridforitems(qid):
    user_count = ActionItemsSelected.objects.filter(action_items_id=qid).last()
    return user_count.user_id

@register.filter
def user_selected(action_id, user_id):
    is_user_selected = UserSelectedHomeworkItems.objects.filter(
                                action_items_id=action_id, 
                                user_id=user_id
                                ).count()
    return is_user_selected


@register.filter
def lastuseridforhomework(action_id):
    user_count = UserSelectedHomeworkItems.objects.filter(action_items_id=action_id).last()
    return user_count.user_id
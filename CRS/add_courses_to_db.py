import pandas as pd
import json
from .models import Course


# add courses from json to database
def AddCoursesToDB(courses_json='CRS/courses.JSON'):

    fields = ["general.מספר מקצוע", "general.שם מקצוע", "general.נקודות", "general.סילבוס"]

    data = json.load(open(courses_json, encoding='utf-8'))
    courses_df = pd.json_normalize(data)

    sub_courses_df = courses_df.loc[:, fields]
    sub_courses_df.rename(
        columns={"general.שם מקצוע": "name", "general.מספר מקצוע": "number", "general.נקודות": "credit",
                 "general.סילבוס": "sylabus"},
        inplace=True)

    for row in sub_courses_df.itertuples(index=True, name='Pandas'):
        course = Course(name=row.name,
                        number=row.number,
                        number_string=row.number,
                        credit_points=row.credit,
                        info=row.sylabus)
        #print(course)
        # try:
        course.save()
        # except:
        #     print("error saving course " + row.number + row.name)

    # print(sub_courses_df.loc[[1,200,300,400,500],:])
    # dest = path + filename
    # sub_courses_df.to_csv(dest, index=False, encoding='utf-8')


def ClearCoursesDB():
    courses = Course.objects.all()
    for course in courses:
        course.delete()





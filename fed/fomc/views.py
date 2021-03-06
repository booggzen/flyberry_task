import json
import time
from datetime import datetime, timedelta
from django.shortcuts import render
from django.http import HttpResponse
from fomc import site_scraper
from fomc.models import MeetingScheduleEntry, ProjectionTableSummary
from fomc.models import populate_projection_tables

API_VERSION = "1.0"
AGE_LIMIT_DAYS = 7 # abitrary

def _timestamp_from_datetime(dt):
    return time.mktime(dt.timetuple()) * 1000

def _scrape_dates():
    return MeetingScheduleEntry.objects.order_by("-scrape_date").values_list("scrape_date", flat=True).distinct()
    

def _transpose_dicts(in_data, key, columns):
    transposed_dict = {}
    for obj in in_data:
        obj_dict = obj.as_dict(columns)
        _ID = obj_dict[key]
        for k, v in obj_dict.items():
            if k != key:
                if not k in transposed_dict:
                    transposed_dict[k] = {_ID: v}
                else:
                    transposed_dict[k][_ID] = v
    return transposed_dict

def JsonResponse(response, status=200):
    return HttpResponse(json.dumps(response), content_type='application/json', status=status)

def successful_response(data):
    result = {"status": "ok",
            "version": API_VERSION,
            "data": data}
    return JsonResponse(result, 200)
                         
def failure_response(code="00000", message="Unknown Error", http_status=500):
    result = {"status": "error",
              "code": code,
              "message": message}
    return JsonResponse(result, http_status)
            

def error404(request):
    return failure_response("404", "404 Error")

def error500(request):
    return failure_response("500", "500 Error")


def version(request):
    retrieval_dates = _scrape_dates()
    refresh_date = None
    if retrieval_dates:
        refresh_date = retrieval_dates[0]
    data = {"author": "Jim Hagan",
            "software last revised": _timestamp_from_datetime(datetime(2015, 1, 20)), # eventually pull this from GIT
            "most recent scrape date": _timestamp_from_datetime(refresh_date),
            "description": "Federal Reserve Information API",
            "source repository": "https://github.com/JimHagan/flyberry_task.git",
            "all scrape dates": [_timestamp_from_datetime(r) for r in retrieval_dates]}
    data_style = request.GET.get("data_style", "string")
    if data_style.lower() == "json":
        return successful_response(data)
    else:
        return successful_response(json.dumps(data))


"""
This is the primary method for querying FOMC ("Federal Reserve Open Market Committee")
meeting information.

base URL...

<server>/fed/fomc/calendar  

By itself the base URL will return a JSON repsonse with a data element containing a stringified JSON
list of meeting descriptions

Header info (successful response)...

{"status": "ok", "version": "1.0", "data": [<format dependent elements>]}

Example of a meeting element...

{"meeting_year": "2014", "meeting_end_date": "2014-01-29 00:00:00+00:00", "scrape_date": "2015-01-08 19:44:04.281746+00:00", "meeting_start_date": "2014-01-28 00:00:00+00:00", "projections": "False", "statement": "False", "meeting_name": "FOMC_2014_JANUARY", "estimated_release": "2014-01-29 07:00:00+00:00"}

Options...

transpose : (default="true") - Puts the data in column order.  If transpose is false, each JSON object represents a row.
stringify : (default="true") - Puts the JSON data element in a string format.
columns : (default = "") - This list of column names describes which fields to output.  If "" all standard fields will be output.

Sample URLs


http://localhost:8000/fed/fomc/calendar?transpose=false&stringify=false

http://localhost:8000/fed/fomc/calendar?transpose=false&stringify=false&columns=scrape_date,meeting_name,projections,statement

http://localhost:8000/fed/fomc/calendar?columns=meeting_name,projections,scrape_date

http://localhost:8000/fed/fomc/calendar?columns=meeting_name,projections,scrape_date&transpose=false&stringify=false

http://localhost:8000/fed/fomc/calendar?transpose=false&stringify=false&columns=scrape_date,meeting_name,statement_url

http://localhost:8000/fed/fomc/calendar?transpose=false&stringify=false&columns=projections,scrape_date,meeting_name,projections_html_url,projections_pdf_url


"""
def calendar(request):
    refresh_needed = True
    recent_recs = MeetingScheduleEntry.objects.filter(scrape_date__gte=datetime.utcnow() - timedelta(days=AGE_LIMIT_DAYS))
    refresh_needed = not recent_recs.exists()
    
    if refresh_needed:
        #in a projection mode we could allow data with different scrape dates to stick around.
        ProjectionTableSummary.objects.all().delete()
        MeetingScheduleEntry.objects.all().delete()
        print "Getting schedules..."
        raw_schedules = site_scraper.parse_fed_schedules()
        for sch in raw_schedules:
            if "month" in sch:
                schedule_object = MeetingScheduleEntry()
                schedule_object.from_original_dict(sch)
                schedule_object.save()
                if "parsed_proj_table_body" in sch:
                    populate_projection_tables(schedule_object, sch["parsed_proj_table_body"])

        print "Got schedules..."
                                    

    all_objects = MeetingScheduleEntry.objects.all().order_by("-meeting_start_date")
    
    transpose = request.GET.get("transpose", "true")
    
    columns = request.GET.get("columns", "").split(",")
    if columns == ['']:
        columns = []

    output_dict = _transpose_dicts(all_objects, "id", columns) if transpose.lower()=="true" else [obj.as_dict(columns) for obj in all_objects]
    
    
    stringify = request.GET.get("stringify", "true")
    if stringify.lower() == "false":
        return successful_response(output_dict)
    else:
        return successful_response(json.dumps(output_dict))


"""
This is the primary method for querying pace_of_firming table data associated
with FOMC meeting entries

base URL...

<server>/fed/fomc/pace_of_firming

By itself the base URL will return a JSON repsonse with a data element containing a stringified JSON
list of meeting descriptions

Header info (successful response)...

{"status": "ok", "version": "1.0", "data": [<format dependent elements>]}

Example of a table element...

{"meeting_year": "2014", "meeting_end_date": "2014-01-29 00:00:00+00:00", "scrape_date": "2015-01-08 19:44:04.281746+00:00", "meeting_start_date": "2014-01-28 00:00:00+00:00", "projections": "False", "statement": "False", "meeting_name": "FOMC_2014_JANUARY", "estimated_release": "2014-01-29 07:00:00+00:00"}

Options...

stringify : (default="true") - Puts the JSON data element in a string format.

Sample URLs

http://localhost:8000/fed/fomc/pace_of_firming

http://localhost:8000/fed/fomc/pace_of_firming?stringify=False

http://localhost:8000/fed/fomc/pace_of_firming?stringify=True&meeting_name=FOMC_2014_MARCH,FOMC_2014_JUNE

http://localhost:8000/fed/fomc/pace_of_firming?meeting_id=4263

http://localhost:8000/fed/fomc/pace_of_firming?meeting_id=4263,4273

http://localhost:8000/fed/fomc/pace_of_firming?begin_release=1401595200000.0

http://localhost:8000/fed/fomc/pace_of_firming?begin_release=1401595200000.0&end_release=1404172800000.0

http://localhost:8000/fed/fomc/pace_of_firming?begin_scrape=1420848000000.0

http://localhost:8000/fed/fomc/pace_of_firming?end_scrape=1420848000000.0

"""

def pace_of_firming(request):
    pof_tables = ProjectionTableSummary.objects.filter(table_name__icontains="appropriate_pace_of_policy_firming")
    output_list = []

    # There has got to be a more pythonic way of collapsing this repetitive filter code, but I'm not sure at the moment.
    meeting_ids = request.GET.get("meeting_id", None)
    if meeting_ids:
        pof_tables = pof_tables.filter(meeting_schedule_entry_id__in=[int(i) for i in meeting_ids.split(',')])

    meeting_names = request.GET.get("meeting_name", None)
    if meeting_names:
        pof_tables = pof_tables.filter(meeting_schedule_entry__meeting_name__in=[m.strip() for m in meeting_names.split(',')])

    begin_release = request.GET.get("begin_release", None)
    if begin_release:
        begin_release_datetime = datetime.utcfromtimestamp(float(begin_release) / 1000.0)
        pof_tables = pof_tables.filter(meeting_schedule_entry__estimated_release__gte=begin_release_datetime)
        
    end_release = request.GET.get("end_release", None)
    if end_release:
        end_release_datetime = datetime.utcfromtimestamp(float(end_release) / 1000.0)
        pof_tables = pof_tables.filter(meeting_schedule_entry__estimated_release__lte=end_release_datetime)
        

    begin_scrape = request.GET.get("begin_scrape", None)
    if begin_scrape:
        begin_scrape_datetime = datetime.utcfromtimestamp(float(begin_scrape) / 1000.0)
        pof_tables = pof_tables.filter(meeting_schedule_entry__scrape_date__gte=begin_scrape_datetime)

    end_scrape = request.GET.get("end_scrape", None)
    if end_scrape:
        end_scrape_datetime = datetime.utcfromtimestamp(float(end_scrape) / 1000.0)
        pof_tables = pof_tables.filter(meeting_schedule_entry__scrape_date__lte=end_scrape_datetime)


    for p in pof_tables:
        output_list.append(p.as_dict())


    stringify = request.GET.get("stringify", "true")
    if stringify.lower() == "false":
        return successful_response(output_list)
    else:
        return successful_response(json.dumps(output_list))

import json
from datetime import datetime
from django.db import models

class MeetingScheduleEntry(models.Model):
    meeting_year = models.IntegerField(null=True)
    meeting_month = models.CharField(null=True, max_length=20)
    meeting_name = models.CharField(null=True, max_length=100)
    meeting_start_date = models.DateTimeField(null=True)
    meeting_end_date = models.DateTimeField(null=True)
    statement = models.BooleanField(default=False)
    statement_url = models.CharField(null=True, max_length=256)
    projections = models.BooleanField(default=False)
    scrape_date = models.DateTimeField(null=True)
    estimated_release = models.DateTimeField(null=True)
    raw_entry = models.TextField(null=True)
    unscheduled = models.BooleanField(default=False)
    #Not as robust as possible but covers most use cases
    class Meta:
        unique_together = ("meeting_name", "scrape_date")

    def as_dict(self, columns = []):
        output_dict = {}
        _output_columns = ["id"]
        output_columns = ["id","meeting_name", "meeting_year", "meeting_month",
                        "unscheduled", "meeting_start_date",
                        "meeting_end_date", "scrape_date",
                        "statement", "statement_url", "projections",
                        "estimated_release"] if not len(columns) else ["id"] + columns
        for column in output_columns:
            output_dict[column] = str(getattr(self, column))
        return output_dict
    
    def from_original_dict(self, meeting_dict):        
        self.meeting_month = meeting_dict["month"]
        self.meeting_year = meeting_dict["year"]
        if "statement_url" in meeting_dict:
            self.statement_url = meeting_dict["statement_url"]
            self.statement=True
        self.meeting_name = ("FOMC_%s_%s" % (self.meeting_year, meeting_dict["month"])).upper()
        self.raw_entry = json.dumps(meeting_dict)
        self.scrape_date = datetime.strptime(meeting_dict["scrape_date"], "%Y-%m-%d %H:%M:%S.%f")
        timezone_offset = 5 # a kludge
        raw_days = meeting_dict["day"]
        if "unscheduled" in raw_days.lower():
            self.unscheduled=True
            self.meeting_name = self.meeting_name + "_ADHOC"
        month_num = datetime.strptime(meeting_dict["month"][:3], "%b").month
    
        days = raw_days.replace("*","").strip().split("-")
        if len(days) == 2:
            d1 = int(days[0])
            d2 = int(days[1])
         
            self.meeting_start_date = datetime(meeting_dict["year"], month_num, d1)
            self.meeting_end_date = datetime(meeting_dict["year"], month_num, d2)
            self.estimated_release = datetime(meeting_dict["year"], month_num, d2, 2 + timezone_offset)
        
        else:
            days = raw_days.replace("*","").strip().split(" ")
            if len(days):
                d1 = int(days[0])
                d2 = int(days[0])
                self.meeting_start_date = datetime(meeting_dict["year"], month_num, d1)
                self.meeting_end_date = datetime(meeting_dict["year"], month_num, d2)
                self.estimated_release = datetime(meeting_dict["year"], month_num, d2, 2 + timezone_offset)
    

class MeetingTableSummary(models.Model):
    title = models.CharField(max_length=100)
    table_as_json = models.TextField()
    scrape_date = models.DateTimeField()
    meeting = models.ForeignKey(MeetingScheduleEntry)

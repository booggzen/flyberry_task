Simple API for retrieving data from a Federal Reserve web site

Usage

The basic URL prefix for all queries is: <server>/fed/fomc
Calling this prefix without any other paramters will return the version info for the
service.

For example...

{"status": "ok", "version": "1.0", "data": "{\"last revised\": \"January 7, 2015\", \"source repository\": \"https://github.com/JimHagan/flyberry_task.git\", \"description\": \"Federal Reserve Information API\", \"author\": \"Jim Hagan\"}"}


RESPONSE FORMAT



If a query is successful, an "ok" response will be returned with HTTP response code 200:

{
 "status": "ok",
 "version": "version_num",
 "data": "<the returned query data>"
}


If a query is unsuccessful, an "error" response will be returned:

{
 "status": "error",
 "code": "short_code",
 "message": "A longer description of the error"
}                                                                                                                                                                                                               

For example, entering an unknown URL will return the fact that a 404 error occcured in our custom JSON format.

Example...

{"status": "error", "message": "404 Error", "code": "404"}                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  


Sample URLs


[Calendar Method]

http://localhost:8000/fed/fomc/calendar?transpose=false&stringify=false

http://localhost:8000/fed/fomc/calendar?transpose=false&stringify=false&columns=scrape_date,meeting_name,projections,statement

http://localhost:8000/fed/fomc/calendar?columns=meeting_name,projections,scrape_date

http://localhost:8000/fed/fomc/calendar?columns=meeting_name,projections,scrape_date&transpose=false&stringify=false

http://localhost:8000/fed/fomc/calendar?transpose=false&stringify=false&columns=scrape_date,meeting_name,statement_url

http://localhost:8000/fed/fomc/calendar?transpose=false&stringify=false&columns=projections,scrape_date,meeting_name,projections_html_url,projections_pdf_url

[Pace Of Firming Method]

http://localhost:8000/fed/fomc/pace_of_firming

http://localhost:8000/fed/fomc/pace_of_firming?stringify=False

http://localhost:8000/fed/fomc/pace_of_firming?stringify=True&meeting_name=FOMC_2014_MARCH,FOMC_2014_JUNE

http://localhost:8000/fed/fomc/pace_of_firming?begin_release=1401595200000.0  

http://localhost:8000/fed/fomc/pace_of_firming?begin_release=1401595200000.0&end_release=1404172800000.0

http://localhost:8000/fed/fomc/pace_of_firming?begin_scrape=1420848000000.0

http://localhost:8000/fed/fomc/pace_of_firming?end_scrape=1420848000000.0

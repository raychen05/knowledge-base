### How to find the query by MWS 


 
#### QA Environment 
 
 
- Document search - All Databases (clarivate.com) 
 - WOS MWS SERVICE Status Page (dev-wos.com) 
 
 
#### Steps: 
 
 
1. Go  Web of Knowledge application 
2. Execute a search from UI 
3. Right click to select  "Inspect" 
4. Go the "Application" tab 
5. Go "Local Storage" and click the url link 
6. Find the value of "wos_sid".    

wos_sid	"USW2EC4A98esKTGQJ4oNlrajRq1Au"

7.	Take the leading 10 characters.  e.g.   USW2EC4A98 
8. Go "WOS MWS Service" application 
9. Search by the leading 10 letters of sid 
10. It returns successfully, you will see the resule like Service: WOS MWS SERVICE 9.0.656 (2022-09-15T21:19:35Z) 
11. Click "Session Contents" 
12. Search by the sid value. USW2EC4A98esKTGQJ4oNlrajRq1Au 
13. It returns the search result and you can click link to the query (e.g.UA.SearchEngine.6 ) 
14. You will see the  query detail in the page ( API name, WQL, ES query etc.) 
 
 
